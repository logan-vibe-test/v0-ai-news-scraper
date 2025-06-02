"""
Test script to verify the fixed AI Voice News Scraper
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_news_scraping():
    """Test news scraping functionality"""
    logger.info("🧪 Testing News Scraping...")
    
    try:
        from scrapers.news_scraper import scrape_news_sources
        news_items = await scrape_news_sources()
        
        logger.info(f"✅ Found {len(news_items)} articles")
        
        # Show first few articles
        for i, item in enumerate(news_items[:3]):
            logger.info(f"  {i+1}. {item['title'][:80]}... ({item['source']})")
        
        return news_items
    except Exception as e:
        logger.error(f"❌ News scraping failed: {str(e)}")
        return []

async def test_content_processing():
    """Test content processing"""
    logger.info("🧪 Testing Content Processing...")
    
    try:
        from processors.content_processor import process_content
        
        # Create test articles
        test_articles = [
            {
                'title': 'OpenAI Launches New Voice AI Model',
                'url': 'https://example.com/test1',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'content': 'OpenAI has announced a breakthrough in voice AI technology with their new text-to-speech model.',
                'raw_html': ''
            },
            {
                'title': 'ElevenLabs Introduces Voice Cloning Technology',
                'url': 'https://example.com/test2',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'content': 'ElevenLabs has released new voice cloning capabilities for their AI voice platform.',
                'raw_html': ''
            }
        ]
        
        processed_items = []
        for article in test_articles:
            processed = await process_content(article)
            if processed:
                processed_items.append(processed)
                logger.info(f"✅ Processed: {processed['title']}")
        
        logger.info(f"✅ Processed {len(processed_items)} relevant articles")
        return processed_items
        
    except Exception as e:
        logger.error(f"❌ Content processing failed: {str(e)}")
        return []

async def test_database():
    """Test database functionality"""
    logger.info("🧪 Testing Database...")
    
    try:
        from storage.db_manager import store_news_item, store_reaction
        
        # Test storing a news item
        test_item = {
            'title': 'Test Voice AI Article',
            'url': 'https://example.com/test',
            'source': 'Test Source',
            'published_date': datetime.now().isoformat(),
            'content': 'This is a test article about voice AI technology.',
            'summary': 'Test summary about voice AI.'
        }
        
        result = await store_news_item(test_item)
        if result:
            logger.info("✅ Database storage successful")
            return True
        else:
            logger.error("❌ Database storage failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database test failed: {str(e)}")
        return False

async def test_reddit():
    """Test Reddit scraping"""
    logger.info("🧪 Testing Reddit Scraping...")
    
    try:
        from scrapers.reddit_scraper import scrape_reddit
        reactions = await scrape_reddit()
        
        logger.info(f"✅ Found {len(reactions)} Reddit posts")
        
        # Show first few posts
        for i, reaction in enumerate(reactions[:2]):
            logger.info(f"  {i+1}. r/{reaction.get('subreddit', 'unknown')}: {reaction.get('title', '')[:60]}...")
        
        return reactions
        
    except Exception as e:
        logger.error(f"❌ Reddit scraping failed: {str(e)}")
        return []

async def run_full_test():
    """Run complete system test"""
    logger.info("🚀 Starting Full System Test")
    logger.info("=" * 60)
    
    # Test 1: News Scraping
    news_items = await test_news_scraping()
    
    # Test 2: Content Processing
    processed_items = await test_content_processing()
    
    # Test 3: Database
    db_success = await test_database()
    
    # Test 4: Reddit (optional)
    reddit_posts = await test_reddit()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📰 News Articles Found: {len(news_items)}")
    logger.info(f"🔍 Articles Processed: {len(processed_items)}")
    logger.info(f"🗄️ Database Working: {'✅' if db_success else '❌'}")
    logger.info(f"💬 Reddit Posts Found: {len(reddit_posts)}")
    
    if len(news_items) > 0 and len(processed_items) > 0 and db_success:
        logger.info("\n🎉 ALL CORE TESTS PASSED! The app is working!")
        logger.info("You can now run: python main_fixed.py")
    else:
        logger.error("\n❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(run_full_test())
