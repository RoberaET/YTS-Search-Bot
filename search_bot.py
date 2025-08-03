#!/usr/bin/env python3
"""
Movie Search Bot for Telegram
Allows users to search for specific movies on YTS.mx
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
• `/torrent` - Get torrent files for the last searched movie(s)
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`
        """
        
        # Create inline keyboard buttons
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
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
• `/torrent` - Get torrent files for the last searched movie(s)
• `/torrent_all` - Get torrents for ALL movies from last search
• `/torrent_1`, `/torrent_2`, etc. - Get torrents for specific movie
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`
• `/torrent` (after searching)

**What you'll get:**
• Movie poster image
• IMDb rating
• Rotten Tomatoes rating (if available)
• Download links
• Movie details
• Torrent files (720p & 1080p)

**Multiple Movies:**
If your search returns multiple movies, use:
• `/torrent_all` - Get torrents for all movies
• `/torrent_1` - Get torrents for first movie
• `/torrent_2` - Get torrents for second movie
• etc.

**🆕 What's New Feature:**
• Shows featured 2025 movies from YTS.mx using website filters
• Filtered by: Year 2025, Rating 6+, All genres, All qualities
• Sorted by Featured (like website homepage)
• Use the "What's New?" button to see the featured 2025 movies
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command - search for a movie"""
        query = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Searching for: **{query}**...", parse_mode=ParseMode.MARKDOWN)
        try:
            # Search for the movie
            movies = await self.search_movies(query)
            if not movies:
                await update.message.reply_text(f"❌ No movies found for: **{query}**", parse_mode=ParseMode.MARKDOWN)
                try:
                    await self.show_main_menu_buttons(update.message)
                except Exception as e:
                    logger.error(f"Error showing main menu buttons: {e}")
                    # Fallback: send a simple message with buttons
                    try:
                        keyboard = [
                            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
                            [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
                            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                            [InlineKeyboardButton("❓ Help", callback_data="help")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text("🎬 **Main Menu**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                    except Exception as e2:
                        logger.error(f"Fallback button error: {e2}")
                return
            # Send results
            for i, movie in enumerate(movies[:3], 1):  # Limit to 3 results
                notification = self.format_movie_info(movie)
                poster_url = movie.get('large_cover_image') or movie.get('medium_cover_image')
                if poster_url:
                    try:
                        await self.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=poster_url,
                            caption=notification,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        await update.message.reply_text(notification, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(notification, parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(1)  # Small delay between messages
            if len(movies) > 3:
                await update.message.reply_text(f"📋 Showing first 3 results. Found {len(movies)} total movies for: **{query}**", parse_mode=ParseMode.MARKDOWN)
            # Store the search results for this user
            user_id = update.effective_user.id
            self.last_search_results[user_id] = movies[:3]  # Store first 3 results
        except Exception as e:
            logger.error(f"Error in search: {e}")
            await update.message.reply_text(f"❌ Error searching for: **{query}**\n\nPlease try again later.", parse_mode=ParseMode.MARKDOWN)
        finally:
            # Always show main menu buttons at the end, even if there was an error
            try:
                await self.show_main_menu_buttons(update.message)
            except Exception as e:
                logger.error(f"Error showing main menu buttons: {e}")
                # Fallback: send a simple message with buttons
                try:
                    keyboard = [
                        [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
                        [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
                        [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                        [InlineKeyboardButton("❓ Help", callback_data="help")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("🎬 **Main Menu**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                except Exception as e2:
                    logger.error(f"Fallback button error: {e2}")
    
    async def search_movies(self, query: str):
        """Search for movies by title"""
        try:
            params = {
                'query_term': query,
                'limit': 20,
                'sort_by': 'date_added',
                'order_by': 'desc'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(YTS_SEARCH_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        movies = data.get('data', {}).get('movies', [])
                        return movies
                    else:
                        logger.error(f"Search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return []
    
    async def torrent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /torrent command - send torrent files for last searched movies"""
        user_id = update.effective_user.id
        
        if user_id not in self.last_search_results or not self.last_search_results[user_id]:
            await update.message.reply_text("❌ No recent search found. Please search for a movie first using `/search <movie title>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        movies = self.last_search_results[user_id]
        
        # If only one movie, send torrents for it
        if len(movies) == 1:
            movie = movies[0]
            title = movie.get('title', 'Unknown')
            await update.message.reply_text(f"📥 Getting torrent files for: **{title}**...", parse_mode=ParseMode.MARKDOWN)
            await self.send_torrents_for_movie(update, movie)
        else:
            # Multiple movies - show options
            await self.show_torrent_options(update, movies)
    
    async def show_torrent_options(self, update: Update, movies: list):
        """Show options for multiple movies"""
        options_message = "📋 **Multiple movies found in last search:**\n\n"
        
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'Unknown')
            rating = movie.get('rating', 0)
            options_message += f"{i}. **{title}** ({year}) - ⭐ {rating}/10\n"
        
        options_message += "\n**Commands:**\n"
        options_message += "• `/torrent_all` - Get torrents for ALL movies\n"
        options_message += "• `/torrent_1`, `/torrent_2`, etc. - Get torrents for specific movie\n"
        
        await update.message.reply_text(options_message, parse_mode=ParseMode.MARKDOWN)
    
    async def torrent_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /torrent_all command - send torrent files for all movies from last search"""
        user_id = update.effective_user.id
        
        if user_id not in self.last_search_results or not self.last_search_results[user_id]:
            await update.message.reply_text("❌ No recent search found. Please search for a movie first using `/search <movie title>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        movies = self.last_search_results[user_id]
        await update.message.reply_text(f"📥 Getting torrent files for **{len(movies)} movies**...", parse_mode=ParseMode.MARKDOWN)
        
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'Unknown')
            await update.message.reply_text(f"📥 **{i}/{len(movies)}** - Getting torrents for: **{title}**...", parse_mode=ParseMode.MARKDOWN)
            await self.send_torrents_for_movie(update, movie)
            await asyncio.sleep(1)  # Small delay between movies
        
        # Show main menu buttons after sending all torrents
        await self.show_main_menu_buttons(update.message)
    
    async def torrent_specific_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /torrent_X command - send torrent files for specific movie"""
        user_id = update.effective_user.id
        
        if user_id not in self.last_search_results or not self.last_search_results[user_id]:
            await update.message.reply_text("❌ No recent search found. Please search for a movie first using `/search <movie title>`", parse_mode=ParseMode.MARKDOWN)
            return
        
        # Extract number from command (e.g., /torrent_1 -> 1)
        command = update.message.text
        try:
            movie_index = int(command.split('_')[1]) - 1  # Convert to 0-based index
        except (IndexError, ValueError):
            await update.message.reply_text("❌ Invalid command. Use `/torrent_1`, `/torrent_2`, etc.", parse_mode=ParseMode.MARKDOWN)
            return
        
        movies = self.last_search_results[user_id]
        if movie_index < 0 or movie_index >= len(movies):
            await update.message.reply_text(f"❌ Invalid movie number. Available: 1-{len(movies)}", parse_mode=ParseMode.MARKDOWN)
            return
        
        movie = movies[movie_index]
        title = movie.get('title', 'Unknown')
        await update.message.reply_text(f"📥 Getting torrent files for: **{title}**...", parse_mode=ParseMode.MARKDOWN)
        await self.send_torrents_for_movie(update, movie)
        
        # Show main menu buttons after sending torrents
        await self.show_main_menu_buttons(update.message)
    
    async def send_torrents_for_movie(self, update: Update, movie: dict):
        """Send torrent files for a specific movie"""
        title = movie.get('title', 'Unknown')
        
        try:
            torrents = movie.get('torrents', [])
            if not torrents:
                await update.message.reply_text(f"❌ No torrents available for **{title}**", parse_mode=ParseMode.MARKDOWN)
                return
            
            # Find 720p and 1080p torrents
            torrent_720p = None
            torrent_1080p = None
            
            for torrent in torrents:
                quality = torrent.get('quality', '').lower()
                if '720p' in quality or '720' in quality:
                    torrent_720p = torrent
                elif '1080p' in quality or '1080' in quality:
                    torrent_1080p = torrent
            
            # Send 720p torrent if available
            if torrent_720p:
                try:
                    torrent_url = torrent_720p.get('url')
                    if torrent_url:
                        # Download the torrent file first
                        torrent_content = await self.download_torrent_file(torrent_url)
                        if torrent_content:
                            # Create a temporary file
                            import tempfile
                            import os
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.torrent') as temp_file:
                                temp_file.write(torrent_content)
                                temp_file_path = temp_file.name
                            
                            try:
                                # Send the local file
                                with open(temp_file_path, 'rb') as file:
                                    await self.bot.send_document(
                                        chat_id=update.effective_chat.id,
                                        document=file,
                                        filename=f"{title} - 720p.torrent",
                                        caption=f"🎬 **{title}** - 720p Quality\n📁 Size: {torrent_720p.get('size', 'Unknown')}\n🌱 Seeds: {torrent_720p.get('seeds', 0)}"
                                    )
                                logger.info(f"Sent 720p torrent for: {title}")
                            finally:
                                # Clean up temporary file
                                try:
                                    os.unlink(temp_file_path)
                                except:
                                    pass
                        else:
                            await update.message.reply_text(f"❌ Failed to download 720p torrent for **{title}**", parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text(f"❌ 720p torrent URL not available for **{title}**", parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    logger.error(f"Error sending 720p torrent: {e}")
                    await update.message.reply_text(f"❌ Error sending 720p torrent for **{title}**", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"❌ 720p torrent not available for **{title}**", parse_mode=ParseMode.MARKDOWN)
            
            # Send 1080p torrent if available
            if torrent_1080p:
                try:
                    torrent_url = torrent_1080p.get('url')
                    if torrent_url:
                        # Download the torrent file first
                        torrent_content = await self.download_torrent_file(torrent_url)
                        if torrent_content:
                            # Create a temporary file
                            import tempfile
                            import os
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.torrent') as temp_file:
                                temp_file.write(torrent_content)
                                temp_file_path = temp_file.name
                            
                            try:
                                # Send the local file
                                with open(temp_file_path, 'rb') as file:
                                    await self.bot.send_document(
                                        chat_id=update.effective_chat.id,
                                        document=file,
                                        filename=f"{title} - 1080p.torrent",
                                        caption=f"🎬 **{title}** - 1080p Quality\n📁 Size: {torrent_1080p.get('size', 'Unknown')}\n🌱 Seeds: {torrent_1080p.get('seeds', 0)}"
                                    )
                                logger.info(f"Sent 1080p torrent for: {title}")
                            finally:
                                # Clean up temporary file
                                try:
                                    os.unlink(temp_file_path)
                                except:
                                    pass
                        else:
                            await update.message.reply_text(f"❌ Failed to download 1080p torrent for **{title}**", parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text(f"❌ 1080p torrent URL not available for **{title}**", parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    logger.error(f"Error sending 1080p torrent: {e}")
                    await update.message.reply_text(f"❌ Error sending 1080p torrent for **{title}**", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"❌ 1080p torrent not available for **{title}**", parse_mode=ParseMode.MARKDOWN)
            
            # If neither quality is available, show available qualities
            if not torrent_720p and not torrent_1080p:
                available_qualities = [t.get('quality', 'Unknown') for t in torrents]
                await update.message.reply_text(
                    f"❌ 720p and 1080p not available for **{title}**\n\nAvailable qualities: {', '.join(available_qualities)}",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Show main menu buttons after sending torrents - send as NEW message
            menu_message = f"✅ **Torrent files sent for: {title}**\n\n📥 Check the files above!"
            reply_markup = self.get_main_menu_keyboard()
            
            await update.message.reply_text(menu_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in torrent command: {e}")
            await update.message.reply_text(f"❌ Error getting torrent files for **{title}**\n\nPlease try again later.", parse_mode=ParseMode.MARKDOWN)
    
    async def download_torrent_file(self, url: str) -> bytes:
        """Download torrent file content from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Failed to download torrent file: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading torrent file: {e}")
            return None
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()  # Answer the callback query
        
        if query.data == "search_movies":
            await self.handle_search_button(query)
        elif query.data == "get_torrents":
            await self.handle_torrent_button(query)
        elif query.data == "help":
            await self.handle_help_button(query)
        elif query.data == "whats_new":
            await self.handle_whats_new_button(query)
        elif query.data.startswith("torrent_"):
            if query.data == "torrent_all":
                await self.handle_torrent_all_button(query)
            else:
                await self.handle_torrent_specific_button(query)
        elif query.data == "back_to_menu":
            await self.handle_back_to_menu(query)
    
    async def handle_search_button(self, query):
        """Handle search button press"""
        message = """
🔍 **Search Movies**

Please type your search query in the format:
`/search <movie title>`

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`
• `/search Captain America`

I'll search YTS.mx and show you movie details with posters!
        """
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_torrent_button(self, query):
        """Handle torrent button press"""
        user_id = query.from_user.id
        
        if user_id not in self.last_search_results or not self.last_search_results[user_id]:
            message = """
📥 **Get Torrents**

❌ No recent search found!

Please search for a movie first using:
`/search <movie title>`

**Example:** `/search deadpool`


            """
            keyboard = [
                [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
                [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
                [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                [InlineKeyboardButton("❓ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        movies = self.last_search_results[user_id]
        
        if len(movies) == 1:
            # Single movie - send torrents directly
            movie = movies[0]
            title = movie.get('title', 'Unknown')
            await query.edit_message_text(f"📥 Getting torrent files for: **{title}**...", parse_mode=ParseMode.MARKDOWN)
            await self.send_torrents_for_movie_callback(query, movie)
        else:
            # Multiple movies - show options
            await self.show_torrent_options_callback(query, movies)
    
    async def handle_help_button(self, query):
        """Handle help button press"""
        help_message = """
🎬 **Movie Search Bot Help**

**Commands:**
• `/search <movie title>` - Search for a specific movie on YTS
• `/torrent` - Get torrent files for the last searched movie(s)
• `/torrent_all` - Get torrents for ALL movies from last search
• `/torrent_1`, `/torrent_2`, etc. - Get torrents for specific movie
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`
• `/torrent` (after searching)

**What you'll get:**
• Movie poster image
• IMDb rating
• Rotten Tomatoes rating (if available)
• Download links
• Movie details
• Torrent files (720p & 1080p)

**Multiple Movies:**
If your search returns multiple movies, use:
• `/torrent_all` - Get torrents for all movies
• `/torrent_1` - Get torrents for first movie
• `/torrent_2` - Get torrents for second movie
• etc.
        """
        await query.edit_message_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_whats_new_button(self, query):
        """Handle What's New button press - show featured 2025 movies from homepage"""
        await query.edit_message_text("🆕 **Checking Featured 2025 Movies...**\n\n⏳ Please wait while I fetch the featured 2025 movies from YTS.mx using website filters...", parse_mode=ParseMode.MARKDOWN, reply_markup=self.get_main_menu_keyboard())
        
        try:
            # Fetch 2025 movies using exact website filtering parameters
            async with aiohttp.ClientSession() as session:
                url = "https://yts.mx/api/v2/list_movies.json"
                params = {
                    'limit': 200,  # Get more movies to filter from
                    'sort_by': 'featured',  # Order By: Featured (from website)
                    'order_by': 'desc',
                    'quality': 'all',  # Quality: All
                    'genre': 'all',  # Genre: All
                    'minimum_rating': '6',  # Rating: 6+
                    'year': '2025',  # Year: 2025
                    'language': 'all'  # Language: All
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        movies = data.get('data', {}).get('movies', [])
                    else:
                        await query.edit_message_text("❌ **Error fetching 2025 movies**\n\nUnable to connect to YTS.mx. Please try again later.", parse_mode=ParseMode.MARKDOWN, reply_markup=self.get_main_menu_keyboard())
                        return
            
            if not movies:
                await query.edit_message_text("❌ **No movies found**\n\nUnable to fetch movies from YTS.mx.", parse_mode=ParseMode.MARKDOWN, reply_markup=self.get_main_menu_keyboard())
                return
            
            # Filter for 2025 movies only
            movies_2025 = []
            for movie in movies:
                year = movie.get('year', 0)
                if year == 2025:
                    movies_2025.append(movie)
            
            if not movies_2025:
                await query.edit_message_text("🆕 **No 2025 Movies Found**\n\nNo 2025 movies are currently available on YTS.mx.\n\nCheck back later for new releases!", parse_mode=ParseMode.MARKDOWN, reply_markup=self.get_main_menu_keyboard())
                return
            
            # Limit to top 10 2025 movies
            latest_2025_movies = movies_2025[:10]
            
            # Create the message
            message = f"🔥 **Featured 2025 Movies**\n\nFound **{len(latest_2025_movies)}** 2025 movies on YTS.mx (Rating 6+):\n\n"
            
            for i, movie in enumerate(latest_2025_movies, 1):
                title = movie.get('title', 'Unknown')
                year = movie.get('year', 'Unknown')
                rating = movie.get('rating', 0)
                genres = ', '.join(movie.get('genres', [])[:3])  # First 3 genres
                date_added = movie.get('date_uploaded', 'Unknown')
                
                # Format the date
                try:
                    if date_added != 'Unknown':
                        from datetime import datetime
                        date_obj = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime('%b %d')
                    else:
                        formatted_date = "Unknown"
                except:
                    formatted_date = "Unknown"
                
                message += f"**{i}.** **{title}** ({year}) - ⭐ {rating}/10\n"
                message += f"    🎭 {genres}\n"
                message += f"    📅 Added: {formatted_date}\n\n"
            
            message += "💡 **Tip:** Use the Search button to find specific movies and get their torrent files!"
            
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=self.get_main_menu_keyboard())
            
        except Exception as e:
            logger.error(f"Error in What's New feature: {e}")
            await query.edit_message_text("❌ **Error fetching 2025 movies**\n\nSomething went wrong while checking for 2025 movies. Please try again later.", parse_mode=ParseMode.MARKDOWN, reply_markup=self.get_main_menu_keyboard())
    
    async def handle_torrent_specific_button(self, query):
        """Handle specific torrent button press (torrent_1, torrent_2, etc.)"""
        user_id = query.from_user.id
        
        if user_id not in self.last_search_results or not self.last_search_results[user_id]:
            error_message = "❌ No recent search found!"
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        # Extract number from callback data (e.g., torrent_1 -> 1)
        try:
            movie_index = int(query.data.split('_')[1]) - 1  # Convert to 0-based index
        except (IndexError, ValueError):
            error_message = "❌ Invalid torrent selection!"
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        movies = self.last_search_results[user_id]
        if movie_index < 0 or movie_index >= len(movies):
            error_message = f"❌ Invalid movie number. Available: 1-{len(movies)}"
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        movie = movies[movie_index]
        title = movie.get('title', 'Unknown')
        await query.edit_message_text(f"📥 Getting torrent files for: **{title}**...", parse_mode=ParseMode.MARKDOWN)
        await self.send_torrents_for_movie_callback(query, movie)
    
    async def show_torrent_options_callback(self, query, movies: list):
        """Show torrent options for multiple movies via callback"""
        options_message = "📋 **Multiple movies found in last search:**\n\n"
        
        keyboard = []
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'Unknown')
            rating = movie.get('rating', 0)
            options_message += f"{i}. **{title}** ({year}) - ⭐ {rating}/10\n"
            keyboard.append([InlineKeyboardButton(f"📥 {title}", callback_data=f"torrent_{i}")])
        
        keyboard.append([InlineKeyboardButton("📥 Get ALL Torrents", callback_data="torrent_all")])
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(options_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    async def send_torrents_for_movie_callback(self, query, movie: dict):
        """Send torrent files for a specific movie via callback"""
        title = movie.get('title', 'Unknown')
        
        try:
            torrents = movie.get('torrents', [])
            if not torrents:
                # Show error with persistent buttons
                error_message = f"❌ No torrents available for **{title}**"
                reply_markup = self.get_main_menu_keyboard()
                await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                return
            
            # Find 720p and 1080p torrents
            torrent_720p = None
            torrent_1080p = None
            
            for torrent in torrents:
                quality = torrent.get('quality', '').lower()
                if '720p' in quality or '720' in quality:
                    torrent_720p = torrent
                elif '1080p' in quality or '1080' in quality:
                    torrent_1080p = torrent
            
            # Update status with persistent buttons
            status_message = f"📥 **Downloading torrents for: {title}**\n\n⏳ Please wait while I download the torrent files..."
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(status_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
            # Send 720p torrent if available
            if torrent_720p:
                try:
                    torrent_url = torrent_720p.get('url')
                    if torrent_url:
                        torrent_content = await self.download_torrent_file(torrent_url)
                        if torrent_content:
                            import tempfile
                            import os
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.torrent') as temp_file:
                                temp_file.write(torrent_content)
                                temp_file_path = temp_file.name
                            
                            try:
                                with open(temp_file_path, 'rb') as file:
                                    await self.bot.send_document(
                                        chat_id=query.message.chat_id,
                                        document=file,
                                        filename=f"{title} - 720p.torrent",
                                        caption=f"🎬 **{title}** - 720p Quality\n📁 Size: {torrent_720p.get('size', 'Unknown')}\n🌱 Seeds: {torrent_720p.get('seeds', 0)}"
                                    )
                                logger.info(f"Sent 720p torrent for: {title}")
                            finally:
                                try:
                                    os.unlink(temp_file_path)
                                except:
                                    pass
                        else:
                            # Show error with persistent buttons
                            error_message = f"❌ Failed to download 720p torrent for **{title}**"
                            reply_markup = self.get_main_menu_keyboard()
                            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                            return
                    else:
                        # Show error with persistent buttons
                        error_message = f"❌ 720p torrent URL not available for **{title}**"
                        reply_markup = self.get_main_menu_keyboard()
                        await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                        return
                except Exception as e:
                    logger.error(f"Error sending 720p torrent: {e}")
                    # Show error with persistent buttons
                    error_message = f"❌ Error sending 720p torrent for **{title}**"
                    reply_markup = self.get_main_menu_keyboard()
                    await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                    return
            else:
                # Show error with persistent buttons
                error_message = f"❌ 720p torrent not available for **{title}**"
                reply_markup = self.get_main_menu_keyboard()
                await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                return
            
            # Send 1080p torrent if available
            if torrent_1080p:
                try:
                    torrent_url = torrent_1080p.get('url')
                    if torrent_url:
                        torrent_content = await self.download_torrent_file(torrent_url)
                        if torrent_content:
                            import tempfile
                            import os
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.torrent') as temp_file:
                                temp_file.write(torrent_content)
                                temp_file_path = temp_file.name
                            
                            try:
                                with open(temp_file_path, 'rb') as file:
                                    await self.bot.send_document(
                                        chat_id=query.message.chat_id,
                                        document=file,
                                        filename=f"{title} - 1080p.torrent",
                                        caption=f"🎬 **{title}** - 1080p Quality\n📁 Size: {torrent_1080p.get('size', 'Unknown')}\n🌱 Seeds: {torrent_1080p.get('seeds', 0)}"
                                    )
                                logger.info(f"Sent 1080p torrent for: {title}")
                            finally:
                                try:
                                    os.unlink(temp_file_path)
                                except:
                                    pass
                        else:
                            # Show error with persistent buttons
                            error_message = f"❌ Failed to download 1080p torrent for **{title}**"
                            reply_markup = self.get_main_menu_keyboard()
                            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                            return
                    else:
                        # Show error with persistent buttons
                        error_message = f"❌ 1080p torrent URL not available for **{title}**"
                        reply_markup = self.get_main_menu_keyboard()
                        await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                        return
                except Exception as e:
                    logger.error(f"Error sending 1080p torrent: {e}")
                    # Show error with persistent buttons
                    error_message = f"❌ Error sending 1080p torrent for **{title}**"
                    reply_markup = self.get_main_menu_keyboard()
                    await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                    return
            else:
                # Show error with persistent buttons
                error_message = f"❌ 1080p torrent not available for **{title}**"
                reply_markup = self.get_main_menu_keyboard()
                await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                return
            
            # Success message with main menu buttons - send as NEW message
            menu_message = f"✅ **Torrent files sent for: {title}**\n\n📥 Check the files above!"
            reply_markup = self.get_main_menu_keyboard()
            
            logger.info(f"Showing main menu buttons after sending torrents for: {title}")
            # Send as a NEW message instead of editing the existing one
            await self.bot.send_message(
                chat_id=query.message.chat_id,
                text=menu_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in torrent callback: {e}")
            # Show error with persistent buttons
            error_message = f"❌ Error getting torrent files for **{title}**\n\nPlease try again later."
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    async def handle_torrent_all_button(self, query):
        """Handle torrent_all button press"""
        user_id = query.from_user.id
        
        if user_id not in self.last_search_results or not self.last_search_results[user_id]:
            # Show error with persistent buttons
            error_message = "❌ No recent search found!"
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        movies = self.last_search_results[user_id]
        
        # Show initial status with persistent buttons
        status_message = f"📥 **Getting torrent files for {len(movies)} movies**\n\n⏳ Please wait while I download all torrent files..."
        reply_markup = self.get_main_menu_keyboard()
        await query.edit_message_text(status_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'Unknown')
            
            # Update status with persistent buttons
            progress_message = f"📥 **{i}/{len(movies)}** - Getting torrents for: **{title}**\n\n⏳ Please wait while I download the torrent files..."
            reply_markup = self.get_main_menu_keyboard()
            await query.edit_message_text(progress_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
            await self.send_torrents_for_movie_callback(query, movie)
            await asyncio.sleep(1)  # Small delay between movies
        
        # Final message with main menu buttons - send as NEW message
        final_message = f"✅ **All torrent files sent for {len(movies)} movies!**\n\n📥 Check the files above!"
        reply_markup = self.get_main_menu_keyboard()
        
        # Send as a NEW message instead of editing the existing one
        await self.bot.send_message(
            chat_id=query.message.chat_id,
            text=final_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def get_main_menu_keyboard(self):
        """Get the main menu keyboard markup"""
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def show_main_menu_buttons(self, message):
        """Show main menu buttons after any action"""
        reply_markup = self.get_main_menu_keyboard()
        await message.reply_text("🎬 **Main Menu**\n\nUse the buttons below to interact with me:", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_back_to_menu(self, query):
        """Handle back to menu button press"""
        welcome_message = """
🎬 **Movie Search Bot**

Welcome! I can search for movies on YTS.mx for you.

**Commands:**
• `/search <movie title>` - Search for a specific movie
• `/torrent` - Get torrent files for the last searched movie(s)
• `/help` - Show this help message

**Examples:**
• `/search 28 Years Later`
• `/search Deadpool 3`
• `/search The Batman`
        """
        
        # Create inline keyboard buttons
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
            [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plain text messages as search queries"""
        query = update.message.text.strip()
        if not query:
            await update.message.reply_text("❌ Please provide a movie title to search for.", parse_mode=ParseMode.MARKDOWN)
            await self.show_main_menu_buttons(update.message)
            return
        await update.message.reply_text(f"🔍 Searching for: **{query}**...", parse_mode=ParseMode.MARKDOWN)
        try:
            # Search for the movie
            movies = await self.search_movies(query)
            if not movies:
                await update.message.reply_text(f"❌ No movies found for: **{query}**", parse_mode=ParseMode.MARKDOWN)
                try:
                    await self.show_main_menu_buttons(update.message)
                except Exception as e:
                    logger.error(f"Error showing main menu buttons: {e}")
                    # Fallback: send a simple message with buttons
                    try:
                        keyboard = [
                            [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
                            [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
                            [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                            [InlineKeyboardButton("❓ Help", callback_data="help")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text("🎬 **Main Menu**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                    except Exception as e2:
                        logger.error(f"Fallback button error: {e2}")
                return
            # Send results
            for i, movie in enumerate(movies[:3], 1):  # Limit to 3 results
                notification = self.format_movie_info(movie)
                poster_url = movie.get('large_cover_image') or movie.get('medium_cover_image')
                if poster_url:
                    try:
                        await self.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=poster_url,
                            caption=notification,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        await update.message.reply_text(notification, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(notification, parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(1)  # Small delay between messages
            if len(movies) > 3:
                await update.message.reply_text(f"📋 Showing first 3 results. Found {len(movies)} total movies for: **{query}**", parse_mode=ParseMode.MARKDOWN)
            # Store the search results for this user
            user_id = update.effective_user.id
            self.last_search_results[user_id] = movies[:3]  # Store first 3 results
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            await update.message.reply_text(f"❌ Error searching for: **{query}**\n\nPlease try again later.", parse_mode=ParseMode.MARKDOWN)
        finally:
            # Always show main menu buttons at the end, even if there was an error
            try:
                await self.show_main_menu_buttons(update.message)
            except Exception as e:
                logger.error(f"Error showing main menu buttons: {e}")
                # Fallback: send a simple message with buttons
                try:
                    keyboard = [
                        [InlineKeyboardButton("🔍 Search Movies", callback_data="search_movies")],
                        [InlineKeyboardButton("📥 Get Torrents", callback_data="get_torrents")],
                        [InlineKeyboardButton("🆕 What's New?", callback_data="whats_new")],
                        [InlineKeyboardButton("❓ Help", callback_data="help")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("🎬 **Main Menu**", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                except Exception as e2:
                    logger.error(f"Fallback button error: {e2}")
    
    def format_movie_info(self, movie: dict) -> str:
        """Format movie information for display"""
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 0)
        genres = ', '.join(movie.get('genres', []))
        date_added = movie.get('date_uploaded', 'Unknown')
        
        # Format date
        try:
            if date_added != 'Unknown':
                from datetime import datetime
                date_obj = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%B %d, %Y')
            else:
                formatted_date = "Unknown"
        except:
            formatted_date = date_added
        
        # Start building notification
        notification = f"🎬 **{title}** ({year})\n"
        notification += f"⭐ **IMDb Rating:** {rating}/10\n"
        notification += f"🎭 **Genres:** {genres}\n"
        notification += f"📅 **Added to YTS:** {formatted_date}\n"
        
        # Add torrent information
        notification += "\n📥 **Available Qualities:**\n"
        torrents = movie.get('torrents', [])
        
        if torrents:
            for i, torrent in enumerate(torrents[:3], 1):  # Show first 3 qualities
                quality = torrent.get('quality', 'Unknown')
                size = torrent.get('size', 'Unknown')
                seeds = torrent.get('seeds', 0)
                
                seed_emoji = "🌱" if seeds > 0 else "❌"
                notification += f"{i}. **{quality}** - {size} ({seed_emoji} {seeds} seeds)\n"
        else:
            notification += "No torrents available yet\n"
        
        notification += f"\n🔗 **YTS Link:** https://yts.mx/movies/{movie.get('slug', '')}"
        notification += f"\n\n🖼️ **Movie poster included above**"
        
        return notification
    
    async def setup_handlers(self):
        """Setup command handlers"""
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("torrent", self.torrent_command))
        self.application.add_handler(CommandHandler("torrent_all", self.torrent_all_command))
        
        # Add handlers for specific torrent commands (torrent_1, torrent_2, etc.)
        for i in range(1, 11):  # Support up to 10 movies
            self.application.add_handler(CommandHandler(f"torrent_{i}", self.torrent_specific_command))
        
        # Add callback query handler for buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Add message handler for plain text messages (treat as search queries)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        logger.info("Command handlers setup complete")
    
    async def run_bot(self):
        """Run the search bot"""
        await self.setup_handlers()
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Movie Search Bot started successfully!")
        
        # Keep the bot running
        try:
            await self.application.updater.idle()
        except AttributeError:
            # Fallback for older versions
            while True:
                await asyncio.sleep(1)

async def main():
    """Main function"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    bot = MovieSearchBot()
    await bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main()) 