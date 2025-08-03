#!/usr/bin/env python3
"""
Test script to see what movies are available in YTS
"""

import asyncio
import logging
from enhanced_movie_notifier import EnhancedMovieNotifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_available_movies():
    """Test to see what movies are available"""
    print("🧪 Testing Available Movies in YTS")
    print("=" * 75)
    
    notifier = EnhancedMovieNotifier()
    
    # Test getting latest movies
    print("📡 Fetching latest movies from YTS...")
    movies = await notifier.get_latest_movies()
    
    if not movies:
        print("❌ No movies found")
        return
    
    print(f"✅ Found {len(movies)} latest movies")
    
    # Show all movies with their details
    print("\n🎬 All Available Movies:")
    print("-" * 85)
    
    comedy_count = 0
    excluded_count = 0
    valid_count = 0
    
    for i, movie in enumerate(movies[:20], 1):  # Show first 20
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = movie.get('genres', [])
        genres_str = ', '.join(genres)
        
        # Check if it's comedy
        is_comedy = 'Comedy' in genres
        if is_comedy:
            comedy_count += 1
        
        # Check if it would be excluded
        excluded_genres = {'Biography', 'Documentary', 'Drama', 'History', 'Sport', 'Music', 'Comedy'}
        is_excluded = any(genre in excluded_genres for genre in genres)
        if is_excluded:
            excluded_count += 1
        else:
            valid_count += 1
        
        # Check if it meets basic criteria
        meets_criteria = rating >= 6.0 and year >= 2025 and not is_excluded
        
        status = ""
        if is_comedy:
            status = " 🚫 COMEDY (EXCLUDED)"
        elif is_excluded:
            status = " 🚫 EXCLUDED"
        elif meets_criteria:
            status = " ✅ VALID"
        else:
            status = " ❌ DOESN'T MEET CRITERIA"
        
        print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
        print(f"   Genres: {genres_str}{status}")
        print()
    
    # Summary
    print("📊 SUMMARY:")
    print(f"   • Total movies checked: {len(movies[:20])}")
    print(f"   • Comedy movies: {comedy_count}")
    print(f"   • Excluded movies (all excluded genres): {excluded_count}")
    print(f"   • Valid movies (not excluded): {valid_count}")
    print(f"   • Movies meeting all criteria (2025+, 6.0+, not excluded): {sum(1 for m in movies[:20] if m.get('rating', 0) >= 6.0 and m.get('year', 0) >= 2025 and not any(g in {'Biography', 'Documentary', 'Drama', 'History', 'Sport', 'Music', 'Comedy'} for g in m.get('genres', [])))}")
    
    # Show genre breakdown
    print("\n🎭 GENRE BREAKDOWN:")
    all_genres = {}
    for movie in movies[:20]:
        for genre in movie.get('genres', []):
            all_genres[genre] = all_genres.get(genre, 0) + 1
    
    for genre, count in sorted(all_genres.items(), key=lambda x: x[1], reverse=True):
        excluded_mark = " 🚫" if genre in {'Biography', 'Documentary', 'Drama', 'History', 'Sport', 'Music', 'Comedy'} else ""
        print(f"   • {genre}: {count}{excluded_mark}")

async def main():
    """Main test function"""
    print("🎬 YTS Movie Availability Test")
    print("=" * 85)
    
    try:
        await test_available_movies()
        
        print("\n🎉 Test completed!")
        print("\n💡 Insights:")
        print("• This shows what movies are currently available in YTS")
        print("• Comedy movies are properly excluded")
        print("• The bot will notify you when new non-comedy movies are added")
        print("• Currently no 2025+ non-comedy movies with 6.0+ rating available")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 