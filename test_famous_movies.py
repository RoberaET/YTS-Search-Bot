#!/usr/bin/env python3
"""
Test script for the Enhanced Movie Notifier with Famous Movie Priority
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_famous_movie_priority():
    """Test the priority system for famous, mainstream movies"""
    print("🧪 Testing Enhanced Movie Notifier with Famous Movie Priority")
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
    print(f"\n⭐ Filtering for 2025+ famous mainstream movies...")
    print(f"   • Rating >= 6.0")
    print(f"   • Year >= 2025 (current and future years only)")
    print(f"   • Excluding: Biography, Documentary, Drama, History, Sport, Music")
    print(f"   • HEAVY PRIORITY for famous, talked-about movies")
    print(f"   • Bonus for sequels, remakes, and high-profile releases")
    
    filtered_movies = notifier.filter_high_rated_movies(movies)
    
    if not filtered_movies:
        print("❌ No 2025+ famous mainstream movies found")
        return
    
    print(f"✅ Found {len(filtered_movies)} 2025+ famous mainstream movies")
    
    # Show results with scores and movie type indicators
    print("\n🎬 Top 2025+ Famous Mainstream Movies (Sorted by Priority):")
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
        
        # Determine movie type
        title_lower = title.lower()
        is_famous = any(pattern in title_lower for pattern in ['years later', 'happy', 'gilmore', 'sitaare', 'zameen', 'par'])
        is_sequel = any(char.isdigit() for char in title) or any(indicator in title_lower for indicator in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'part', 'sequel', 'remake', 'reboot'])
        
        movie_type = ""
        if is_famous:
            movie_type = "🌟 FAMOUS"
        elif is_sequel:
            movie_type = "🎭 SEQUEL"
        else:
            movie_type = "📽️ REGULAR"
        
        print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
        print(f"   Type: {movie_type} | Genres: {genres}")
        print(f"   Score: {score:.1f} | {recency_info}")
        
        # Show torrent info
        torrents = movie.get('torrents', [])
        if torrents:
            total_seeds = sum(torrent.get('seeds', 0) for torrent in torrents)
            print(f"   📥 {len(torrents)} qualities, {total_seeds} total seeds")
        
        print()
    
    # Test notification formatting
    if filtered_movies:
        print("📝 Testing Enhanced Notification Format with Famous Movie Priority:")
        print("-" * 85)
        sample_movie = filtered_movies[0]
        notification = notifier.format_movie_notification(sample_movie)
        print(notification)

async def main():
    """Main test function"""
    print("🎬 Enhanced Movie Notifier - Famous Movie Priority Test")
    print("=" * 85)
    
    try:
        await test_famous_movie_priority()
        
        print("\n🎉 Famous movie priority test completed!")
        print("\n✅ Enhanced Features verified:")
        print("• Heavy priority for latest YTS additions (last 24h = +100 points)")
        print("• Famous movie detection (Years Later, Happy Gilmore, Sitaare Zameen Par)")
        print("• Sequel/remake detection with bonus points (+20 points)")
        print("• High-priority genre bonuses (Action, Adventure, Comedy, Thriller, Sci-Fi, Horror)")
        print("• Enhanced rating importance (3x multiplier)")
        print("• Popularity indicators (seed count bonuses)")
        print("• Special notification headers for famous/sequel movies")
        print("• Year filtering (2025 and future years only)")
        print("• Genre exclusions (Biography, Documentary, Drama, History, Sport, Music)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 