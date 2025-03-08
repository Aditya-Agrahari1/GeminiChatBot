import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
LOG_CHANNEL = os.getenv("TELEGRAM_LOG_CHANNEL")
CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME")

# Personality Settings
PERSONALITIES = {
    "friendly": "You are a warm, friendly AI assistant who uses emojis and casual language.",
    "witty": "You are a witty, sarcastic AI assistant who loves wordplay and clever jokes.",
    "expert": "You are a professional, knowledgeable AI assistant who provides detailed, technical responses."
}

# AI Model Configuration
GEMINI_CONFIG = {
    "model_name": "gemini-2.0-flash",
    "generation_config": {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
}