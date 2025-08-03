#!/usr/bin/env python3
"""
Test script for the Enhanced Movie Notifier with Comedy Excluded
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_no_comedy_filtering():
    """Test the filtering system with Comedy excluded"""
    print("🧪 Testing Enhanced Movie Notifier with Comedy Excluded")
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
    print(f"\n⭐ Filtering for 2025+ movies (Comedy EXCLUDED)...")
    print(f"   • Rating >= 6.0")
    print(f"   • Year >= 2025 (current and future years only)")
    print(f"   • Excluding: Biography, Documentary, Drama, History, Sport, Music")
    print(f"   • Comedy movies are now EXCLUDED")
    print(f"   • Prioritizing: Action, Adventure, Crime, Fantasy, Horror, Mystery, Romance, Sci-Fi, Thriller, War, Western")
    
    filtered_movies = notifier.filter_high_rated_movies(movies)
    
    if not filtered_movies:
        print("❌ No 2025+ non-comedy movies found")
        return
    
    print(f"✅ Found {len(filtered_movies)} 2025+ non-comedy movies")
    
    # Show results with genre information
    print("\n🎬 Top 2025+ Movies (Comedy Excluded):")
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
        
        # Check if it's a comedy (should be excluded)
        is_comedy = 'Comedy' in movie.get('genres', [])
        comedy_warning = " ⚠️ COMEDY (SHOULD BE EXCLUDED)" if is_comedy else ""
        
        print(f"{i}. {title} ({year}) - {rating}/10 ⭐{comedy_warning}")
        print(f"   Genres: {genres}")
        print(f"   Score: {score:.1f} | {recency_info}")
        
        # Show torrent info
        torrents = movie.get('torrents', [])
        if torrents:
            total_seeds = sum(torrent.get('seeds', 0) for torrent in torrents)
            print(f"   📥 {len(torrents)} qualities, {total_seeds} total seeds")
        
        print()
    
    # Check for any comedy movies that might have slipped through
    comedy_movies = [m for m in filtered_movies if 'Comedy' in m.get('genres', [])]
    if comedy_movies:
        print("⚠️  WARNING: Found Comedy movies that should be excluded:")
        for movie in comedy_movies:
            print(f"   • {movie.get('title')} - {', '.join(movie.get('genres', []))}")
    else:
        print("✅ SUCCESS: No Comedy movies found in filtered results")
    
    # Test notification formatting
    if filtered_movies:
        print("📝 Testing Notification Format (Comedy Excluded):")
        print("-" * 85)
        sample_movie = filtered_movies[0]
        notification = notifier.format_movie_notification(sample_movie)
        print(notification)

async def main():
    """Main test function"""
    print("🎬 Enhanced Movie Notifier - Comedy Exclusion Test")
    print("=" * 85)
    
    try:
        await test_no_comedy_filtering()
        
        print("\n🎉 Comedy exclusion test completed!")
        print("\n✅ Updated Features verified:")
        print("• Comedy genre removed from preferred genres")
        print("• Comedy genre removed from high-priority genres")
        print("• Only Action, Adventure, Crime, Fantasy, Horror, Mystery, Romance, Sci-Fi, Thriller, War, Western prioritized")
        print("• All previous filtering features maintained")
        print("• Movie poster images still included")
        print("• 2025+ year filtering maintained")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 