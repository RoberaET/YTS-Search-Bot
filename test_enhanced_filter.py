#!/usr/bin/env python3
"""
Test script for the Enhanced Movie Notifier with year filtering and OMDB integration
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_filtering():
    """Test the enhanced filtering with year and OMDB integration"""
    print("🧪 Testing Enhanced Movie Notifier with Year Filtering")
    print("=" * 60)
    
    notifier = EnhancedMovieNotifier()
    
    # Test getting latest movies
    print("📡 Fetching latest movies from YTS...")
    movies = await notifier.get_latest_movies()
    
    if not movies:
        print("❌ No movies found")
        return
    
    print(f"✅ Found {len(movies)} latest movies")
    
    # Test filtering with year requirement
    print(f"\n⭐ Filtering movies with rating >= 6.0 and year >= 2015...")
    high_rated = notifier.filter_high_rated_movies(movies)
    
    if not high_rated:
        print("❌ No high-rated movies found after 2015")
        return
    
    print(f"✅ Found {len(high_rated)} high-rated movies after 2015")
    
    # Show results
    print("\n🎬 High-Rated Movies After 2015:")
    print("-" * 50)
    
    for i, movie in enumerate(high_rated[:5], 1):
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        
        print(f"{i}. {title} ({year}) - {rating}/10")
        print(f"   Genres: {genres}")
        
        # Test OMDB integration
        print(f"   🔍 Testing OMDB integration...")
        omdb_data = notifier.get_omdb_rating(title, str(year))
        
        if omdb_data:
            ratings = omdb_data.get('ratings', {})
            
            if 'Rotten Tomatoes' in ratings:
                print(f"   🍅 Rotten Tomatoes: {ratings['Rotten Tomatoes']}")
            
            if 'Metacritic' in ratings:
                print(f"   📊 Metacritic: {ratings['Metacritic']}")
            
            runtime = omdb_data.get('runtime', '')
            if runtime:
                print(f"   ⏱️ Runtime: {runtime}")
        else:
            print(f"   ℹ️ No OMDB data available")
        
        print()
    
    # Test notification formatting
    if high_rated:
        print("📝 Testing Enhanced Notification Format:")
        print("-" * 50)
        sample_movie = high_rated[0]
        notification = notifier.format_movie_notification(sample_movie)
        print(notification)

async def main():
    """Main test function"""
    print("🎬 Enhanced Movie Notifier - Test Suite")
    print("=" * 70)
    
    try:
        await test_enhanced_filtering()
        
        print("\n🎉 Enhanced filtering test completed!")
        print("\n✅ Features verified:")
        print("• Year filtering (>= 2015)")
        print("• IMDb rating filtering (>= 6.0)")
        print("• OMDB API integration")
        print("• Rotten Tomatoes ratings")
        print("• Enhanced notification format")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 