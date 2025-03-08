import google.generativeai as genai
from telegram import Update
from telegram.ext import ContextTypes
from config import GOOGLE_API_KEY, PERSONALITIES, GEMINI_CONFIG
from database.models import UserModel, MessageModel
from utils.decorators import subscription_required
import asyncio

class ChatHandler:
    def __init__(self):
        self.user_model = UserModel()
        self.message_model = MessageModel()
        
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_CONFIG["model_name"],
            generation_config=GEMINI_CONFIG["generation_config"]
        )

    @subscription_required
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.user_model.update_user(user.id, user.full_name or "Unknown")
        
        user_id = update.message.from_user.id
        user_message = update.message.text
        self.message_model.store_message(user_id, user_message, is_bot=False)
        
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            history = self.message_model.get_chat_history(user_id)
            user_doc = self.user_model.get_user(user_id)
            personality = user_doc.get('personality', 'friendly') if user_doc else 'friendly'
            personality_prompt = PERSONALITIES[personality]
            
            prompt = f"""{personality_prompt}
Remember to maintain a {personality} tone throughout your response.

Previous messages:
{history}

Respond naturally to continue the conversation. If the user's message is brief or unclear, 
encourage them to share more while maintaining your {personality} character."""
            
            chat = self.model.start_chat(history=[])
            response = chat.send_message(prompt)
            response_text = response.text
            
            typing_delay = min(len(response_text) / 30, 5.0)
            await asyncio.sleep(typing_delay)
            
            self.message_model.store_message(user_id, response_text, is_bot=True)
            await update.message.reply_text(response_text)
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            await update.message.reply_text(error_message)

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        self.message_model.db.messages.update_one(
            {"user_id": user_id},
            {"$set": {"conversation": []}}
        )
        await update.message.reply_text("Chat history cleared!")