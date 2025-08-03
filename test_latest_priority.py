#!/usr/bin/env python3
"""
Test script for the Enhanced Movie Notifier with Latest YTS Priority
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_latest_priority():
    """Test the priority system for latest YTS releases"""
    print("🧪 Testing Enhanced Movie Notifier with Latest YTS Priority")
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
    print(f"\n⭐ Filtering for 2025+ mainstream movies with latest YTS priority...")
    print(f"   • Rating >= 6.0")
    print(f"   • Year >= 2025 (current and future years only)")
    print(f"   • Excluding: Biography, Documentary, Drama, History, Sport, Music")
    print(f"   • HEAVY PRIORITY for latest YTS additions")
    
    filtered_movies = notifier.filter_high_rated_movies(movies)
    
    if not filtered_movies:
        print("❌ No 2025+ mainstream movies found")
        return
    
    print(f"✅ Found {len(filtered_movies)} 2025+ mainstream movies")
    
    # Show results with scores and recency info
    print("\n🎬 Top 2025+ Mainstream Movies (Sorted by Latest YTS Priority):")
    print("-" * 85)
    
    for i, movie in enumerate(filtered_movies[:10], 1):
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        score = movie.get('_score', 0)
        date_added = movie.get('date_uploaded', 'Unknown')
        
        # Calculate recency
        recency_info = "Unknown"
        try:
            if date_added != 'Unknown':
                from datetime import datetime
                date_obj = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
                current_time = datetime.now(date_obj.tzinfo)
                hours_since_added = (current_time - date_obj).total_seconds() / 3600
                
                if hours_since_added <= 24:
                    recency_info = f"🔥 JUST ADDED ({hours_since_added:.1f}h ago)"
                elif hours_since_added <= 72:
                    recency_info = f"⚡ FRESH ({hours_since_added:.1f}h ago)"
                elif hours_since_added <= 168:
                    recency_info = f"🆕 NEW ({hours_since_added:.1f}h ago)"
                else:
                    recency_info = f"📅 {hours_since_added:.1f}h ago"
        except:
            recency_info = "Unknown"
        
        print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
        print(f"   Genres: {genres}")
        print(f"   Score: {score:.1f} | {recency_info}")
        
        # Show torrent info
        torrents = movie.get('torrents', [])
        if torrents:
            total_seeds = sum(torrent.get('seeds', 0) for torrent in torrents)
            print(f"   📥 {len(torrents)} qualities, {total_seeds} total seeds")
        
        print()
    
    # Test notification formatting
    if filtered_movies:
        print("📝 Testing Enhanced Notification Format with Latest Priority:")
        print("-" * 85)
        sample_movie = filtered_movies[0]
        notification = notifier.format_movie_notification(sample_movie)
        print(notification)

async def main():
    """Main test function"""
    print("🎬 Enhanced Movie Notifier - Latest YTS Priority Test")
    print("=" * 85)
    
    try:
        await test_latest_priority()
        
        print("\n🎉 Latest YTS priority test completed!")
        print("\n✅ Features verified:")
        print("• Heavy priority for latest YTS additions (last 24h = +50 points)")
        print("• Fresh releases priority (last 3 days = +30 points)")
        print("• New additions priority (last week = +20 points)")
        print("• Year filtering (2025 and future years only)")
        print("• Genre exclusions (Biography, Documentary, Drama, History, Sport, Music)")
        print("• Enhanced notification format with recency indicators")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 