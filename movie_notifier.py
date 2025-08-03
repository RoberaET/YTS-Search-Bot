#!/usr/bin/env python3
"""
Movie Release Notifier Bot
Automatically checks YTS.mx for newly released movies with IMDb ratings above 6
and sends notifications to the user.
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

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # Your Telegram chat ID
CHECK_INTERVAL = 3600  # Check every hour (in seconds)
MIN_RATING = 6.0
MIN_YEAR = 2025  # Only movies released in 2025 and future years
MAX_MOVIES_PER_CHECK = 50  # Increased to get more movies for better filtering

# Filtered genres (movies with these genres will be excluded)
EXCLUDED_GENRES = {'Biography', 'Documentary', 'Drama', 'History', 'Sport', 'Music'}

# Preferred genres for mainstream movies (higher priority)
PREFERRED_GENRES = {
    'Action', 'Adventure', 'Comedy', 'Crime', 'Fantasy', 'Horror', 
    'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
}

# YTS API endpoints
YTS_BASE_URL = "https://yts.mx/api/v2"
YTS_LATEST_URL = f"{YTS_BASE_URL}/list_movies.json"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MovieNotifier:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.known_movies = set()  # Track movies we've already notified about
        self.last_check_time = None
        
    async def get_latest_movies(self) -> List[Dict]:
        """Get latest movies from YTS API"""
        try:
            params = {
                'limit': MAX_MOVIES_PER_CHECK,
                'sort_by': 'date_added',
                'order_by': 'desc'
            }
            
            logger.info("Fetching latest movies from YTS...")
            response = requests.get(YTS_LATEST_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.error(f"YTS API error: {data.get('status_message', 'Unknown error')}")
                return []
            
            movies = data.get('data', {}).get('movies', [])
            logger.info(f"Found {len(movies)} latest movies")
            return movies
            
        except Exception as e:
            logger.error(f"Error fetching latest movies: {e}")
            return []
    
    def calculate_movie_score(self, movie: Dict) -> float:
        """Calculate a score for movie prioritization based on various factors"""
        score = 0.0
        
        # Base score from IMDb rating
        rating = movie.get('rating', 0)
        score += rating * 2  # Rating is very important
        
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
        """Get movies we haven't notified about yet"""
        new_movies = []
        
        for movie in movies:
            movie_id = movie.get('id')
            if movie_id and movie_id not in self.known_movies:
                new_movies.append(movie)
                self.known_movies.add(movie_id)
        
        logger.info(f"Found {len(new_movies)} new movies to notify about")
        return new_movies
    
    def get_tomatometer_rating(self, movie: Dict) -> Optional[str]:
        """Get Rotten Tomatoes rating if available"""
        # YTS API doesn't directly provide Rotten Tomatoes ratings
        # We could integrate with another API like OMDB for this
        # For now, we'll return None
        return None
    
    def format_movie_notification(self, movie: Dict) -> str:
        """Format movie information for notification"""
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        date_added = movie.get('date_uploaded', 'Unknown')
        
        # Format date
        try:
            if date_added != 'Unknown':
                date_obj = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%B %d, %Y')
            else:
                formatted_date = 'Unknown'
        except:
            formatted_date = date_added
        
        # Determine if it's a very recent release
        current_year = datetime.now().year
        is_recent = year >= current_year - 1
        
        notification = f"🎬 **{'🔥 HOT NEW RELEASE!' if is_recent else 'NEW HIGH-RATED MOVIE!'}**\n\n"
        notification += f"📽️ **{title}** ({year})\n"
        notification += f"⭐ **IMDb Rating:** {rating}/10\n"
        notification += f"🎭 **Genres:** {genres}\n"
        notification += f"📅 **Added:** {formatted_date}\n"
        
        if is_recent:
            notification += f"🚀 **Recent Release** (within last year)\n"
        
        notification += "\n"
        
        # Add torrent information
        torrents = movie.get('torrents', [])
        if torrents:
            notification += "📥 **Available Qualities:**\n"
            for i, torrent in enumerate(torrents[:3], 1):  # Show top 3 qualities
                quality = torrent.get('quality', 'Unknown')
                size = torrent.get('size', 'Unknown')
                seeds = torrent.get('seeds', 0)
                notification += f"{i}. **{quality}** - {size} (🌱 {seeds} seeds)\n"
        
        notification += f"\n🔗 **YTS Link:** https://yts.mx/movies/{movie.get('slug', '')}"
        
        return notification
    
    async def send_notification(self, movie: Dict):
        """Send notification about a new movie"""
        try:
            notification = self.format_movie_notification(movie)
            
            await self.bot.send_message(
                chat_id=CHAT_ID,
                text=notification,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
            logger.info(f"Sent notification for: {movie.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
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
        logger.info("Starting Movie Release Notifier Bot...")
        logger.info(f"Checking for movies with IMDb rating >= {MIN_RATING} and year >= {MIN_YEAR}")
        logger.info(f"Excluding genres: {', '.join(EXCLUDED_GENRES)}")
        logger.info(f"Prioritizing mainstream genres: {', '.join(PREFERRED_GENRES)}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
        
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
    
    notifier = MovieNotifier()
    await notifier.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 