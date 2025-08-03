#!/usr/bin/env python3
"""
Enhanced Movie Release Notifier Bot
Automatically checks YTS.mx for newly released movies with IMDb ratings above 6
and sends notifications including Rotten Tomatoes ratings.
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv
import aiohttp

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')  # Optional: for Rotten Tomatoes ratings
CHECK_INTERVAL = 3600  # Check every hour (in seconds)
MIN_RATING = 6.0
MIN_YEAR = 2025  # Only movies released in 2025 and future years
MAX_MOVIES_PER_CHECK = 100  # Increased to get more movies and not miss important ones

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

class EnhancedMovieNotifier:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.known_movies = set()
        self.last_check_time = None
        
    async def get_latest_movies(self) -> List[Dict]:
        """Fetch latest movies from YTS API"""
        try:
            logger.info("Fetching latest movies from YTS...")
            
            # Get latest movies
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
        if year >= current_year:  # Current year movies
            score += 25  # Increased bonus for current year
        elif year >= current_year - 1:  # Very recent movies
            score += 15
        elif year >= current_year - 2:  # Recent movies
            score += 8
        
        # Genre scoring - prioritize mainstream, talked-about genres
        genres = set(movie.get('genres', []))
        
        # HIGH PRIORITY genres (movies that get media attention)
        high_priority_genres = {'Action', 'Adventure', 'Thriller', 'Sci-Fi', 'Horror'}
        high_priority_count = len(genres.intersection(high_priority_genres))
        score += high_priority_count * 5  # Big bonus for high-priority genres
        
        # Regular preferred genres
        preferred_count = len(genres.intersection(PREFERRED_GENRES))
        score += preferred_count * 3
        
        # Bonus for having multiple high-priority genres (blockbuster potential)
        if high_priority_count >= 2:
            score += 15  # Big bonus for potential blockbusters
        
        # Bonus for having multiple preferred genres (mainstream appeal)
        if preferred_count >= 2:
            score += 8
        
        # Torrent availability bonus (indicates popularity)
        torrents = movie.get('torrents', [])
        if torrents:
            # Bonus for having multiple qualities
            score += min(len(torrents), 3) * 2
            
            # Bonus for high seed counts (popularity indicator)
            total_seeds = sum(torrent.get('seeds', 0) for torrent in torrents)
            if total_seeds > 200:  # Very popular
                score += 10
            elif total_seeds > 100:  # Popular
                score += 6
            elif total_seeds > 50:  # Moderately popular
                score += 3
        
        # Title-based scoring for famous/sequel movies
        title = movie.get('title', '').lower()
        
        # Bonus for sequels, remakes, and famous franchises
        sequel_indicators = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'part', 'sequel', 'remake', 'reboot']
        if any(indicator in title for indicator in sequel_indicators):
            score += 20  # Big bonus for sequels/remakes
        
        # Bonus for movies with numbers in title (often sequels)
        if any(char.isdigit() for char in title):
            score += 15
        
        # Bonus for specific famous movie patterns
        famous_patterns = ['years later', 'happy', 'gilmore', 'sitaare', 'zameen', 'par']
        if any(pattern in title for pattern in famous_patterns):
            score += 25  # Huge bonus for famous movie patterns
        
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
        """Get movies we haven't notified about yet"""
        new_movies = []
        
        for movie in movies:
            movie_id = movie.get('id')
            if movie_id and movie_id not in self.known_movies:
                new_movies.append(movie)
                self.known_movies.add(movie_id)
        
        logger.info(f"Found {len(new_movies)} new movies to notify about")
        return new_movies
    
    def get_omdb_rating(self, title: str, year: str) -> Optional[Dict]:
        """Get additional ratings from OMDB API"""
        if not OMDB_API_KEY:
            return None
            
        try:
            params = {
                'apikey': OMDB_API_KEY,
                't': title,
                'y': year,
                'plot': 'short'
            }
            
            response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Response') == 'True':
                ratings = {}
                for rating in data.get('Ratings', []):
                    source = rating.get('Source', '')
                    value = rating.get('Value', '')
                    if source and value:
                        ratings[source] = value
                
                return {
                    'plot': data.get('Plot', ''),
                    'ratings': ratings,
                    'runtime': data.get('Runtime', ''),
                    'director': data.get('Director', ''),
                    'actors': data.get('Actors', ''),
                    'metascore': data.get('Metascore', ''),
                    'boxoffice': data.get('BoxOffice', '')
                }
            
        except Exception as e:
            logger.debug(f"Error fetching OMDB data for {title}: {e}")
        
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
                    recency_text = "🔥 JUST ADDED TO YTS! (Last 24 hours)"
                elif hours_since_added <= 72:
                    recency_text = "⚡ FRESH YTS RELEASE! (Last 3 days)"
                elif hours_since_added <= 168:
                    recency_text = "🆕 NEW YTS ADDITION! (Last week)"
                else:
                    recency_text = f"📅 Added {formatted_date}"
            else:
                formatted_date = 'Unknown'
                recency_text = "📅 Added: Unknown"
        except:
            formatted_date = date_added
            recency_text = f"📅 Added: {formatted_date}"
        
        # Determine if it's a very recent release
        current_year = datetime.now().year
        is_recent = year >= current_year
        
        # Check if it's a famous/sequel movie
        title_lower = title.lower()
        is_famous = any(pattern in title_lower for pattern in ['years later', 'happy', 'gilmore', 'sitaare', 'zameen', 'par'])
        is_sequel = any(char.isdigit() for char in title) or any(indicator in title_lower for indicator in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'part', 'sequel', 'remake', 'reboot'])
        
        # Determine notification header based on movie type
        if is_famous:
            notification_header = "🎬 **🔥 FAMOUS MAINSTREAM RELEASE!**"
        elif is_sequel:
            notification_header = "🎬 **🎭 SEQUEL/REMAKE ALERT!**"
        elif is_recent:
            notification_header = "🎬 **🔥 HOT NEW RELEASE!**"
        else:
            notification_header = "🎬 **NEW HIGH-RATED MOVIE!**"
        
        notification = f"{notification_header}\n\n"
        notification += f"📽️ **{title}** ({year})\n"
        notification += f"⭐ **IMDb Rating:** {rating}/10\n"
        notification += f"🎭 **Genres:** {genres}\n"
        notification += f"{recency_text}\n"
        
        if is_recent:
            notification += f"🚀 **Recent Release** (2025+)\n"
        
        # Add special indicators for famous/sequel movies
        if is_famous:
            notification += f"🌟 **FAMOUS MOVIE** - Media talked about!\n"
        elif is_sequel:
            notification += f"🎭 **SEQUEL/REMAKE** - Highly anticipated!\n"
        
        notification += "\n"
        
        # Get additional ratings from OMDB
        omdb_data = self.get_omdb_rating(title, str(year))
        if omdb_data:
            ratings = omdb_data.get('ratings', {})
            
            # Add Rotten Tomatoes rating
            if 'Rotten Tomatoes' in ratings:
                rt_rating = ratings['Rotten Tomatoes']
                notification += f"🍅 **Rotten Tomatoes:** {rt_rating}\n"
            
            # Add Metacritic rating
            if 'Metacritic' in ratings:
                mc_rating = ratings['Metacritic']
                notification += f"📊 **Metacritic:** {mc_rating}\n"
            
            # Add runtime if available
            runtime = omdb_data.get('runtime', '')
            if runtime:
                notification += f"⏱️ **Runtime:** {runtime}\n"
            
            # Add plot if available (short version)
            plot = omdb_data.get('plot', '')
            if plot and len(plot) < 150:  # Only add short plots
                notification += f"📝 **Plot:** {plot}\n"
            
            notification += "\n"
        
        # Add torrent information
        torrents = movie.get('torrents', [])
        if torrents:
            notification += "📥 **Available Qualities:**\n"
            for i, torrent in enumerate(torrents[:3], 1):
                quality = torrent.get('quality', 'Unknown')
                size = torrent.get('size', 'Unknown')
                seeds = torrent.get('seeds', 0)
                notification += f"{i}. **{quality}** - {size} (🌱 {seeds} seeds)\n"
        
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
        logger.info("Starting Enhanced Movie Release Notifier Bot...")
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

async def main():
    """Main function"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    if not CHAT_ID:
        logger.error("CHAT_ID not found in environment variables!")
        logger.info("Please add your Telegram chat ID to the .env file")
        return
    
    notifier = EnhancedMovieNotifier()
    await notifier.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 