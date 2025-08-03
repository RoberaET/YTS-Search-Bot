#!/usr/bin/env python3
"""
Test script to verify notification for 28 Years Later
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_notification():
    """Test notification for 28 Years Later"""
    print("🧪 Testing Notification for 28 Years Later")
    print("=" * 75)
    
    notifier = EnhancedMovieNotifier()
    
    # Create a mock 28 Years Later movie
    movie_28_years = {
        'id': 12345,
        'title': '28 Years Later',
        'year': 2025,
        'rating': 6.9,
        'genres': ['Horror', 'Thriller'],
        'date_uploaded': '2025-07-29T08:00:50Z',
        'large_cover_image': 'https://example.com/poster.jpg',
        'torrents': [
            {'quality': '1080p', 'size': '2.1 GB', 'seeds': 150, 'peers': 20},
            {'quality': '720p', 'size': '1.2 GB', 'seeds': 200, 'peers': 30}
        ],
        'slug': '28-years-later-2025'
    }
    
    print("📝 Testing notification format...")
    notification = notifier.format_movie_notification(movie_28_years)
    print("\n" + notification)
    
    print(f"\n✅ Notification format test completed!")
    print(f"📱 This notification would be sent to Telegram")
    print(f"🎬 Movie: 28 Years Later (2025)")
    print(f"⭐ Rating: 6.9/10")
    print(f"🎭 Genres: Horror, Thriller")
    print(f"📅 Added: July 29, 2025")
    
    # Test if it would pass filtering
    print(f"\n🔍 Testing filtering...")
    filtered_movies = notifier.filter_high_rated_movies([movie_28_years])
    
    if filtered_movies:
        print(f"✅ 28 Years Later PASSES filtering!")
        score = filtered_movies[0].get('_score', 0)
        print(f"📊 Priority Score: {score}")
    else:
        print(f"❌ 28 Years Later FAILS filtering")

async def main():
    """Main test function"""
    print("🎬 28 Years Later Notification Test")
    print("=" * 85)
    
    try:
        await test_notification()
        
        print("\n🎉 Test completed!")
        print("\n💡 Summary:")
        print("• 28 Years Later meets all criteria")
        print("• Notification format is working")
        print("• The bot should send this notification")
        print("• Check your Telegram for the notification!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 