"""
Simple Reddit test to verify functionality
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_reddit():
    """Test Reddit scraper functionality"""
    logger.info("🧪 Testing Reddit Scraper")
    
    # Check credentials
    if not all([os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET')]):
        logger.error("❌ Reddit API credentials not configured")
        logger.info("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in your .env file")
        return False
    
    try:
        from scrapers.reddit_scraper_improved import scrape_reddit
        
        logger.info("Starting Reddit scraping test...")
        reactions = await scrape_reddit([])
        
        logger.info(f"✅ Reddit test completed: {len(reactions)} reactions found")
        
        if reactions:
            logger.info("\n📋 Sample Results:")
            for i, reaction in enumerate(reactions[:5]):
                logger.info(f"{i+1}. r/{reaction['subreddit']} - {reaction['type']}")
                if reaction['type'] == 'post':
                    logger.info(f"   Title: {reaction['title']}")
                logger.info(f"   Content: {reaction['content'][:100]}...")
                logger.info(f"   Score: {reaction['score']} | Relevance: {reaction.get('relevance_score', 0)}")
                logger.info(f"   URL: {reaction['url']}")
                logger.info("")
        else:
            logger.warning("⚠️ No voice AI content found on Reddit")
            logger.info("This could be normal if there's no recent voice AI discussion")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Reddit test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_reddit())
