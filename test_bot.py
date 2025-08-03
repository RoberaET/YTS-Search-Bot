#!/usr/bin/env python3
"""
Test script for the Movie Torrent Finder Bot
This script tests the YTS API integration without running the actual Telegram bot.
"""

import sys
import os
from yts_api import YTSAPI

def test_yts_api():
    """Test the YTS API functionality"""
    print("🧪 Testing YTS API Integration")
    print("=" * 40)
    
    yts = YTSAPI()
    
    # Test movies to search for
    test_movies = [
        "Inception",
        "The Dark Knight",
        "Interstellar",
        "Pulp Fiction",
        "The Matrix"
    ]
    
    for movie in test_movies:
        print(f"\n🔍 Searching for: {movie}")
        print("-" * 30)
        
        try:
            movies = yts.search_movies(movie)
            
            if movies:
                print(f"✅ Found {len(movies)} movies with rating ≥ 6.0")
                
                # Show first result
                first_movie = movies[0]
                title = first_movie.get('title', 'Unknown')
                year = first_movie.get('year', 'Unknown')
                rating = first_movie.get('rating', 0)
                
                print(f"📽️  Top result: {title} ({year}) - {rating}/10")
                
                # Check torrents
                torrents = yts.get_torrents_for_movie(first_movie)
                if torrents:
                    print(f"📥 Available torrents: {len(torrents)}")
                    for i, torrent in enumerate(torrents[:3], 1):
                        quality = torrent.get('quality', 'Unknown')
                        size = torrent.get('size', 'Unknown')
                        seeds = torrent.get('seeds', 0)
                        print(f"   {i}. {quality} - {size} (🌱 {seeds} seeds)")
                else:
                    print("❌ No torrents available")
                    
            else:
                print("❌ No movies found with rating ≥ 6.0")
                
        except Exception as e:
            print(f"❌ Error searching for {movie}: {e}")
    
    print("\n" + "=" * 40)
    print("✅ YTS API test completed!")

def test_movie_formatting():
    """Test movie information formatting"""
    print("\n🎬 Testing Movie Formatting")
    print("=" * 40)
    
    yts = YTSAPI()
    
    # Test with a known movie
    movies = yts.search_movies("Inception")
    
    if movies:
        movie = movies[0]
        formatted_info = yts.format_movie_info(movie)
        
        print("📝 Formatted movie information:")
        print("-" * 30)
        print(formatted_info)
    else:
        print("❌ Could not find test movie for formatting")

def main():
    """Main test function"""
    print("🎬 Movie Torrent Finder Bot - Test Suite")
    print("=" * 50)
    
    # Test YTS API
    test_yts_api()
    
    # Test formatting
    test_movie_formatting()
    
    print("\n🎉 All tests completed!")
    print("\nIf all tests passed, your bot should work correctly.")
    print("Make sure to set your BOT_TOKEN before running the actual bot.")

if __name__ == "__main__":
    main() 