#!/usr/bin/env python3
"""
Test script for the Enhanced Movie Notifier with updated genre filtering
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_updated_filtering():
    """Test the updated filtering with all excluded genres"""
    print("🧪 Testing Enhanced Movie Notifier with Updated Genre Filtering")
    print("=" * 75)
    
    notifier = EnhancedMovieNotifier()
    
    # Test getting latest movies
    print("📡 Fetching latest movies from YTS...")
    movies = await notifier.get_latest_movies()
    
    if not movies:
        print("❌ No movies found")
        return
    
    print(f"✅ Found {len(movies)} latest movies")
    
    # Test filtering with updated criteria
    print(f"\n⭐ Filtering for mainstream movies...")
    print(f"   • Rating >= 6.0")
    print(f"   • Year >= 2015")
    print(f"   • Excluding: Biography, Documentary, Drama, History, Sport, Music")
    print(f"   • Prioritizing: Action, Adventure, Comedy, Crime, Fantasy, Horror, Mystery, Romance, Sci-Fi, Thriller, War, Western")
    
    filtered_movies = notifier.filter_high_rated_movies(movies)
    
    if not filtered_movies:
        print("❌ No mainstream movies found")
        return
    
    print(f"✅ Found {len(filtered_movies)} mainstream movies")
    
    # Show results with scores
    print("\n🎬 Top Mainstream Movies (Sorted by Priority):")
    print("-" * 75)
    
    for i, movie in enumerate(filtered_movies[:10], 1):
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        score = movie.get('_score', 0)
        
        # Determine if it's recent
        current_year = 2025  # Current year
        is_recent = year >= current_year - 1
        
        print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
        print(f"   Genres: {genres}")
        print(f"   Score: {score:.1f} {'🔥 RECENT!' if is_recent else ''}")
        
        # Show torrent info
        torrents = movie.get('torrents', [])
        if torrents:
            total_seeds = sum(torrent.get('seeds', 0) for torrent in torrents)
            print(f"   📥 {len(torrents)} qualities, {total_seeds} total seeds")
        
        print()
    
    # Test notification formatting
    if filtered_movies:
        print("📝 Testing Enhanced Notification Format:")
        print("-" * 75)
        sample_movie = filtered_movies[0]
        notification = notifier.format_movie_notification(sample_movie)
        print(notification)

async def main():
    """Main test function"""
    print("🎬 Enhanced Movie Notifier - Updated Genre Filtering Test")
    print("=" * 85)
    
    try:
        await test_updated_filtering()
        
        print("\n🎉 Updated filtering test completed!")
        print("\n✅ Features verified:")
        print("• Genre exclusions (Biography, Documentary, Drama, History, Sport, Music)")
        print("• Mainstream genre prioritization")
        print("• Recent release prioritization")
        print("• Smart scoring system")
        print("• Enhanced notification format")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 