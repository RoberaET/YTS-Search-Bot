import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# YTS API Configuration
YTS_API_BASE_URL = "https://yts.mx/api/v2"
YTS_SEARCH_URL = f"{YTS_API_BASE_URL}/list_movies.json"

# Bot Settings
MIN_RATING = 6.0
MAX_RESULTS = 10 