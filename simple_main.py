"""
Simplified main script to test basic functionality
"""
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def simple_test():
    """Simple test to see if we can get any articles"""
    logger.info("Starting simple test")
    
    try:
        # Test news scraping
        from scrapers.news_scraper import scrape_news_sources
        logger.info("Testing news scraping...")
        
        raw_news_items = await scrape_news_sources()
        logger.info(f"Found {len(raw_news_items)} raw articles")
        
        # Show first few articles
        for i, item in enumerate(raw_news_items[:5]):
            logger.info(f"{i+1}. {item['source']}: {item['title']}")
        
        if len(raw_news_items) == 0:
            logger.error("No articles found! Check your news sources and selectors.")
            return
        
        # Test processing one article (without relevance filtering)
        logger.info("Testing article processing...")
        test_item = raw_news_items[0].copy()
        
        # Simple processing without relevance check
        from processors.content_processor import fetch_article_content
        content = await fetch_article_content(test_item['url'])
        
        if content:
            test_item['content'] = content
            test_item['summary'] = f"Test summary for: {test_item['title']}"
            logger.info(f"Successfully processed: {test_item['title']}")
            logger.info(f"Content length: {len(content)} characters")
        else:
            logger.error(f"Failed to fetch content for: {test_item['url']}")
        
    except Exception as e:
        logger.error(f"Error in simple test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
