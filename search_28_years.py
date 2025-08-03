#!/usr/bin/env python3
"""
Search script to find "28 Years Later" specifically
"""

import asyncio
import logging
import aiohttp
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def search_28_years_later():
    """Search specifically for 28 Years Later"""
    print("🔍 Searching for '28 Years Later' specifically")
    print("=" * 75)
    
    # YTS API endpoints
    YTS_API_BASE_URL = "https://yts.mx/api/v2"
    YTS_LIST_MOVIES_URL = f"{YTS_API_BASE_URL}/list_movies.json"
    YTS_SEARCH_URL = f"{YTS_API_BASE_URL}/list_movies.json"
    
    async with aiohttp.ClientSession() as session:
        # First, let's search for "28 Years Later" specifically
        print("📡 Searching for '28 Years Later'...")
        search_params = {
            'query_term': '28 Years Later',
            'limit': 20,
            'sort_by': 'date_added',
            'order_by': 'desc'
        }
        
        try:
            async with session.get(YTS_SEARCH_URL, params=search_params) as response:
                if response.status == 200:
                    data = await response.json()
                    movies = data.get('data', {}).get('movies', [])
                    
                    print(f"✅ Found {len(movies)} movies with '28 Years Later' in search")
                    
                    for i, movie in enumerate(movies, 1):
                        title = movie.get('title', 'Unknown')
                        year = movie.get('year', 'Unknown')
                        rating = movie.get('rating', 0)
                        genres = ', '.join(movie.get('genres', []))
                        date_added = movie.get('date_uploaded', 'Unknown')
                        
                        print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
                        print(f"   Genres: {genres}")
                        print(f"   Date Added: {date_added}")
                        print()
                else:
                    print(f"❌ Search failed with status {response.status}")
                    
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Now let's check the latest movies to see what's actually available
        print("\n📡 Checking latest movies from YTS...")
        latest_params = {
            'limit': 50,
            'sort_by': 'date_added',
            'order_by': 'desc'
        }
        
        try:
            async with session.get(YTS_LIST_MOVIES_URL, params=latest_params) as response:
                if response.status == 200:
                    data = await response.json()
                    movies = data.get('data', {}).get('movies', [])
                    
                    print(f"✅ Found {len(movies)} latest movies")
                    
                    # Look for any movie with "28" or "Years" in the title
                    found_matches = []
                    for movie in movies:
                        title = movie.get('title', '').lower()
                        if '28' in title or 'years' in title or 'later' in title:
                            found_matches.append(movie)
                    
                    if found_matches:
                        print(f"\n🎯 Found {len(found_matches)} potential matches:")
                        for i, movie in enumerate(found_matches, 1):
                            title = movie.get('title', 'Unknown')
                            year = movie.get('year', 'Unknown')
                            rating = movie.get('rating', 0)
                            genres = ', '.join(movie.get('genres', []))
                            
                            print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
                            print(f"   Genres: {genres}")
                            print()
                    else:
                        print("\n❌ No movies found with '28', 'Years', or 'Later' in title")
                        
                        # Show first 10 movies to see what's available
                        print("\n📋 First 10 latest movies:")
                        for i, movie in enumerate(movies[:10], 1):
                            title = movie.get('title', 'Unknown')
                            year = movie.get('year', 'Unknown')
                            rating = movie.get('rating', 0)
                            genres = ', '.join(movie.get('genres', []))
                            
                            print(f"{i}. {title} ({year}) - {rating}/10 ⭐")
                            print(f"   Genres: {genres}")
                            print()
                else:
                    print(f"❌ Latest movies fetch failed with status {response.status}")
                    
        except Exception as e:
            print(f"❌ Latest movies error: {e}")

async def main():
    """Main function"""
    print("🎬 28 Years Later Search Test")
    print("=" * 85)
    
    try:
        await search_28_years_later()
        
        print("\n🎉 Search completed!")
        print("\n💡 Possible reasons why '28 Years Later' isn't found:")
        print("• Movie might not be in YTS database yet")
        print("• Movie might have a different title")
        print("• Movie might be too new and not indexed yet")
        print("• YTS might not have the movie available")
        
    except Exception as e:
        print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 