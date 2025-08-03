import requests
import logging
from typing import List, Dict, Optional
from config import YTS_SEARCH_URL, MIN_RATING

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YTSAPI:
    """Class to handle YTS API interactions"""
    
    def __init__(self):
        self.base_url = YTS_SEARCH_URL
    
    def search_movies(self, query: str) -> List[Dict]:
        """
        Search for movies using the YTS API
        
        Args:
            query (str): Movie title to search for
            
        Returns:
            List[Dict]: List of movies with rating >= MIN_RATING
        """
        try:
            params = {
                'query_term': query,
                'limit': 50,  # Get more results to filter from
                'sort_by': 'rating'  # Sort by rating
            }
            
            logger.info(f"Searching for movies with query: {query}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.error(f"YTS API error: {data.get('status_message', 'Unknown error')}")
                return []
            
            movies = data.get('data', {}).get('movies', [])
            
            # Filter movies with rating >= MIN_RATING
            filtered_movies = []
            for movie in movies:
                rating = movie.get('rating', 0)
                if rating >= MIN_RATING:
                    filtered_movies.append(movie)
            
            logger.info(f"Found {len(filtered_movies)} movies with rating >= {MIN_RATING}")
            return filtered_movies
            
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def get_torrents_for_movie(self, movie: Dict) -> List[Dict]:
        """
        Extract torrent information from a movie
        
        Args:
            movie (Dict): Movie data from YTS API
            
        Returns:
            List[Dict]: List of torrent information
        """
        torrents = movie.get('torrents', [])
        
        # Sort torrents by quality (prefer higher quality)
        quality_order = ['2160p', '1080p', '720p', '480p']
        
        def sort_key(torrent):
            quality = torrent.get('quality', '').lower()
            for i, q in enumerate(quality_order):
                if q in quality:
                    return i
            return len(quality_order)
        
        return sorted(torrents, key=sort_key)
    
    def format_movie_info(self, movie: Dict) -> str:
        """
        Format movie information for display
        
        Args:
            movie (Dict): Movie data from YTS API
            
        Returns:
            str: Formatted movie information
        """
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        
        info = f"🎬 **{title}** ({year})\n"
        info += f"⭐ Rating: {rating}/10\n"
        info += f"🎭 Genres: {genres}\n\n"
        
        torrents = self.get_torrents_for_movie(movie)
        
        if torrents:
            info += "📥 **Available Torrents:**\n"
            for i, torrent in enumerate(torrents[:5], 1):  # Limit to 5 torrents
                quality = torrent.get('quality', 'Unknown')
                size = torrent.get('size', 'Unknown')
                seeds = torrent.get('seeds', 0)
                peers = torrent.get('peers', 0)
                magnet_url = torrent.get('url', '')
                
                info += f"{i}. **{quality}** - {size}\n"
                info += f"   🌱 Seeds: {seeds} | 👥 Peers: {peers}\n"
                info += f"   🔗 [Download]({magnet_url})\n\n"
        else:
            info += "❌ No torrents available\n\n"
        
        return info 