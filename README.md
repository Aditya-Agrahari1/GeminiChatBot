# AI Telegram Bot

A Telegram bot powered by Google's Gemini AI with multiple personalities and admin features.

## Features

- 🤖 AI Chat with Context Memory
- 🎭 Multiple Bot Personalities
- 📊 Admin Statistics Dashboard
- 📢 Broadcast Messages
- 📝 Chat History Management
- 🔐 Channel Subscription Check
- 📋 Automatic User Activity Logging

Commands
- /start - Start the bot
- /personality - Change bot's personality
- /clear - Clear chat history
- /help - Show help message
Admin Commands:
- /broadcast - Send message to all users
- /stats - View bot statistics

## Setup

1. Clone the Repository:
git clone https://github.com/yourusername/GeminiBot.git
cd GeminiBot

2. Install Dependencies:
pip install -r requirements.txt

3. Create a `.env` file with your credentials:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GOOGLE_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_uri
ADMIN_ID=your_telegram_id
TELEGRAM_LOG_CHANNEL=your_log_channel_id
TELEGRAM_CHANNEL_USERNAME=your_channel_username
```
## Deployment on Koyeb

1. Fork this repository
2. Sign up for a [Koyeb account](https://app.koyeb.com)
3. Create a new app on Koyeb:
   - Choose "Deploy with Docker"
   - Connect your GitHub repository
   - Set environment variables:
     * `TELEGRAM_TOKEN`
     * `GOOGLE_API_KEY`
     * `MONGODB_URI`
     * `ADMIN_ID`
     * `TELEGRAM_LOG_CHANNEL`
     * `TELEGRAM_CHANNEL_USERNAME`
4. Deploy!
4. Set up the log channel:
- Create a new channel in Telegram
- Add your bot as an administrator
- Set TELEGRAM_LOG_CHANNEL in .env to the channel ID
- The bot will automatically log:
  - New user registrations
  - User activity statistics
  - Error reports
  - System notifications

5. Run the Bot:
python main.py