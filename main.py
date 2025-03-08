from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.admin import AdminHandler
from handlers.chat import ChatHandler
from handlers.commands import CommandHandler as BotCommandHandler
from handlers.personality import PersonalityHandler
from config import TELEGRAM_TOKEN
from aiohttp import web
import asyncio

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Initialize handlers
        self.admin_handler = AdminHandler()
        self.chat_handler = ChatHandler()
        self.command_handler = BotCommandHandler()
        self.personality_handler = PersonalityHandler()
        
        self.setup_handlers()

    def setup_handlers(self):
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.command_handler.start_command))
        self.app.add_handler(CommandHandler("help", self.command_handler.help_command))
        self.app.add_handler(CommandHandler("clear", self.chat_handler.clear_history))
        self.app.add_handler(CommandHandler("personality", self.personality_handler.personality_command))
        self.app.add_handler(CommandHandler("broadcast", self.admin_handler.broadcast_command))
        self.app.add_handler(CommandHandler("stats", self.admin_handler.stats_command))
        
        # Message handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_handler.handle_message))
        
        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(
            self.personality_handler.handle_personality_selection, 
            pattern="^personality_"
        ))

    async def health_check(self, request):
        return web.Response(text="Bot is running!")

    async def run_web(self):
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
        await site.start()

    def run(self):
        print("Starting bot...")
        loop = asyncio.get_event_loop()
        loop.create_task(self.web_app.startup())
        loop.create_task(self.run_web())
        self.app.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()