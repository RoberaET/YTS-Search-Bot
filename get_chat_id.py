#!/usr/bin/env python3
"""
Helper script to get your Telegram chat ID
Run this script and send a message to your bot to get your chat ID
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    
    message = f"""
🎬 **Welcome to Movie Release Notifier Setup!**

Hi {user_name}! 👋

Your **Chat ID** is: `{chat_id}`

To set up notifications:
1. Copy this chat ID: `{chat_id}`
2. Add it to your `.env` file as: `CHAT_ID={chat_id}`
3. Run the movie notifier: `python movie_notifier.py`

The bot will then automatically send you notifications about new high-rated movies!
    """
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any message to show chat ID"""
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    
    message = f"""
📱 **Your Chat ID Information**

Hi {user_name}! 

Your **Chat ID** is: `{chat_id}`

To complete setup:
1. Copy this chat ID: `{chat_id}`
2. Add it to your `.env` file as: `CHAT_ID={chat_id}`
3. Run: `python movie_notifier.py`

You'll then receive automatic notifications about new movies with IMDb ratings ≥ 6.0!
    """
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🔧 **Setup Instructions**

1. **Get your Chat ID** (you just did this!)
2. **Add to .env file:**
   ```
   BOT_TOKEN=your_bot_token
   CHAT_ID=your_chat_id
   ```
3. **Run the notifier:**
   ```
   python movie_notifier.py
   ```

The bot will check YTS.mx every hour for new movies with IMDb ratings ≥ 6.0 and send you notifications!
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Start the chat ID helper bot"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in .env file!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🚀 Starting Chat ID Helper Bot...")
    print("📱 Send any message to your bot to get your Chat ID")
    print("⏹️  Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 