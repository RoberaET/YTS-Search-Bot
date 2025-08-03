#!/usr/bin/env python3
"""
Setup script for Movie Torrent Finder Bot
This script helps users set up the bot quickly.
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists('env_example.txt'):
        shutil.copy('env_example.txt', '.env')
        print("✅ Created .env file from template")
        print("📝 Please edit .env and add your BOT_TOKEN")
        return True
    else:
        print("❌ env_example.txt not found")
        return False

def check_bot_token():
    """Check if bot token is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    
    if bot_token and bot_token != 'your_bot_token_here':
        print("✅ BOT_TOKEN is configured")
        return True
    else:
        print("❌ BOT_TOKEN not configured")
        print("Please edit .env file and add your bot token")
        return False

def run_tests():
    """Run test suite"""
    print("\n🧪 Running tests...")
    
    try:
        subprocess.check_call([sys.executable, "test_bot.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  Test file not found, skipping tests")
        return True

def main():
    """Main setup function"""
    print("🎬 Movie Torrent Finder Bot - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check bot token
    token_configured = check_bot_token()
    
    # Run tests
    tests_passed = run_tests()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    
    if token_configured and tests_passed:
        print("\n✅ Your bot is ready to run!")
        print("Run: python bot.py")
    else:
        print("\n⚠️  Setup completed with warnings:")
        if not token_configured:
            print("• Please configure your BOT_TOKEN in .env file")
        if not tests_passed:
            print("• Some tests failed, check the output above")
        
        print("\nAfter fixing the issues, run: python bot.py")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 