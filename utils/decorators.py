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
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not CHANNEL_USERNAME:
            return await func(self, update, context, *args, **kwargs)
            
        try:
            member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", update.effective_user.id)
            if member.status in ['member', 'administrator', 'creator']:
                return await func(self, update, context, *args, **kwargs)
        except Exception as e:
            print(f"Failed to check subscription: {str(e)}")
            
        await self.send_subscription_message(update.effective_chat.id, context)
        return None
    return wrapper