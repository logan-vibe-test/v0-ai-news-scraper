"""
Configuration package for AI Voice News Scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper_v1.0')
SLACK_API_TOKEN = os.getenv('SLACK_API_TOKEN')

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')

# Database Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'ai_voice_news')

# Application Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', 50))
MAX_REDDIT_POSTS = int(os.getenv('MAX_REDDIT_POSTS', 30))
