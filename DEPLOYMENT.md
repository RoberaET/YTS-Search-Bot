# 🚀 Railway Deployment Guide

This guide will help you deploy your Movie Release Notifier bot on Railway.

## 📋 Prerequisites

1. **GitHub Account** - Your code should be on GitHub
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Telegram Bot Token** - Get from [@BotFather](https://t.me/BotFather)

## 🔧 Step 1: Prepare Your Repository

Your repository should now be clean and ready with these files:
- `search_bot.py` - Main bot file
- `requirements.txt` - Python dependencies
- `Procfile` - Railway process definition
- `runtime.txt` - Python version
- `railway.json` - Railway configuration
- `.gitignore` - Git ignore rules

## 🚀 Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Movie Release Notifier repository

3. **Configure Environment Variables**
   - Go to your project's "Variables" tab
   - Add these environment variables:

   ```
   BOT_TOKEN=your_telegram_bot_token_here
   CHAT_ID=your_chat_id_here (optional)
   OMDB_API_KEY=your_omdb_api_key_here (optional)
   ```

4. **Deploy**
   - Railway will automatically detect the Python project
   - It will install dependencies from `requirements.txt`
   - The bot will start using the `Procfile`

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Add Environment Variables**
   ```bash
   railway variables set BOT_TOKEN=your_bot_token_here
   railway variables set CHAT_ID=your_chat_id_here
   railway variables set OMDB_API_KEY=your_omdb_api_key_here
   ```

5. **Deploy**
   ```bash
   railway up
   ```

## 🔑 Step 3: Get Your Bot Token

1. **Message @BotFather on Telegram**
2. **Send `/newbot`**
3. **Follow the instructions to create your bot**
4. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 📱 Step 4: Test Your Bot

1. **Find your bot** on Telegram (using the username you created)
2. **Send `/start`** to test the bot
3. **Try searching for a movie** using `/search movie_name`
4. **Test the torrent download** feature

## 🔧 Step 5: Monitor Your Deployment

### Railway Dashboard
- **Logs**: View real-time logs in the Railway dashboard
- **Metrics**: Monitor CPU, memory usage
- **Deployments**: Track deployment history

### Common Issues & Solutions

1. **Bot not responding**
   - Check Railway logs for errors
   - Verify BOT_TOKEN is correct
   - Ensure the bot is running (check "Deployments" tab)

2. **Import errors**
   - Verify all dependencies are in `requirements.txt`
   - Check Railway logs for missing packages

3. **Environment variables not working**
   - Double-check variable names in Railway dashboard
   - Ensure no extra spaces in values

## 📊 Step 6: Scaling (Optional)

### Free Tier Limits
- **Monthly Usage**: 500 hours
- **Concurrent Requests**: Limited
- **Storage**: 1GB

### Upgrade for Production
- **Pro Plan**: $5/month for unlimited usage
- **Team Plan**: $20/month for team collaboration

## 🔄 Step 7: Continuous Deployment

Railway automatically deploys when you push to your GitHub repository:
1. **Make changes** to your code
2. **Commit and push** to GitHub
3. **Railway automatically redeploys** your bot

## 📝 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ Yes | Your Telegram bot token from @BotFather |
| `CHAT_ID` | ❌ No | Your Telegram chat ID (for notifications) |
| `OMDB_API_KEY` | ❌ No | OMDB API key for additional movie data |

## 🆘 Troubleshooting

### Bot Not Starting
```bash
# Check Railway logs
railway logs
```

### Dependencies Issues
```bash
# Verify requirements.txt
cat requirements.txt
```

### Environment Variables
```bash
# List all variables
railway variables
```

## 🎉 Success!

Once deployed, your bot will be available 24/7 on Railway's infrastructure. The bot will automatically restart if it crashes and will scale based on usage.

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Telegram Bot API**: [core.telegram.org/bots](https://core.telegram.org/bots)
- **GitHub Issues**: Create an issue in your repository 