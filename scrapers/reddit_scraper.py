# Import the simplified version to avoid dependency issues
from .reddit_scraper_simple import scrape_reddit

# Re-export for compatibility
__all__ = ['scrape_reddit']
