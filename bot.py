import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from config import BOT_TOKEN, MAX_RESULTS
from yts_api import YTSAPI

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MovieTorrentBot:
    def __init__(self):
        self.yts_api = YTSAPI()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🎬 **Welcome to Movie Torrent Finder Bot!**

I can help you find high-quality movie torrents with IMDb ratings of 6.0 or higher.

**How to use:**
• Simply send me a movie title
• I'll search for movies with good ratings
• You'll get download links for available torrents

**Commands:**
/start - Show this welcome message
/help - Show help information
/search <movie> - Search for a specific movie

**Example:** Try sending "Inception" or "The Dark Knight"
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🔍 **How to use this bot:**

1. **Search by movie title:** Just type the movie name
   Example: "Inception", "The Dark Knight", "Interstellar"

2. **Use search command:** /search <movie title>
   Example: /search Inception

3. **What you'll get:**
   • Movie title and year
   • IMDb rating (only movies ≥ 6.0)
   • Available torrent qualities
   • Download links (magnet URLs)
   • Seed/peer information

**Features:**
✅ Only shows movies with IMDb rating ≥ 6.0
✅ Multiple quality options (4K, 1080p, 720p, 480p)
✅ Sorted by quality preference
✅ Seed/peer count for each torrent
✅ Direct magnet link downloads

**Note:** This bot uses the YTS API to find legitimate torrent sources.
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a movie title.\n"
                "Usage: /search <movie title>\n"
                "Example: /search Inception"
            )
            return
        
        query = ' '.join(context.args)
        await self.search_movies(update, context, query)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages as movie searches"""
        if update.message.text.startswith('/'):
            return
        
        query = update.message.text.strip()
        if len(query) < 2:
            await update.message.reply_text(
                "❌ Please enter a movie title (at least 2 characters)."
            )
            return
        
        await self.search_movies(update, context, query)
    
    async def search_movies(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
        """Search for movies and send results"""
        # Send typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Search for movies
        movies = self.yts_api.search_movies(query)
        
        if not movies:
            await update.message.reply_text(
                f"❌ No movies found with rating ≥ 6.0 for '{query}'\n\n"
                "Try:\n"
                "• Checking the spelling\n"
                "• Using a different title\n"
                "• Searching for a more popular movie"
            )
            return
        
        # Limit results
        movies = movies[:MAX_RESULTS]
        
        # Send results
        await update.message.reply_text(
            f"🎬 Found {len(movies)} movies with rating ≥ 6.0 for '{query}':\n"
            f"{'='*50}"
        )
        
        for i, movie in enumerate(movies, 1):
            movie_info = self.yts_api.format_movie_info(movie)
            
            # Create inline keyboard for quick actions
            keyboard = []
            torrents = self.yts_api.get_torrents_for_movie(movie)
            
            if torrents:
                # Add buttons for different qualities
                for j, torrent in enumerate(torrents[:3], 1):  # Limit to 3 qualities
                    quality = torrent.get('quality', 'Unknown')
                    magnet_url = torrent.get('url', '')
                    keyboard.append([
                        InlineKeyboardButton(
                            f"📥 {quality}",
                            url=magnet_url
                        )
                    ])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            try:
                await update.message.reply_text(
                    movie_info,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Error sending movie info: {e}")
                # Send without markdown if there's an error
                await update.message.reply_text(
                    f"Movie {i}: {movie.get('title', 'Unknown')} - {movie.get('rating', 0)}/10"
                )
            
            # Small delay between messages to avoid rate limiting
            await asyncio.sleep(0.5)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Sorry, something went wrong. Please try again later."
            )

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        print("Please set your BOT_TOKEN in the .env file")
        return
    
    # Create bot instance
    bot = MovieTorrentBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("search", bot.search_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    logger.info("Starting Movie Torrent Finder Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 