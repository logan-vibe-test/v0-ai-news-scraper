"""
Reddit scraper for AI Voice News Scraper - Uses improved version
"""
from .reddit_scraper_improved import scrape_reddit, initialize_reddit

# Re-export the main functions
__all__ = ['scrape_reddit', 'initialize_reddit']
