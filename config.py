"""
Configuration for AI Voice News Scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# General configuration
CONFIG = {
    # Scraping frequency in seconds
    'scraping_interval': int(os.getenv('SCRAPING_INTERVAL', 3600)),  # Default: 1 hour
    
    # Digest frequency in seconds
    'digest_interval': int(os.getenv('DIGEST_INTERVAL', 86400)),  # Default: 24 hours
    
    # Notification settings
    'notifications': {
        'slack': os.getenv('ENABLE_SLACK', 'false').lower() == 'true',
        'email': os.getenv('ENABLE_EMAIL', 'false').lower() == 'true',
    },
    
    # Logging level
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    
    # Database settings
    'database': {
        'uri': os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
        'name': os.getenv('DB_NAME', 'ai_voice_news'),
    },
}
