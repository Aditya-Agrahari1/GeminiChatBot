import google.generativeai as genai
from telegram import Update
from telegram.ext import ContextTypes
from config import GOOGLE_API_KEY, PERSONALITIES, GEMINI_CONFIG
from database.models import UserModel, MessageModel
from utils.decorators import subscription_required
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from urllib.parse import quote
# Change this line
from handlers.personality import PersonalityHandler  # Correct import path

class ChatHandler:
    def __init__(self, personality_handler=None):
        self.user_model = UserModel()
        self.message_model = MessageModel()
        self.personality_handler = personality_handler or PersonalityHandler()

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

    @subscription_required
    async def handle_generate_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Please provide a prompt after /gen command.\n\n e.g. /gen a cute cat")
            return

        try:
            chat_id = update.effective_chat.id
            await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
            
            prompt = ' '.join(context.args)
            api_url = "https://aiart-zroo.onrender.com/api/generate"
            
            # Prepare the request data according to API documentation
            data = {
                "video_description": prompt,
                "test_mode": False
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # Add request timeout and retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None, 
                        lambda: requests.post(api_url, json=data, headers=headers, timeout=60)
                    )
                    response.raise_for_status()
                    
                    # Extract image URL from response
                    result = response.json()
                    if 'error' in result:
                        raise ValueError(result['error'])
                    
                    image_url = result.get('image_url')
                    if not image_url:
                        raise ValueError("No image URL in response")
                        
                    # Download the generated image
                    img_response = await loop.run_in_executor(
                        None,
                        lambda: requests.get(image_url, timeout=10)
                    )
                    img_response.raise_for_status()
                    break
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(2)  # Longer delay between retries
                    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")

            # Send image immediately after successful download
            await update.message.reply_photo(photo=img_response.content)

        except requests.exceptions.Timeout:
            await update.message.reply_text("Image generation timed out. Please try again later.")
        except Exception as e:
            error_message = f"Image generation failed: {str(e)}"
            await update.message.reply_text(error_message)

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data='clear_yes')],
            [InlineKeyboardButton("No", callback_data='clear_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Are you sure you want to clear your chat history?",
            reply_markup=reply_markup
        )

    async def handle_clear_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == 'clear_yes':
            user_id = query.from_user.id
            self.message_model.db.messages.update_one(
                {"user_id": user_id},
                {"$set": {"conversation": []}}
            )
            await query.edit_message_text("Chat history cleared!")
        else:
            await query.edit_message_text("Chat history was not cleared.")
