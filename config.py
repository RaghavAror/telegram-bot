import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # For web search