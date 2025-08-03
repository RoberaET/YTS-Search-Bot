#!/usr/bin/env python3
"""
Test script for the Movie Release Notifier
Tests the functionality without running the continuous monitoring.
"""

import asyncio
import logging
from movie_notifier import MovieNotifier
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_notifier():
    """Test the basic movie notifier"""
    print("🧪 Testing Basic Movie Notifier")
    print("=" * 50)
    
    notifier = MovieNotifier()
    
    # Test getting latest movies
    print("📡 Fetching latest movies from YTS...")
    movies = await notifier.get_latest_movies()
    
    if not movies:
        print("❌ No movies found")
        return
    
    print(f"✅ Found {len(movies)} latest movies")
    
    # Test filtering high-rated movies
    print("\n⭐ Filtering movies with rating >= 6.0...")
    high_rated = notifier.filter_high_rated_movies(movies)
    
    if not high_rated:
        print("❌ No high-rated movies found")
        return
    
    print(f"✅ Found {len(high_rated)} high-rated movies")
    
    # Show top 3 results
    print("\n🎬 Top 3 High-Rated Movies:")
    print("-" * 40)
    
    for i, movie in enumerate(high_rated[:3], 1):
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        
        print(f"{i}. {title} ({year}) - {rating}/10")
        print(f"   Genres: {genres}")
        
        # Show torrent qualities
        torrents = movie.get('torrents', [])
        if torrents:
            qualities = [t.get('quality', 'Unknown') for t in torrents[:3]]
            print(f"   Qualities: {', '.join(qualities)}")
        print()

async def test_enhanced_notifier():
    """Test the enhanced movie notifier with OMDB integration"""
    print("\n🧪 Testing Enhanced Movie Notifier")
    print("=" * 50)
    
    notifier = EnhancedMovieNotifier()
    
    # Test getting latest movies
    print("📡 Fetching latest movies from YTS...")
    movies = await notifier.get_latest_movies()
    
    if not movies:
        print("❌ No movies found")
        return
    
    print(f"✅ Found {len(movies)} latest movies")
    
    # Test filtering high-rated movies
    print("\n⭐ Filtering movies with rating >= 6.0...")
    high_rated = notifier.filter_high_rated_movies(movies)
    
    if not high_rated:
        print("❌ No high-rated movies found")
        return
    
    print(f"✅ Found {len(high_rated)} high-rated movies")
    
    # Test OMDB integration with first movie
    if high_rated:
        first_movie = high_rated[0]
        title = first_movie.get('title', 'Unknown')
        year = first_movie.get('year', 'Unknown')
        
        print(f"\n🔍 Testing OMDB integration for: {title} ({year})")
        omdb_data = notifier.get_omdb_rating(title, str(year))
        
        if omdb_data:
            print("✅ OMDB data retrieved successfully!")
            ratings = omdb_data.get('ratings', {})
            
            if 'Rotten Tomatoes' in ratings:
                print(f"🍅 Rotten Tomatoes: {ratings['Rotten Tomatoes']}")
            
            if 'Metacritic' in ratings:
                print(f"📊 Metacritic: {ratings['Metacritic']}")
            
            plot = omdb_data.get('plot', '')
            if plot:
                print(f"📝 Plot: {plot[:100]}...")
        else:
            print("ℹ️  No OMDB data available (API key not configured or movie not found)")

async def test_notification_formatting():
    """Test notification formatting"""
    print("\n🧪 Testing Notification Formatting")
    print("=" * 50)
    
    notifier = MovieNotifier()
    
    # Get a sample movie
    movies = await notifier.get_latest_movies()
    if not movies:
        print("❌ No movies found for testing")
        return
    
    high_rated = notifier.filter_high_rated_movies(movies)
    if not high_rated:
        print("❌ No high-rated movies found for testing")
        return
    
    sample_movie = high_rated[0]
    notification = notifier.format_movie_notification(sample_movie)
    
    print("📝 Sample Notification:")
    print("-" * 40)
    print(notification)

async def main():
    """Main test function"""
    print("🎬 Movie Release Notifier - Test Suite")
    print("=" * 60)
    
    try:
        # Test basic notifier
        await test_basic_notifier()
        
        # Test enhanced notifier
        await test_enhanced_notifier()
        
        # Test notification formatting
        await test_notification_formatting()
        
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python get_chat_id.py' to get your chat ID")
        print("2. Add your chat ID to the .env file")
        print("3. Run 'python movie_notifier.py' to start monitoring")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 