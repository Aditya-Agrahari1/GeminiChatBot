from telegram import Update
from telegram.ext import ContextTypes
from database.models import UserModel
from config import LOG_CHANNEL

class CommandHandler:
    def __init__(self):
        self.user_model = UserModel()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        user_name = user.full_name or "Unknown"

        existing_user = self.user_model.get_user(user_id)
        is_new_user = existing_user is None

        self.user_model.update_user(user_id, user_name)

        if is_new_user and LOG_CHANNEL:
            log_message = (
                f"#NewUser\n"
                f"👤 [User: {user_name}](tg://user?id={user_id})\n"
                f"🆔 ID: {user_id}"
            )
            try:
                await context.bot.send_message(
                    chat_id=LOG_CHANNEL,
                    text=log_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Failed to log new user: {str(e)}")

        welcome_message = (
            "Welcome! I'm your AI assistant. How can I help you today?" if is_new_user
            else "Welcome back! How can I assist you today?"
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "🤖 *Available Commands*\n\n"
            "/start - Start the bot\n"
            "/personality - Change bot's personality\n"
            "/clear - Clear chat history\n"
            "/help - Show this help message\n\n"
            "💡 *Tips*:\n"
            "• You can chat naturally with the bot\n"
            "• The bot remembers context from previous messages\n"
            "• Use /clear to start a fresh conversation"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')