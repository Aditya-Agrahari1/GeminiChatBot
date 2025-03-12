# AI Telegram Bot

A powerful Telegram bot powered by Google's Gemini AI, featuring multiple personalities, admin controls, and user activity logging.

## 🚀 Features

- 🤖 **AI Chat with Context Memory:** Natural conversations with multi-turn context handling.
- 🎨 **AI Image Generation:** Create images from text prompts using Pollination.ai's models.
- 🎭 **Multiple Bot Personalities:** Switch between different conversational styles.
- 📊 **Admin Statistics Dashboard:** Track user activity, message counts, and real-time insights.
- 📢 **Broadcast Messages:** Send announcements to all users or specific segments.
- 📝 **Chat History Management:** Store conversations in MongoDB for persistence.
- 🔐 **Channel Subscription Check:** Force users to join a channel before using the bot, with a 'Join & Try Again' button.
- 📋 **Automatic User Activity Logging:** Log new user registrations (only once) and interactions.

## 🛠️ Commands

### User Commands
- `/start` - Start the bot and initiate a chat.
- `/personality` - Change the bot's personality.
- `/clear` - Clear the current chat history.
- `/gen <prompt>` - Generate custom images from text descriptions
- `/help` - Show available commands and their descriptions.

### Admin Commands
- `/broadcast` - Send a message to all users (or specific segments).
- `/stats` - View real-time bot statistics and user metrics.

## 🏗️ Setup Instructions

1. **Clone the Repository:**
```bash
git clone https://github.com/Aditya-Agrahari1/Gemini-Bot
cd GeminiChatBot
```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create a `.env` file with your credentials:**
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GOOGLE_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_uri
ADMIN_ID=your_telegram_id
TELEGRAM_LOG_CHANNEL=your_log_channel_id
TELEGRAM_CHANNEL_USERNAME=your_channel_username
```

4. **Set up the log channel:**
- Create a new channel in Telegram.
- Add your bot as an administrator.
- Set `TELEGRAM_LOG_CHANNEL` in `.env` to the channel ID.

The bot will automatically log:
- New user registrations (only once per user).
- User activity statistics and message counts.
- System notifications and error reports.

5. **Run the Bot:**
```bash
python main.py
```

## 📂 Project Structure
```
chat_bot/
├── .env
├── config.py
├── main.py
├── requirements.txt
├── app.py
├── handlers/
│   ├── __init__.py
│   ├── admin.py        # broadcast, stats commands
│   ├── chat.py         # message handling
│   ├── commands.py     # start, clear, help commands
│   └── personality.py  # personality related commands
├── database/
│   ├── __init__.py
│   ├── mongodb.py      # database connection
│   └── models.py       # database operations
├── utils/
│   ├── __init__.py
│   ├── decorators.py   # admin check, subscription check
│   └── helpers.py      # common utilities
└── README.md
```

## 🚀 Deployment on Koyeb

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

---

Built with ❤️ by **Aditya** using **Gemini API** and **MongoDB**. ✨


