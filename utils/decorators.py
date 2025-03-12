from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID, CHANNEL_USERNAME

def admin_required(func):
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("⚠️ This command is only available for administrators.")
            return
        return await func(self, update, context, *args, **kwargs)
    return wrapper

def subscription_required(func):
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not CHANNEL_USERNAME:
            return await func(self, update, context)
            
        try:
            # Check if update and user exist
            if not update or not update.effective_user:
                print("Warning: No valid user found in update")
                return
                
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id if update.effective_chat else None
            
            if not chat_id:
                print("Warning: No valid chat_id found")
                return
                
            member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return await func(self, update, context)
                
        except Exception as e:
            print(f"Failed to check subscription: {str(e)}")
            
        # Send subscription message only if we have a valid chat_id
        if chat_id:
            from handlers.personality import PersonalityHandler
            await PersonalityHandler.send_subscription_message(chat_id, context)
            
        return
    return wrapper