from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from handlers.admin import AdminHandler
from handlers.chat import ChatHandler
from handlers.commands import CommandHandler as BotCommandHandler
from handlers.personality import PersonalityHandler
from config import TELEGRAM_TOKEN, ADMIN_ID
import asyncio
import os
from telegram import Update

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Initialize handlers
        self.personality_handler = PersonalityHandler()  # Create once
        self.admin_handler = AdminHandler()
        self.chat_handler = ChatHandler(personality_handler=self.personality_handler)  # Pass the instance
        self.command_handler = BotCommandHandler()
        
        # Add error handler
        self.app.add_error_handler(self.error_handler)
        
        self.setup_handlers()

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Exception while handling an update: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )

    def setup_handlers(self):
        # Command handlers
        self.app.add_handler(CommandHandler("clear", self.chat_handler.clear_history))
        self.app.add_handler(CommandHandler("start", self.command_handler.start_command))
        self.app.add_handler(CommandHandler("help", self.command_handler.help_command))
        self.app.add_handler(CommandHandler("personality", self.personality_handler.personality_command))
        self.app.add_handler(CommandHandler("broadcast", self.admin_handler.broadcast_command))
        self.app.add_handler(CommandHandler("stats", self.admin_handler.stats_command))
        self.app.add_handler(CommandHandler("gen", self.chat_handler.handle_generate_image))
        
        # Add subscription check handler
        self.app.add_handler(CallbackQueryHandler(
            self.personality_handler.handle_subscription_check,
            pattern="^check_subscription$"
        ))
        
        # Callback handlers - personality handler must come before clear confirmation
        self.app.add_handler(CallbackQueryHandler(
            self.personality_handler.handle_personality_selection, 
            pattern="^personality_"
        ))
        self.app.add_handler(CallbackQueryHandler(
            self.chat_handler.handle_clear_confirmation,
            pattern="^clear_"  # Add pattern for clear confirmation
        ))
        
        # Message handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_handler.handle_message))
    def is_running(self):
        return hasattr(self, 'app') and self.app.running
    async def shutdown(self):
        try:
            if self.is_running():
                print("Shutting down bot...")
                await self.app.stop()
                await self.app.shutdown()
                print("Bᴏᴛ Iꜱ Sᴛᴏᴘᴘᴇᴅ....")
        except Exception as e:
            print(f"Error during shutdown: {e}")

    async def start(self):
        print("Starting bot...")
        await self.app.initialize()
        await self.app.start()
        me = await self.app.bot.get_me()
        print(f"{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        await self.app.bot.send_message(ADMIN_ID, f"**__{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**", parse_mode='Markdown')
        await self.app.updater.start_polling()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start())
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.shutdown())
        finally:
            loop.close()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()



# Don't Forget to Star the Repo ⭐ [https://github.com/Aditya-Agrahari1/GeminiChatBot]
#Support OpenSource
