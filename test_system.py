"""
Comprehensive system test for AI Voice News Scraper
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class SystemTester:
    def __init__(self):
        self.results = {}
    
    async def test_environment(self):
        """Test environment configuration"""
        logger.info("🔧 Testing Environment Configuration")
        
        required_vars = ['OPENAI_API_KEY', 'MONGODB_URI', 'EMAIL_FROM', 'EMAIL_TO']
        optional_vars = ['REDDIT_CLIENT_ID', 'TWITTER_BEARER_TOKEN', 'SLACK_API_TOKEN']
        
        missing_required = []
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        missing_optional = []
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_required:
            logger.error(f"❌ Missing required variables: {', '.join(missing_required)}")
            self.results['environment'] = False
        else:
            logger.info("✅ All required environment variables configured")
            if missing_optional:
                logger.warning(f"⚠️ Optional variables not configured: {', '.join(missing_optional)}")
            self.results['environment'] = True
        
        return self.results['environment']
    
    async def test_news_scraping(self):
        """Test news scraping functionality"""
        logger.info("📰 Testing News Scraping")
        
        try:
            from scrapers.news_scraper import scrape_news_sources
            news_items = await scrape_news_sources()
            
            if news_items:
                logger.info(f"✅ News scraping successful: {len(news_items)} articles found")
                # Show sample
                for i, item in enumerate(news_items[:2]):
                    logger.info(f"   {i+1}. {item['title'][:80]}... ({item['source']})")
                self.results['news_scraping'] = True
            else:
                logger.warning("⚠️ News scraping returned no articles")
                self.results['news_scraping'] = False
            
        except Exception as e:
            logger.error(f"❌ News scraping failed: {str(e)}")
            self.results['news_scraping'] = False
        
        return self.results['news_scraping']
    
    async def test_content_processing(self):
        """Test content processing"""
        logger.info("🔍 Testing Content Processing")
        
        if not os.getenv('OPENAI_API_KEY'):
            logger.warning("⚠️ OpenAI API key not configured, skipping content processing test")
            self.results['content_processing'] = False
            return False
        
        try:
            from processors.content_processor import process_content
            
            # Create a test article about voice AI
            test_article = {
                'title': 'New Voice AI Technology Breakthrough',
                'url': 'https://example.com/test',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'content': 'This article discusses new developments in voice AI technology, including text-to-speech synthesis and voice cloning capabilities.',
                'raw_html': ''
            }
            
            # Mock the fetch_article_content function to return our test content
            import processors.content_processor as cp
            original_fetch = cp.fetch_article_content
            
            async def mock_fetch(url):
                return test_article['content']
            cp.fetch_article_content = mock_fetch
            
            processed = await process_content(test_article)
            
            # Restore original function
            cp.fetch_article_content = original_fetch
            
            if processed and 'summary' in processed:
                logger.info("✅ Content processing successful")
                logger.info(f"   Summary: {processed['summary'][:100]}...")
                self.results['content_processing'] = True
            else:
                logger.warning("⚠️ Content processing returned no result")
                self.results['content_processing'] = False
                
        except Exception as e:
            logger.error(f"❌ Content processing failed: {str(e)}")
            self.results['content_processing'] = False
        
        return self.results['content_processing']
    
    async def test_reddit_scraping(self):
        """Test Reddit scraping"""
        logger.info("💬 Testing Reddit Scraping")
        
        if not all([os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET')]):
            logger.warning("⚠️ Reddit API credentials not configured, skipping Reddit test")
            self.results['reddit_scraping'] = False
            return False
        
        try:
            from scrapers.reddit_scraper import scrape_reddit
            reactions = await scrape_reddit([])
            
            logger.info(f"✅ Reddit scraping successful: {len(reactions)} reactions found")
            if reactions:
                for i, reaction in enumerate(reactions[:2]):
                    logger.info(f"   {i+1}. r/{reaction.get('subreddit', 'unknown')}: {reaction.get('title', '')[:60]}...")
            
            self.results['reddit_scraping'] = True
            
        except Exception as e:
            logger.error(f"❌ Reddit scraping failed: {str(e)}")
            self.results['reddit_scraping'] = False
        
        return self.results['reddit_scraping']
    
    async def test_database(self):
        """Test database connection"""
        logger.info("🗄️ Testing Database Connection")
        
        if not os.getenv('MONGODB_URI'):
            logger.warning("⚠️ MongoDB URI not configured, skipping database test")
            self.results['database'] = False
            return False
        
        try:
            from storage.db_manager import store_news_item
            
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
                logger.info("✅ Database connection successful")
                self.results['database'] = True
            else:
                logger.error("❌ Database storage failed")
                self.results['database'] = False
                
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            self.results['database'] = False
        
        return self.results['database']
    
    async def test_email_notification(self):
        """Test email notification"""
        logger.info("📧 Testing Email Notification")
        
        required_email_vars = ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_TO']
        if not all(os.getenv(var) for var in required_email_vars):
            logger.warning("⚠️ Email configuration incomplete, skipping email test")
            self.results['email_notification'] = False
            return False
        
        try:
            from notifiers.email_notifier import send_email_digest
            
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
            if result:
                logger.info("✅ Email notification successful")
                self.results['email_notification'] = True
            else:
                logger.error("❌ Email notification failed")
                self.results['email_notification'] = False
                
        except Exception as e:
            logger.error(f"❌ Email notification failed: {str(e)}")
            self.results['email_notification'] = False
        
        return self.results['email_notification']
    
    async def run_all_tests(self):
        """Run all system tests"""
        logger.info("🧪 Starting AI Voice News Scraper System Tests")
        logger.info("=" * 60)
        
        # Run all tests
        await self.test_environment()
        await self.test_news_scraping()
        await self.test_content_processing()
        await self.test_reddit_scraping()
        await self.test_database()
        await self.test_email_notification()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("SYSTEM TEST RESULTS")
        logger.info("=" * 60)
        
        test_names = {
            'environment': '🔧 Environment Configuration',
            'news_scraping': '📰 News Scraping',
            'content_processing': '🔍 Content Processing',
            'reddit_scraping': '💬 Reddit Scraping',
            'database': '🗄️ Database Connection',
            'email_notification': '📧 Email Notification'
        }
        
        passed = 0
        total = len(self.results)
        
        for test_key, test_name in test_names.items():
            status = "✅ PASS" if self.results.get(test_key, False) else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
            if self.results.get(test_key, False):
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! System is ready for production.")
            logger.info("Run: python main.py")
        elif passed >= 3:  # Core functionality works
            logger.info("⚠️ Core functionality working. Some optional features may be disabled.")
            logger.info("Run: python main_no_social.py (for news-only mode)")
        else:
            logger.error("❌ Critical issues found. Please fix configuration before running.")
        
        return passed, total

async def main():
    """Main test function"""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
