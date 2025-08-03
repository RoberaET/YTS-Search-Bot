#!/usr/bin/env python3
"""
Movie Search Bot for Telegram (Railway Compatible)
Allows users to search for specific movies on YTS.mx
Note: Torrent download functionality removed for Railway compliance
"""

import asyncio
import logging
import os
import aiohttp
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

# API endpoints
YTS_BASE_URL = "https://yts.mx/api/v2"
YTS_SEARCH_URL = f"{YTS_BASE_URL}/list_movies.json"
OMDB_BASE_URL = "http://www.omdbapi.com/"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MovieSearchBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.last_search_results = {}  # Store last search results per user
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🎬 **Movie Search Bot**

Welcome! I can search for movies on YTS.mx for you.

**Commands:**
• `/search <movie title>` - Search for a specific movie
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`

**Note:** This version shows movie information and YTS links only.
        """
        
        # Create inline keyboard buttons
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🎬 **Movie Search Bot Help**

**Commands:**
• `/search <movie title>` - Search for a specific movie on YTS
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`

**What you'll get:**
• Movie poster image
• IMDb rating
• Rotten Tomatoes rating (if available)
• YTS.mx page link
• Movie details

**Note:** This version shows movie information and YTS links only.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        try:
            # Get search query from command
            query = ' '.join(context.args)
            if not query:
                await update.message.reply_text("❌ Please provide a movie title to search for.\n\nExample: `/search 28 Years Later`", parse_mode=ParseMode.MARKDOWN)
                await self.show_main_menu_buttons(update.message)
                return
            
            await self.perform_search(update, query)
            
        except Exception as e:
            logger.error(f"Error in search_command: {e}")
            await update.message.reply_text(f"❌ Error searching for: {query}\nPlease try again later.")
            await self.show_main_menu_buttons(update.message)

    async def perform_search(self, update: Update, query: str):
        """Perform the actual search"""
        try:
            # Show searching message
            searching_msg = await update.message.reply_text(f"🔍 Searching for: **{query}**...", parse_mode=ParseMode.MARKDOWN)
            
            # Search for movies
            movies = await self.search_movies(query)
            
            if not movies:
                await searching_msg.edit_text(f"❌ No movies found for: **{query}**\n\nTry a different search term.", parse_mode=ParseMode.MARKDOWN)
                await self.show_main_menu_buttons(update.message)
                return
            
            # Store results for this user
            user_id = update.effective_user.id
            self.last_search_results[user_id] = movies
            
            # Display results
            await self.display_search_results(update, movies, query)
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            await update.message.reply_text(f"❌ Error searching for: {query}\nPlease try again later.")
            await self.show_main_menu_buttons(update.message)

    async def search_movies(self, query: str):
        """Search for movies on YTS.mx"""
        try:
            params = {
                'query_term': query,
                'limit': 20,
                'sort_by': 'download_count',
                'order_by': 'desc'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(YTS_SEARCH_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'ok' and data.get('data', {}).get('movies'):
                            return data['data']['movies']
            return []
            
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return []

    async def display_search_results(self, update: Update, movies: list, query: str):
        """Display search results"""
        try:
            # Limit to first 5 movies
            movies = movies[:5]
            
            result_text = f"🎬 **Search Results for: {query}**\n\n"
            
            for i, movie in enumerate(movies, 1):
                movie_info = self.format_movie_info(movie)
                result_text += f"**{i}.** {movie_info}\n\n"
            
            result_text += "💡 **Tip:** Visit the YTS.mx links to download movies."
            
            # Create keyboard with search options
            keyboard = [
                [InlineKeyboardButton("🔍 New Search", callback_data="search_movies")],
                [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                [InlineKeyboardButton("❓ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Try to send with poster image
            try:
                if movies and movies[0].get('large_cover_image'):
                    await update.message.reply_photo(
                        photo=movies[0]['large_cover_image'],
                        caption=result_text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"Error displaying results: {e}")
            await update.message.reply_text("❌ Error displaying results. Please try again.")
            await self.show_main_menu_buttons(update.message)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "search_movies":
            await self.handle_search_button(query)
        elif query.data == "whats_new":
            await self.handle_whats_new_button(query)
        elif query.data == "help":
            await self.handle_help_button(query)
        elif query.data == "back_to_menu":
            await self.handle_back_to_menu(query)

    async def handle_search_button(self, query):
        """Handle search button press"""
        await query.edit_message_text(
            "🔍 **Search Movies**\n\nSend me a movie title to search for.\n\nExamples:\n• 28 Years Later\n• Deadpool 3\n• The Batman",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
            ]])
        )

    async def handle_help_button(self, query):
        """Handle help button press"""
        help_message = """
🎬 **Movie Search Bot Help**

**Commands:**
• `/search <movie title>` - Search for a specific movie on YTS
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`

**What you'll get:**
• Movie poster image
• IMDb rating
• Rotten Tomatoes rating (if available)
• YTS.mx page link
• Movie details

**Note:** This version shows movie information and YTS links only.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_whats_new_button(self, query):
        """Handle What's New button press"""
        try:
            await query.edit_message_text("🆕 **Loading Featured 2025 Movies...**", parse_mode=ParseMode.MARKDOWN)
            
            # Search for featured 2025 movies
            params = {
                'limit': 100,
                'sort_by': 'featured',
                'order_by': 'desc',
                'quality': 'all',
                'genre': 'all',
                'minimum_rating': '6',
                'year': '2025',
                'language': 'all'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(YTS_SEARCH_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'ok' and data.get('data', {}).get('movies'):
                            movies = data['data']['movies']
                            
                            if movies:
                                # Filter for 2025 movies and limit to 10
                                movies_2025 = [m for m in movies if m.get('year') == 2025][:10]
                                
                                if movies_2025:
                                    result_text = "🆕 **Featured 2025 Movies**\n\n"
                                    
                                    for i, movie in enumerate(movies_2025, 1):
                                        movie_info = self.format_movie_info(movie)
                                        result_text += f"**{i}.** {movie_info}\n\n"
                                    
                                    result_text += "💡 **Tip:** Visit the YTS.mx links to download movies."
                                    
                                    keyboard = [
                                        [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
                                        [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                                        [InlineKeyboardButton("❓ Help", callback_data="help")]
                                    ]
                                    reply_markup = InlineKeyboardMarkup(keyboard)
                                    
                                    await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                                else:
                                    await query.edit_message_text(
                                        "🆕 **No Featured 2025 Movies Found**\n\nNo 2025 movies are currently in the featured section.",
                                        parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=self.get_main_menu_keyboard()
                                    )
                            else:
                                await query.edit_message_text(
                                    "🆕 **No Featured 2025 Movies Found**\n\nNo 2025 movies are currently in the featured section.",
                                    parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=self.get_main_menu_keyboard()
                                )
                        else:
                            await query.edit_message_text(
                                "🆕 **No Featured 2025 Movies Found**\n\nNo 2025 movies are currently in the featured section.",
                                parse_mode=ParseMode.MARKDOWN,
                                reply_markup=self.get_main_menu_keyboard()
                            )
                    else:
                        await query.edit_message_text(
                            "❌ **Error loading featured movies**\n\nPlease try again later.",
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=self.get_main_menu_keyboard()
                        )
                        
        except Exception as e:
            logger.error(f"Error in handle_whats_new_button: {e}")
            await query.edit_message_text(
                "❌ **Error loading featured movies**\n\nPlease try again later.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_main_menu_keyboard()
            )

    async def handle_back_to_menu(self, query):
        """Handle back to menu button press"""
        welcome_message = """
🎬 **Movie Search Bot**

Welcome! I can search for movies on YTS.mx for you.

**Commands:**
• `/search <movie title>` - Search for a specific movie
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`

**Note:** This version shows movie information and YTS links only.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plain text messages as search queries"""
        try:
            query = update.message.text.strip()
            
            # Skip if it's a command
            if query.startswith('/'):
                return
            
            await self.perform_search(update, query)
            
        except Exception as e:
            logger.error(f"Error in handle_text_message: {e}")
            await update.message.reply_text("❌ Error processing your search. Please try again.")
            await self.show_main_menu_buttons(update.message)

    def format_movie_info(self, movie: dict) -> str:
        """Format movie information for display"""
        try:
            title = movie.get('title', 'Unknown Title')
            year = movie.get('year', 'Unknown Year')
            rating = movie.get('rating', 0)
            genres = ', '.join(movie.get('genres', []))
            yts_url = f"https://yts.mx/movies/{movie.get('slug', '')}"
            
            # Get Rotten Tomatoes rating if available
            rt_rating = ""
            if OMDB_API_KEY and movie.get('imdb_code'):
                # Note: We'll skip OMDB API calls for Railway compatibility
                pass
            
            info = f"**{title}** ({year})\n"
            info += f"⭐ IMDb: {rating}/10\n"
            if rt_rating:
                info += f"🍅 RT: {rt_rating}\n"
            if genres:
                info += f"🎭 Genres: {genres}\n"
            info += f"🔗 [View on YTS.mx]({yts_url})"
            
            return info
            
        except Exception as e:
            logger.error(f"Error formatting movie info: {e}")
            return f"**{movie.get('title', 'Unknown')}** - [View on YTS.mx](https://yts.mx)"

    def get_main_menu_keyboard(self):
        """Get main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def show_main_menu_buttons(self, message):
        """Show main menu buttons"""
        try:
            await message.reply_text(
                "Choose an option:",
                reply_markup=self.get_main_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"Error showing main menu: {e}")

    async def setup_handlers(self):
        """Set up bot handlers"""
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("search", self.search_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        return application

    async def run_bot(self):
        """Run the bot"""
        try:
            application = await self.setup_handlers()
            logger.info("Bot started successfully!")
            await application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Error running bot: {e}")

async def main():
    """Main function"""
    bot = MovieSearchBot()
    await bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main()) 