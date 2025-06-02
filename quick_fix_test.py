"""
Quick test to verify the app works
"""
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def quick_test():
    """Quick test of core functionality"""
    logger.info("🧪 Quick Test Starting...")
    
    try:
        # Test 1: Import main components
        from scrapers.news_scraper import scrape_news_sources
        from processors.content_processor import process_content
        from storage.db_manager import store_news_item
        logger.info("✅ All imports successful")
        
        # Test 2: Scrape a few articles
        logger.info("📰 Testing news scraping...")
        news_items = await scrape_news_sources()
        logger.info(f"✅ Found {len(news_items)} articles")
        
        if news_items:
            # Test 3: Process first article
            logger.info("🔍 Testing content processing...")
            first_article = news_items[0]
            processed = await process_content(first_article)
            
            if processed:
                logger.info(f"✅ Processed article: {processed['title'][:50]}...")
                
                # Test 4: Store in database
                logger.info("🗄️ Testing database storage...")
                result = await store_news_item(processed)
                if result:
                    logger.info("✅ Database storage successful")
                    logger.info("\n🎉 QUICK TEST PASSED! App is working!")
                else:
                    logger.error("❌ Database storage failed")
            else:
                logger.warning("⚠️ No articles were relevant to voice AI")
        else:
            logger.error("❌ No articles found")
            
    except Exception as e:
        logger.error(f"❌ Quick test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_test())
