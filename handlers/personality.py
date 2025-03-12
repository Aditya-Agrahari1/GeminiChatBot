from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import UserModel
from utils.decorators import subscription_required

class PersonalityHandler:
    def __init__(self):
        self.user_model = UserModel()
        self.user_personalities = {}
        self.default_personality = "friendly"  # Set default personality
        print("Default personality set to:", self.default_personality)

    def get_user_personality(self, user_id: int) -> str:
        # First check in-memory cache
        if user_id in self.user_personalities:
            return self.user_personalities[user_id]
        
        # Then check database
        user = self.user_model.db.users.find_one({"user_id": user_id})
        if user and "personality" in user:
            self.user_personalities[user_id] = user["personality"]
            return user["personality"]
        
        # If no personality is set, return default
        print(f"New user {user_id} assigned default personality: {self.default_personality}")
        return self.default_personality

    @staticmethod
    async def send_subscription_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not chat_id:
                print("Warning: No chat_id provided for subscription message")
                return
                
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
        except Exception as e:
            print(f"Error sending subscription message: {e}")

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
        
        print(f"Changing personality to {personality} for user {user_id}")  # Added log
        
        self.user_model.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"personality": personality}},
            upsert=True
        )
        
        self.user_personalities[user_id] = personality
        print(f"Personality updated in memory: {self.user_personalities[user_id]}")  # Added log
        
        personality_descriptions = {
            "friendly": "warm and friendly 🤗",
            "witty": "witty and sarcastic 😎",
            "expert": "professional and detailed 🧠"
        }
        
        await query.message.edit_text(
            f"I've switched to my {personality_descriptions[personality]} personality! How can I help you?"
        )

    async def handle_subscription_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = query.from_user.id
            from config import CHANNEL_USERNAME
            
            member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
            if member.status in ['member', 'administrator', 'creator']:
                await query.message.edit_text("✅ Thank you for subscribing! You can now use the bot.")
                return True
            else:
                await query.answer("❌ You need to join the channel first!", show_alert=True)
                return False
                
        except Exception as e:
            print(f"Error checking subscription: {e}")
            await query.answer("❌ Something went wrong, please try again.", show_alert=True)
            return False
