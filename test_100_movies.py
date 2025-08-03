#!/usr/bin/env python3
"""
Test script to verify 100 movie search and 28 Years Later detection
"""

import asyncio
import logging
import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_100_movies():
    """Test fetching 100 movies from YTS"""
    print("🧪 Testing 100 Movie Search from YTS")
    print("=" * 75)
    
    # YTS API endpoints
    YTS_BASE_URL = "https://yts.mx/api/v2"
    YTS_LATEST_URL = f"{YTS_BASE_URL}/list_movies.json"
    
    async with aiohttp.ClientSession() as session:
        # Test fetching 100 movies
        print("📡 Fetching 100 latest movies from YTS...")
        params = {
            'limit': 100,
            'sort_by': 'date_added',
            'order_by': 'desc'
        }
        
        try:
            async with session.get(YTS_LATEST_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    movies = data.get('data', {}).get('movies', [])
                    
                    print(f"✅ Found {len(movies)} movies with limit=100")
                    
                    # Look for 28 Years Later
                    found_28_years = None
                    for movie in movies:
                        title = movie.get('title', '').lower()
                        if '28 years later' in title:
                            found_28_years = movie
                            break
                    
                    if found_28_years:
                        print(f"\n🎯 FOUND 28 YEARS LATER in 100 movie search!")
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
                    else:
                        print(f"\n❌ 28 Years Later NOT found in 100 movie search")
                        
                        # Show first 10 movies to see what we got
                        print(f"\n📋 First 10 movies from 100 search:")
                        for i, movie in enumerate(movies[:10], 1):
                            title = movie.get('title', 'Unknown')
                            year = movie.get('year', 'Unknown')
                            rating = movie.get('rating', 0)
                            genres = ', '.join(movie.get('genres', []))
                            
                            print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
                            print(f"   Genres: {genres}")
                            print()
                    
                    # Check how many 2025 movies we have
                    movies_2025 = [m for m in movies if m.get('year', 0) >= 2025]
                    print(f"\n📊 Summary:")
                    print(f"   • Total movies: {len(movies)}")
                    print(f"   • 2025+ movies: {len(movies_2025)}")
                    print(f"   • 28 Years Later found: {'Yes' if found_28_years else 'No'}")
                    
                else:
                    print(f"❌ Failed to fetch movies: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main test function"""
    print("🎬 100 Movie Search Test")
    print("=" * 85)
    
    try:
        await test_100_movies()
        
        print("\n🎉 Test completed!")
        print("\n💡 Expected Results:")
        print("• Should fetch 100 movies from YTS")
        print("• 28 Years Later should be found in the 100 movie list")
        print("• This will help the bot find more recent movies")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 