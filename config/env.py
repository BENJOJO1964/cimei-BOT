import os
from dotenv import load_dotenv

load_dotenv()

# LINE Messaging API credentials
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# Google Sheet credentials (optional for sheet_writer.py)
GSPREAD_SERVICE_ACCOUNT_JSON = os.getenv("GSPREAD_SERVICE_ACCOUNT_JSON")

# Weather API key (for future use)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# OpenAI API key (for GPT chat)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram Bot Token and Group ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID") 