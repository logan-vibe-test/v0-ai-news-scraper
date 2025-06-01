"""
Test script to debug the AI Voice News Scraper
"""
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_environment():
    """Test environment configuration"""
    logger.info("=== Testing Environment Configuration ===")
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY', 'MONGODB_URI']
    optional_vars = ['SLACK_API_TOKEN', 'EMAIL_FROM', 'EMAIL_TO', 'SMTP_SERVER']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✓ {var}: {'*' * 10} (configured)")
        else:
            logger.error(f"✗ {var}: Not configured")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✓ {var}: {'*' * 10} (configured)")
        else:
            logger.warning(f"⚠ {var}: Not configured")

async def test_news_scraping():
    """Test news scraping functionality"""
    logger.info("=== Testing News Scraping ===")
    
    try:
        from scrapers.news_scraper import scrape_news_sources
        raw_news_items = await scrape_news_sources()
        logger.info(f"✓ Scraped {len(raw_news_items)} raw news items")
        
        # Show first few items
        for i, item in enumerate(raw_news_items[:3]):
            logger.info(f"  {i+1}. {item['title'][:100]}... from {item['source']}")
        
        return raw_news_items
    except Exception as e:
        logger.error(f"✗ News scraping failed: {str(e)}")
        return []

async def test_content_processing(news_items):
    """Test content processing"""
    logger.info("=== Testing Content Processing ===")
    
    if not news_items:
        logger.warning("No news items to process")
        return []
    
    try:
        from processors.content_processor import process_content
        
        # Test with first item
        test_item = news_items[0]
        logger.info(f"Testing with: {test_item['title']}")
        
        processed_item = await process_content(test_item)
        if processed_item:
            logger.info("✓ Content processing successful")
            logger.info(f"  Summary: {processed_item.get('summary', 'No summary')[:200]}...")
            return [processed_item]
        else:
            logger.warning("⚠ Item was filtered out (not relevant to voice AI)")
            return []
    except Exception as e:
        logger.error(f"✗ Content processing failed: {str(e)}")
        return []

async def test_database():
    """Test database connection"""
    logger.info("=== Testing Database Connection ===")
    
    try:
        from storage.db_manager import store_news_item
        
        # Test with dummy item
        test_item = {
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'source': 'Test Source',
            'published_date': datetime.now().isoformat(),
            'content': 'Test content about voice AI technology',
            'summary': 'Test summary'
        }
        
        result = await store_news_item(test_item)
        if result:
            logger.info("✓ Database connection successful")
        else:
            logger.error("✗ Database storage failed")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")

async def test_email():
    """Test email configuration"""
    logger.info("=== Testing Email Configuration ===")
    
    try:
        from notifiers.email_notifier import send_email_digest
        
        # Create test digest
        test_digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': [{
                'title': 'Test AI Voice News',
                'url': 'https://example.com/test',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'summary': 'This is a test summary for AI voice technology news.'
            }],
            'reactions': []
        }
        
        result = await send_email_digest(test_digest)
        if result:
            logger.info("✓ Email sent successfully")
        else:
            logger.error("✗ Email sending failed")
    except Exception as e:
        logger.error(f"✗ Email test failed: {str(e)}")

async def main():
    """Run all tests"""
    logger.info("Starting AI Voice News Scraper Tests")
    
    # Test environment
    await test_environment()
    
    # Test news scraping
    news_items = await test_news_scraping()
    
    # Test content processing
    processed_items = await test_content_processing(news_items)
    
    # Test database
    await test_database()
    
    # Test email
    await test_email()
    
    logger.info("Tests completed")

if __name__ == "__main__":
    asyncio.run(main())
