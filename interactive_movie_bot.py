#!/usr/bin/env python3
"""
Interactive Movie Release Notifier Bot
Combines automatic notifications with manual search functionality
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
CHECK_INTERVAL = 3600  # Check every hour (in seconds)
MIN_RATING = 6.0
MIN_YEAR = 2025  # Only movies released in 2025 and future years
MAX_MOVIES_PER_CHECK = 100

# Filtered genres (movies with these genres will be excluded)
EXCLUDED_GENRES = {'Biography', 'Documentary', 'Drama', 'History', 'Sport', 'Music', 'Comedy'}

# Preferred genres for mainstream movies (higher priority)
PREFERRED_GENRES = {
    'Action', 'Adventure', 'Crime', 'Fantasy', 'Horror', 
    'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
}

# API endpoints
YTS_BASE_URL = "https://yts.mx/api/v2"
YTS_LATEST_URL = f"{YTS_BASE_URL}/list_movies.json"
OMDB_BASE_URL = "http://www.omdbapi.com/"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InteractiveMovieBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.known_movies = set()
        self.last_check_time = None
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🎬 **Movie Release Notifier Bot**

Welcome! I'll automatically notify you about new high-rated movies from YTS.mx.

**Commands:**
• `/search <movie title>` - Search for a specific movie
• `/status` - Check bot status and current filters
• `/help` - Show this help message

**Current Filters:**
• Year: 2025+ only
• Rating: 6.0+ IMDb rating
• Excluded genres: Biography, Documentary, Drama, History, Sport, Music, Comedy
• Check interval: Every hour

I'll send you notifications with movie posters, ratings, and download links!
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🎬 **Movie Bot Help**

**Commands:**
• `/search <movie title>` - Search for a specific movie on YTS
• `/status` - Show current bot status and filters
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`

**Automatic Notifications:**
I'll automatically check YTS every hour and notify you about new high-rated movies that meet your criteria.
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_message = f"""
📊 **Bot Status**

✅ **Bot is running**
⏰ **Last check:** {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else 'Never'}

**Current Filters:**
• 📅 **Year:** {MIN_YEAR}+ only
• ⭐ **Rating:** {MIN_RATING}+ IMDb rating
• 🚫 **Excluded:** {', '.join(EXCLUDED_GENRES)}
• ⏱️ **Check interval:** {CHECK_INTERVAL} seconds

**Known movies:** {len(self.known_movies)} tracked
        """
        await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a movie title to search for.\n\nExample: `/search 28 Years Later`", parse_mode=ParseMode.MARKDOWN)
            return
        
        query = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Searching for: **{query}**...", parse_mode=ParseMode.MARKDOWN)
        
        try:
            # Search for the movie
            movies = await self.search_movies(query)
            
            if not movies:
                await update.message.reply_text(f"❌ No movies found for: **{query}**", parse_mode=ParseMode.MARKDOWN)
                return
            
            # Send results
            for i, movie in enumerate(movies[:3], 1):  # Limit to 3 results
                notification = self.format_movie_notification(movie)
                
                # Get movie poster
                poster_url = movie.get('large_cover_image') or movie.get('medium_cover_image')
                
                if poster_url:
                    try:
                        await self.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=poster_url,
                            caption=notification,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        # Fallback to text-only
                        await update.message.reply_text(notification, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(notification, parse_mode=ParseMode.MARKDOWN)
                
                await asyncio.sleep(1)  # Small delay between messages
            
            if len(movies) > 3:
                await update.message.reply_text(f"📋 Showing first 3 results. Found {len(movies)} total movies for: **{query}**", parse_mode=ParseMode.MARKDOWN)
                
        except Exception as e:
            logger.error(f"Error in search: {e}")
            await update.message.reply_text(f"❌ Error searching for: **{query}**\n\nPlease try again later.", parse_mode=ParseMode.MARKDOWN)
    
    async def search_movies(self, query: str) -> List[Dict]:
        """Search for movies by title"""
        try:
            params = {
                'query_term': query,
                'limit': 20,
                'sort_by': 'date_added',
                'order_by': 'desc'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(YTS_LATEST_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        movies = data.get('data', {}).get('movies', [])
                        return movies
                    else:
                        logger.error(f"Search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return []
    
    async def get_latest_movies(self) -> List[Dict]:
        """Fetch latest movies from YTS API"""
        try:
            logger.info("Fetching latest movies from YTS...")
            
            params = {
                'limit': MAX_MOVIES_PER_CHECK,
                'sort_by': 'date_added',
                'order_by': 'desc'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(YTS_LATEST_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        movies = data.get('data', {}).get('movies', [])
                        logger.info(f"Found {len(movies)} latest movies")
                        
                        # Also search specifically for "28 Years Later" to ensure we don't miss it
                        search_params = {
                            'query_term': '28 Years Later',
                            'limit': 10,
                            'sort_by': 'date_added',
                            'order_by': 'desc'
                        }
                        
                        async with session.get(YTS_LATEST_URL, params=search_params) as search_response:
                            if search_response.status == 200:
                                search_data = await search_response.json()
                                search_movies = search_data.get('data', {}).get('movies', [])
                                
                                # Add any "28 Years Later" movies that aren't already in the list
                                for search_movie in search_movies:
                                    if not any(m.get('id') == search_movie.get('id') for m in movies):
                                        movies.append(search_movie)
                                        logger.info(f"Added '28 Years Later' movie: {search_movie.get('title', 'Unknown')}")
                        
                        return movies
                    else:
                        logger.error(f"Failed to fetch movies: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching movies: {e}")
            return []
    
    def calculate_movie_score(self, movie: Dict) -> float:
        """Calculate a score for movie prioritization based on various factors"""
        score = 0.0
        
        # Base score from IMDb rating
        rating = movie.get('rating', 0)
        score += rating * 3  # Increased importance of rating
        
        # HEAVY PRIORITY for latest YTS releases (date_added)
        date_added = movie.get('date_uploaded', '')
        if date_added:
            try:
                # Parse the date_added timestamp
                date_obj = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
                current_time = datetime.now(date_obj.tzinfo)
                hours_since_added = (current_time - date_obj).total_seconds() / 3600
                
                # Give massive bonus for very recent additions (last 24 hours)
                if hours_since_added <= 24:
                    score += 100  # HUGE bonus for brand new releases
                elif hours_since_added <= 72:  # Last 3 days
                    score += 60
                elif hours_since_added <= 168:  # Last week
                    score += 40
                elif hours_since_added <= 720:  # Last month
                    score += 20
                else:
                    score += 10  # Base score for older additions
                    
            except:
                # If date parsing fails, give a moderate score
                score += 15
        
        # Year bonus (newer movies get higher scores)
        year = movie.get('year', 0)
        current_year = datetime.now().year
        if year >= current_year - 1:  # Very recent movies
            score += 10
        elif year >= current_year - 2:  # Recent movies
            score += 5
        elif year >= current_year - 3:  # Moderately recent
            score += 2
        
        # Genre scoring
        genres = set(movie.get('genres', []))
        
        # Bonus for preferred genres
        preferred_count = len(genres.intersection(PREFERRED_GENRES))
        score += preferred_count * 3
        
        # Bonus for having multiple preferred genres (mainstream appeal)
        if preferred_count >= 2:
            score += 5
        
        # HIGH PRIORITY genres (movies that get media attention)
        high_priority_genres = {'Action', 'Adventure', 'Thriller', 'Sci-Fi', 'Horror'}
        high_priority_count = len(genres.intersection(high_priority_genres))
        score += high_priority_count * 5  # Big bonus for high-priority genres
        
        # FAMOUS MOVIE DETECTION (sequels, remakes, famous titles)
        title = movie.get('title', '').lower()
        famous_patterns = [
            '28 years later', 'happy gilmore 2', 'sitaare zameen par',
            'deadpool', 'batman', 'spider-man', 'avengers', 'star wars',
            'mission impossible', 'fast and furious', 'james bond'
        ]
        
        for pattern in famous_patterns:
            if pattern in title:
                score += 25  # Big bonus for famous movies
                break
        
        # SEQUEL/REMAKE BONUS
        if any(word in title for word in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']):
            score += 15  # Bonus for sequels
        
        # Torrent availability bonus
        torrents = movie.get('torrents', [])
        if torrents:
            # Bonus for having multiple qualities
            score += min(len(torrents), 3) * 2
            
            # Bonus for high seed counts (popularity indicator)
            total_seeds = sum(torrent.get('seeds', 0) for torrent in torrents)
            if total_seeds > 100:
                score += 5
            elif total_seeds > 50:
                score += 3
        
        return score
    
    def filter_high_rated_movies(self, movies: List[Dict]) -> List[Dict]:
        """Filter movies with IMDb rating >= MIN_RATING, year >= MIN_YEAR, and exclude unwanted genres"""
        filtered_movies = []
        
        for movie in movies:
            rating = movie.get('rating', 0)
            year = movie.get('year', 0)
            genres = set(movie.get('genres', []))
            
            # Check basic requirements
            if rating < MIN_RATING or year < MIN_YEAR:
                continue
            
            # Exclude movies with unwanted genres
            if genres.intersection(EXCLUDED_GENRES):
                continue
            
            # Calculate score for prioritization
            movie['_score'] = self.calculate_movie_score(movie)
            filtered_movies.append(movie)
        
        # Sort by score (highest first) and then by rating
        filtered_movies.sort(key=lambda x: (x['_score'], x.get('rating', 0)), reverse=True)
        
        logger.info(f"Found {len(filtered_movies)} movies after filtering (rating >= {MIN_RATING}, year >= {MIN_YEAR}, excluding {', '.join(EXCLUDED_GENRES)})")
        return filtered_movies
    
    def get_new_movies(self, movies: List[Dict]) -> List[Dict]:
        """Identify movies that haven't been notified about yet"""
        new_movies = []
        
        for movie in movies:
            movie_id = movie.get('id')
            if movie_id and movie_id not in self.known_movies:
                new_movies.append(movie)
                self.known_movies.add(movie_id)
        
        logger.info(f"Found {len(new_movies)} new movies to notify about")
        return new_movies
    
    def get_omdb_rating(self, title: str, year: str) -> Optional[Dict]:
        """Get additional movie data from OMDB API"""
        if not OMDB_API_KEY:
            return None
            
        try:
            url = f"{OMDB_BASE_URL}?t={title}&y={year}&apikey={OMDB_API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    'plot': data.get('Plot', ''),
                    'runtime': data.get('Runtime', ''),
                    'director': data.get('Director', ''),
                    'actors': data.get('Actors', ''),
                    'metascore': data.get('Metascore', ''),
                    'boxoffice': data.get('BoxOffice', '')
                }
        except Exception as e:
            logger.error(f"Error fetching OMDB data: {e}")
        
        return None
    
    def format_movie_notification(self, movie: Dict) -> str:
        """Format movie information for notification"""
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        date_added = movie.get('date_uploaded', 'Unknown')
        score = movie.get('_score', 0)
        
        # Format date and calculate recency
        try:
            if date_added != 'Unknown':
                date_obj = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%B %d, %Y')
                
                # Calculate how recent this addition is
                current_time = datetime.now(date_obj.tzinfo)
                hours_since_added = (current_time - date_obj).total_seconds() / 3600
                
                if hours_since_added <= 24:
                    recency_text = f"🆕 NEW YTS ADDITION! (Last 24h)"
                elif hours_since_added <= 72:
                    recency_text = f"🆕 NEW YTS ADDITION! (Last 3 days)"
                elif hours_since_added <= 168:
                    recency_text = f"🆕 NEW YTS ADDITION! (Last week)"
                else:
                    recency_text = f"📅 Added: {formatted_date}"
            else:
                recency_text = "📅 Added: Unknown"
        except:
            recency_text = f"📅 Added: {date_added}"
        
        # Determine if it's a very recent release
        current_year = datetime.now().year
        is_recent = year >= current_year - 1
        
        # Check if it's a famous movie
        title_lower = title.lower()
        famous_patterns = [
            '28 years later', 'happy gilmore 2', 'sitaare zameen par',
            'deadpool', 'batman', 'spider-man', 'avengers', 'star wars'
        ]
        is_famous = any(pattern in title_lower for pattern in famous_patterns)
        
        # Start building notification
        if is_famous:
            notification = f"🎬 **🔥 FAMOUS MAINSTREAM RELEASE!**\n\n"
        elif is_recent:
            notification = f"🎬 **🔥 HOT NEW RELEASE!**\n\n"
        else:
            notification = f"🎬 **NEW HIGH-RATED MOVIE!**\n\n"
        
        notification += f"📽️ **{title}** ({year})\n"
        notification += f"⭐ **IMDb Rating:** {rating}/10\n"
        notification += f"🎭 **Genres:** {genres}\n"
        notification += f"{recency_text}\n"
        
        if is_recent:
            notification += f"🚀 **Recent Release** (2025+)\n"
        
        if is_famous:
            notification += f"🌟 **FAMOUS MOVIE** - Media talked about!\n"
        
        # Get OMDB data for enhanced information
        omdb_data = self.get_omdb_rating(title, str(year))
        if omdb_data:
            # Add Rotten Tomatoes rating if available
            rt_rating = omdb_data.get('metascore', '')
            if rt_rating and rt_rating != 'N/A':
                try:
                    rt_score = int(rt_rating)
                    if rt_score >= 80:
                        notification += f"🍅 **Rotten Tomatoes:** {rt_score}%\n"
                    elif rt_score >= 60:
                        notification += f"🍅 **Rotten Tomatoes:** {rt_score}%\n"
                    else:
                        notification += f"🍅 **Rotten Tomatoes:** {rt_score}%\n"
                except:
                    pass
            
            # Add Metacritic rating
            mc_rating = omdb_data.get('metascore', '')
            if mc_rating and mc_rating != 'N/A':
                notification += f"📊 **Metacritic:** {mc_rating}/100\n"
            
            # Add runtime if available
            runtime = omdb_data.get('runtime', '')
            if runtime:
                notification += f"⏱️ **Runtime:** {runtime}\n"
            
            # Add plot if available (short version)
            plot = omdb_data.get('plot', '')
            if plot and len(plot) < 150:  # Only add short plots
                notification += f"📝 **Plot:** {plot}\n"
        
        # Add torrent information
        notification += "\n📥 **Available Qualities:**\n"
        torrents = movie.get('torrents', [])
        
        if torrents:
            for i, torrent in enumerate(torrents[:3], 1):  # Show first 3 qualities
                quality = torrent.get('quality', 'Unknown')
                size = torrent.get('size', 'Unknown')
                seeds = torrent.get('seeds', 0)
                
                seed_emoji = "🌱" if seeds > 0 else "❌"
                notification += f"{i}. **{quality}** - {size} ({seed_emoji} {seeds} seeds)\n"
        else:
            notification += "No torrents available yet\n"
        
        notification += f"\n🔗 **YTS Link:** https://yts.mx/movies/{movie.get('slug', '')}"
        notification += f"\n\n🖼️ **Movie poster included above**"
        
        return notification
    
    async def send_notification(self, movie: Dict):
        """Send notification about a new movie with image"""
        try:
            notification = self.format_movie_notification(movie)
            
            # Get movie poster image URL
            poster_url = movie.get('large_cover_image') or movie.get('medium_cover_image')
            
            if poster_url:
                # Send photo with caption
                await self.bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=poster_url,
                    caption=notification,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # Fallback to text-only message if no image
                await self.bot.send_message(
                    chat_id=CHAT_ID,
                    text=notification,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            
            logger.info(f"Sent notification with image for: {movie.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            # Fallback to text-only message if image sending fails
            try:
                notification = self.format_movie_notification(movie)
                await self.bot.send_message(
                    chat_id=CHAT_ID,
                    text=notification,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                logger.info(f"Sent text-only notification for: {movie.get('title', 'Unknown')}")
            except Exception as e2:
                logger.error(f"Error sending fallback notification: {e2}")
    
    async def check_and_notify(self):
        """Main function to check for new movies and send notifications"""
        try:
            # Get latest movies
            movies = await self.get_latest_movies()
            
            if not movies:
                logger.warning("No movies found")
                return
            
            # Filter high-rated movies
            high_rated_movies = self.filter_high_rated_movies(movies)
            
            if not high_rated_movies:
                logger.info("No high-rated movies found")
                return
            
            # Get new movies
            new_movies = self.get_new_movies(high_rated_movies)
            
            if not new_movies:
                logger.info("No new movies to notify about")
                return
            
            # Send notifications
            for movie in new_movies:
                await self.send_notification(movie)
                await asyncio.sleep(2)  # Small delay between notifications
            
            self.last_check_time = datetime.now()
            logger.info(f"Completed check. Notified about {len(new_movies)} new movies.")
            
        except Exception as e:
            logger.error(f"Error in check_and_notify: {e}")
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring with periodic checks"""
        logger.info("Starting Interactive Movie Release Notifier Bot...")
        logger.info(f"Checking for movies with IMDb rating >= {MIN_RATING} and year >= {MIN_YEAR}")
        logger.info(f"Excluding genres: {', '.join(EXCLUDED_GENRES)}")
        logger.info(f"Prioritizing mainstream genres: {', '.join(PREFERRED_GENRES)}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
        
        if OMDB_API_KEY:
            logger.info("OMDB API enabled - will include Rotten Tomatoes ratings")
        else:
            logger.info("OMDB API not configured - ratings from YTS only")
        
        while True:
            try:
                await self.check_and_notify()
                
                # Wait for next check
                logger.info(f"Waiting {CHECK_INTERVAL} seconds until next check...")
                await asyncio.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def setup_handlers(self):
        """Setup command handlers"""
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        
        logger.info("Command handlers setup complete")
    
    async def run_bot(self):
        """Run the interactive bot"""
        await self.setup_handlers()
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Interactive bot started successfully!")
        
        # Start the monitoring task
        monitoring_task = asyncio.create_task(self.run_continuous_monitoring())
        
        try:
            # Keep the bot running
            await self.application.updater.idle()
        finally:
            monitoring_task.cancel()
            await self.application.stop()
            await self.application.shutdown()

async def main():
    """Main function"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    if not CHAT_ID:
        logger.error("CHAT_ID not found in environment variables!")
        logger.info("Please add your Telegram chat ID to the .env file")
        return
    
    bot = InteractiveMovieBot()
    await bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main()) 