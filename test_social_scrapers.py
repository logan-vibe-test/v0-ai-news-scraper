"""
Test script for social media scrapers
"""
import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_reddit():
    """Test Reddit scraper"""
    logger.info("Testing Reddit scraper...")
    
    # Check if Reddit credentials are configured
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing Reddit credentials: {missing_vars}")
        logger.info("Please set these in your .env file")
        return False
    
    try:
        from scrapers.reddit_scraper_improved import scrape_reddit
        reactions = await scrape_reddit()
        
        logger.info(f"Found {len(reactions)} Reddit reactions")
        return len(reactions) > 0
    except Exception as e:
        logger.error(f"Reddit test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_twitter():
    """Test Twitter scraper"""
    logger.info("Testing Twitter scraper...")
    
    # Check if Twitter credentials are configured
    if not os.getenv('TWITTER_BEARER_TOKEN'):
        logger.error("Missing TWITTER_BEARER_TOKEN")
        logger.info("Please set this in your .env file")
        return False
    
    try:
        from scrapers.twitter_scraper_improved import scrape_twitter
        reactions = await scrape_twitter()
        
        logger.info(f"Found {len(reactions)} Twitter reactions")
        return len(reactions) > 0
    except Exception as e:
        logger.error(f"Twitter test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    logger.info("Testing social media scrapers")
    
    # Test Reddit
    reddit_success = await test_reddit()
    
    # Test Twitter
    twitter_success = await test_twitter()
    
    # Summary
    print(f"\n{'='*60}")
    print("SOCIAL MEDIA SCRAPER TEST RESULTS")
    print(f"{'='*60}")
    print(f"Reddit: {'✅ WORKING' if reddit_success else '❌ FAILED'}")
    print(f"Twitter: {'✅ WORKING' if twitter_success else '❌ FAILED'}")
    
    if not reddit_success or not twitter_success:
        print("\nTROUBLESHOOTING TIPS:")
        
        if not reddit_success:
            print("\nFor Reddit:")
            print("1. Verify your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are correct")
            print("2. Create a new Reddit app at https://www.reddit.com/prefs/apps")
            print("3. For better results, add REDDIT_USERNAME and REDDIT_PASSWORD to your .env")
        
        if not twitter_success:
            print("\nFor Twitter:")
            print("1. Verify your TWITTER_BEARER_TOKEN is correct")
            print("2. Twitter API now requires a paid developer account")
            print("3. Consider using the free tier ($100/month) at https://developer.twitter.com/")
            print("4. If you don't want to pay, you can disable Twitter scraping")

if __name__ == "__main__":
    asyncio.run(main())
