from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import UserModel
from utils.decorators import subscription_required

class PersonalityHandler:
    def __init__(self):
        self.user_model = UserModel()
        self.user_personalities = {}

    @subscription_required
    async def personality_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("🤗 Friendly", callback_data="personality_friendly"),
                InlineKeyboardButton("😎 Witty", callback_data="personality_witty"),
                InlineKeyboardButton("🧠 Expert", callback_data="personality_expert")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Choose my personality:\n"
            "🤗 Friendly - Warm and casual\n"
            "😎 Witty - Clever and sarcastic\n"
            "🧠 Expert - Professional and detailed",
            reply_markup=reply_markup
        )

    async def handle_personality_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        personality = query.data.split('_')[1]
        user_id = query.from_user.id
        
        self.user_model.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"personality": personality}},
            upsert=True
        )
        
        self.user_personalities[user_id] = personality
        
        personality_descriptions = {
            "friendly": "warm and friendly 🤗",
            "witty": "witty and sarcastic 😎",
            "expert": "professional and detailed 🧠"
        }
        
        await query.message.edit_text(
            f"I've switched to my {personality_descriptions[personality]} personality! How can I help you?"
        )

    async def send_subscription_message(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        from config import CHANNEL_USERNAME
        
        keyboard = [
            [
                InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}"),
                InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🚫 **Access Denied**\n"
            "You must join our channel to use this bot!\n\n"
            f"🔔 [Join Channel](https://t.me/{CHANNEL_USERNAME})\n"
            "After subscribing, click the \"Try Again\" button."
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )