#!/usr/bin/env python3
"""
Test script to verify that 28 Years Later is now being found
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_28_years_fix():
    """Test that 28 Years Later is now being found"""
    print("🧪 Testing Enhanced Movie Notifier - 28 Years Later Fix")
    print("=" * 75)
    
    notifier = EnhancedMovieNotifier()
    
    # Test getting latest movies
    print("📡 Fetching latest movies from YTS...")
    movies = await notifier.get_latest_movies()
    
    if not movies:
        print("❌ No movies found")
        return
    
    print(f"✅ Found {len(movies)} movies (including 28 Years Later search)")
    
    # Look for 28 Years Later specifically
    found_28_years = None
    for movie in movies:
        title = movie.get('title', '').lower()
        if '28 years later' in title:
            found_28_years = movie
            break
    
    if found_28_years:
        print(f"\n🎯 FOUND 28 YEARS LATER!")
        title = found_28_years.get('title', 'Unknown')
        year = found_28_years.get('year', 'Unknown')
        rating = found_28_years.get('rating', 0)
        genres = ', '.join(found_28_years.get('genres', []))
        date_added = found_28_years.get('date_uploaded', 'Unknown')
        
        print(f"   Title: {title}")
        print(f"   Year: {year}")
        print(f"   Rating: {rating}/10")
        print(f"   Genres: {genres}")
        print(f"   Date Added: {date_added}")
        
        # Check if it meets our criteria
        meets_criteria = (
            rating >= 6.0 and 
            year >= 2025 and 
            not any(genre in {'Biography', 'Documentary', 'Drama', 'History', 'Sport', 'Music', 'Comedy'} 
                   for genre in found_28_years.get('genres', []))
        )
        
        if meets_criteria:
            print("   ✅ MEETS ALL CRITERIA - WILL BE NOTIFIED!")
        else:
            print("   ❌ DOESN'T MEET CRITERIA")
    else:
        print("\n❌ 28 Years Later not found in the movie list")
    
    # Test filtering
    print(f"\n⭐ Testing filtering system...")
    filtered_movies = notifier.filter_high_rated_movies(movies)
    
    print(f"✅ Found {len(filtered_movies)} movies after filtering")
    
    # Check if 28 Years Later is in the filtered results
    filtered_28_years = None
    for movie in filtered_movies:
        title = movie.get('title', '').lower()
        if '28 years later' in title:
            filtered_28_years = movie
            break
    
    if filtered_28_years:
        print(f"\n🎉 28 YEARS LATER WILL BE NOTIFIED!")
        title = filtered_28_years.get('title', 'Unknown')
        score = filtered_28_years.get('_score', 0)
        print(f"   Title: {title}")
        print(f"   Priority Score: {score}")
    else:
        print(f"\n❌ 28 Years Later not in filtered results")
        
        # Show what movies are being filtered
        print(f"\n📋 Movies that passed filtering:")
        for i, movie in enumerate(filtered_movies[:5], 1):
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'Unknown')
            rating = movie.get('rating', 0)
            genres = ', '.join(movie.get('genres', []))
            score = movie.get('_score', 0)
            
            print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
            print(f"   Genres: {genres}")
            print(f"   Score: {score}")
            print()

async def main():
    """Main test function"""
    print("🎬 28 Years Later Fix Test")
    print("=" * 85)
    
    try:
        await test_28_years_fix()
        
        print("\n🎉 Test completed!")
        print("\n💡 Expected Results:")
        print("• 28 Years Later should be found in the movie list")
        print("• It should meet all criteria (2025+, 6.0+, non-excluded genres)")
        print("• It should be included in filtered results")
        print("• It should be notified via Telegram")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 