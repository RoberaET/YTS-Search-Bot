# 🎬 Movie Torrent Finder Bot

A Telegram bot that finds high-quality movie torrents with IMDb ratings of 6.0 or higher using the YTS API.

## ✨ Features

- 🔍 Search movies by title
- ⭐ Only shows movies with IMDb rating ≥ 6.0
- 📥 Multiple quality options (4K, 1080p, 720p, 480p)
- 🌱 Shows seed/peer information
- 🔗 Direct magnet link downloads
- 🎯 Inline keyboard buttons for quick downloads
- 📱 User-friendly interface

## 🚀 Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (you'll need this later)

### 2. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Movie-Release-Notifier

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

1. Copy the example environment file:
```bash
cp env_example.txt .env
```

2. Edit `.env` and add your bot token:
```
BOT_TOKEN=your_actual_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## 📋 Requirements

- Python 3.8+
- `python-telegram-bot` library
- `requests` library
- `python-dotenv` library

## 🎯 Usage

### Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed help information
- `/search <movie>` - Search for a specific movie

### Examples

- Send "Inception" to search for the movie Inception
- Send "The Dark Knight" to search for Batman movies
- Use `/search Interstellar` to search for Interstellar

## 🚀 Deployment Options

### Option 1: Railway (Recommended)

1. **Fork this repository** to your GitHub account

2. **Sign up for Railway** at [railway.app](https://railway.app)

3. **Connect your GitHub repository**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your forked repository

4. **Set environment variables**:
   - Go to your project settings
   - Add environment variable: `BOT_TOKEN` = your bot token

5. **Deploy**:
   - Railway will automatically detect Python and install dependencies
   - The bot will start running

### Option 2: Replit

1. **Go to [replit.com](https://replit.com)** and create a new Python repl

2. **Upload all files** to your repl

3. **Set environment variables**:
   - Go to "Secrets" in the left sidebar
   - Add: `BOT_TOKEN` = your bot token

4. **Run the bot**:
   - Click "Run" button
   - The bot will start and stay running

### Option 3: Local Machine

1. **Install Python** if you haven't already

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment**:
```bash
# Windows
set BOT_TOKEN=your_bot_token_here

# Linux/Mac
export BOT_TOKEN=your_bot_token_here
```

4. **Run the bot**:
```bash
python bot.py
```

### Option 4: VPS/Server

1. **SSH into your server**

2. **Clone and setup**:
```bash
git clone <your-repo-url>
cd Movie-Release-Notifier
pip install -r requirements.txt
```

3. **Create .env file**:
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
```

4. **Run with screen/tmux** (to keep it running):
```bash
# Using screen
screen -S moviebot
python bot.py
# Press Ctrl+A, then D to detach

# Using tmux
tmux new-session -d -s moviebot 'python bot.py'
```

## 🔧 Configuration

You can customize the bot by modifying `config.py`:

- `MIN_RATING`: Minimum IMDb rating (default: 6.0)
- `MAX_RESULTS`: Maximum number of results to show (default: 10)

## 📁 Project Structure

```
Movie-Release-Notifier/
├── bot.py              # Main bot file
├── yts_api.py          # YTS API integration
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables example
└── README.md          # This file
```

## 🔍 How It Works

1. **User Input**: User sends a movie title
2. **API Query**: Bot queries YTS API for movies
3. **Filtering**: Only movies with rating ≥ 6.0 are shown
4. **Formatting**: Results are formatted with movie info and torrent links
5. **Response**: Bot sends formatted results with download buttons

## 🛡️ Legal Notice

This bot uses the YTS API to find legitimate torrent sources. Users are responsible for ensuring they comply with local laws regarding torrent downloads.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues:

1. Check that your bot token is correct
2. Ensure all dependencies are installed
3. Verify your internet connection
4. Check the logs for error messages

For additional help, please open an issue on GitHub. 