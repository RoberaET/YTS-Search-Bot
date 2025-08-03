#!/usr/bin/env python3
"""
Railway Deployment Helper Script
This script helps with Railway-specific deployment configurations.
"""

import os
import sys

def create_railway_config():
    """Create Railway-specific configuration files"""
    
    # Create Procfile for Railway
    procfile_content = """web: python bot.py"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("✅ Created Procfile for Railway deployment")
    
    # Create runtime.txt for Python version
    runtime_content = """python-3.11.0"""
    
    with open('runtime.txt', 'w') as f:
        f.write(runtime_content)
    
    print("✅ Created runtime.txt for Python version")
    
    # Create .dockerignore for Railway
    dockerignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment files
.env
.env.local
.env.example

# Git
.git/
.gitignore

# Documentation
README.md
*.md

# Temporary files
*.tmp
*.temp
"""
    
    with open('.dockerignore', 'w') as f:
        f.write(dockerignore_content)
    
    print("✅ Created .dockerignore for Railway")

def check_environment():
    """Check if required environment variables are set"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN environment variable is not set!")
        print("Please set it in Railway's environment variables section.")
        return False
    
    print("✅ BOT_TOKEN is configured")
    return True

def main():
    """Main function"""
    print("🚀 Railway Deployment Helper")
    print("=" * 40)
    
    # Create Railway-specific files
    create_railway_config()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("\n🎉 Railway deployment files created successfully!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repository to Railway")
    print("3. Set BOT_TOKEN in Railway environment variables")
    print("4. Deploy!")
    
    print("\n📝 Railway Environment Variables to set:")
    print("BOT_TOKEN=your_telegram_bot_token_here")

if __name__ == "__main__":
    main() 