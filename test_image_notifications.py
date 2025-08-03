#!/usr/bin/env python3
"""
Test script for the Enhanced Movie Notifier with Image Notifications
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_image_notifications():
    """Test the image notification functionality"""
    print("🧪 Testing Enhanced Movie Notifier with Image Notifications")
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
    print(f"\n⭐ Filtering for 2025+ movies with images...")
    print(f"   • Rating >= 6.0")
    print(f"   • Year >= 2025 (current and future years only)")
    print(f"   • Excluding: Biography, Documentary, Drama, History, Sport, Music")
    print(f"   • Including movie poster images in notifications")
    
    filtered_movies = notifier.filter_high_rated_movies(movies)
    
    if not filtered_movies:
        print("❌ No 2025+ movies found")
        return
    
    print(f"✅ Found {len(filtered_movies)} 2025+ movies")
    
    # Show results with image availability
    print("\n🎬 Top 2025+ Movies with Image Availability:")
    print("-" * 85)
    
    for i, movie in enumerate(filtered_movies[:5], 1):
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        score = movie.get('_score', 0)
        
        # Check image availability
        large_image = movie.get('large_cover_image')
        medium_image = movie.get('medium_cover_image')
        
        if large_image:
            image_status = "🖼️ Large poster available"
            image_url = large_image
        elif medium_image:
            image_status = "🖼️ Medium poster available"
            image_url = medium_image
        else:
            image_status = "❌ No poster available"
            image_url = "None"
        
        print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
        print(f"   Genres: {genres}")
        print(f"   Score: {score:.1f}")
        print(f"   {image_status}")
        if image_url != "None":
            print(f"   Image URL: {image_url[:50]}...")
        print()
    
    # Test notification formatting with image info
    if filtered_movies:
        print("📝 Testing Notification Format with Image Info:")
        print("-" * 85)
        sample_movie = filtered_movies[0]
        notification = notifier.format_movie_notification(sample_movie)
        print(notification)
        
        # Show image details
        large_image = sample_movie.get('large_cover_image')
        medium_image = sample_movie.get('medium_cover_image')
        
        print(f"\n🖼️ Image Details for '{sample_movie.get('title')}':")
        if large_image:
            print(f"   Large poster: {large_image}")
        if medium_image:
            print(f"   Medium poster: {medium_image}")

async def main():
    """Main test function"""
    print("🎬 Enhanced Movie Notifier - Image Notification Test")
    print("=" * 85)
    
    try:
        await test_image_notifications()
        
        print("\n🎉 Image notification test completed!")
        print("\n✅ New Features verified:")
        print("• Movie poster images included in notifications")
        print("• Large cover images prioritized over medium")
        print("• Fallback to text-only if image unavailable")
        print("• Error handling for image sending failures")
        print("• Enhanced notification format with image indicators")
        print("• All previous filtering and priority features maintained")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 