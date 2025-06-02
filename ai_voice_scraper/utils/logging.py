"""
Logging utilities for AI Voice News Scraper
"""
import logging
import os
from datetime import datetime
import sys

def setup_logging(log_level=None):
    """Set up logging with the specified level"""
    level = getattr(logging, log_level or os.getenv('LOG_LEVEL', 'INFO'))
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create a log file with timestamp
    log_file = f"logs/ai_voice_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('ai_voice_scraper')
