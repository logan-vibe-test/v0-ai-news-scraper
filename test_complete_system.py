"""
Test the complete system with working Reddit scraper
"""
import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def test_news_scraping():
    """Test news scraping"""
    logger.info("Testing news scraping...")
    try:
        from scrapers.news_scraper import scrape_news_sources
        news_items = await scrape_news_sources()
        logger.info(f"✅ News scraping: {len(news_items)} articles found")
        return len(news_items) > 0
    except Exception as e:
        logger.error(f"❌ News scraping failed: {str(e)}")
        return False

async def test_reddit_scraping():
    """Test Reddit scraping"""
    logger.info("Testing Reddit scraping...")
    try:
        from reddit_scraper_working import scrape_reddit_working
        reactions = await scrape_reddit_working()
        logger.info(f"✅ Reddit scraping: {len(reactions)} reactions found")
        return True  # Success even if no reactions found
    except Exception as e:
        logger.error(f"❌ Reddit scraping failed: {str(e)}")
        return False

async def test_email_notification():
    """Test email notification"""
    logger.info("Testing email notification...")
    try:
        from notifiers.email_notifier import send_email_digest
        from datetime import datetime
        
        test_digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': [{
                'title': 'Test Voice AI News',
                'url': 'https://example.com',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'summary': 'This is a test summary for voice AI news.'
            }],
            'reactions': []
        }
        
        result = await send_email_digest(test_digest)
        logger.info(f"✅ Email notification: {'Success' if result else 'Failed'}")
        return result
    except Exception as e:
        logger.error(f"❌ Email notification failed: {str(e)}")
        return False

async def main():
    """Test all components"""
    print("🧪 Testing Complete AI Voice News Scraper System")
    print("=" * 60)
    
    # Test each component
    news_ok = await test_news_scraping()
    reddit_ok = await test_reddit_scraping()
    email_ok = await test_email_notification()
    
    # Summary
    print(f"\n{'='*60}")
    print("SYSTEM TEST RESULTS")
    print(f"{'='*60}")
    print(f"📰 News Scraping: {'✅ WORKING' if news_ok else '❌ FAILED'}")
    print(f"💬 Reddit Scraping: {'✅ WORKING' if reddit_ok else '❌ FAILED'}")
    print(f"📧 Email Notifications: {'✅ WORKING' if email_ok else '❌ FAILED'}")
    
    if all([news_ok, reddit_ok, email_ok]):
        print(f"\n🎉 ALL SYSTEMS WORKING!")
        print("You can now run: python main_with_working_reddit.py")
    else:
        print(f"\n⚠️ Some components need attention")
        if not news_ok:
            print("- Check your news sources and internet connection")
        if not reddit_ok:
            print("- Check your Reddit API credentials")
        if not email_ok:
            print("- Check your email configuration")

if __name__ == "__main__":
    asyncio.run(main())
