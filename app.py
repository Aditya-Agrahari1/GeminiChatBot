from flask import Flask
from main import TelegramBot
import asyncio
import threading
import os
import sys
import time

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
bot = None
loop = None
bot_thread = None
bot_ready = False

def run_bot():
    global bot, loop, bot_ready
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = TelegramBot()
        
        # Run the bot in the event loop
        async def start_and_run():
            await bot.app.initialize()
            await bot.app.start()
            await bot.app.updater.start_polling(drop_pending_updates=True)
            global bot_ready
            bot_ready = True
            while True:
                await asyncio.sleep(1)
            
        loop.run_until_complete(start_and_run())
    except Exception as e:
        print(f"Bot error: {e}")
        if bot and hasattr(bot, 'app'):
            loop.run_until_complete(bot.shutdown())
        sys.exit(1)

# Start bot before Flask app
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# Wait for bot to initialize
timeout = 10  # seconds
start_time = time.time()
while not bot_ready and time.time() - start_time < timeout:
    time.sleep(0.5)

@app.route("/")
def home():
    status = "🟢 Online" if bot and bot.is_running() else "🔴 Offline"
    return f"Bot Status: {status}"

@app.route("/health")
def health_check():
    if bot and hasattr(bot, 'app') and bot.app.running:
        return "OK", 200
    return "Service Unavailable", 503

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)