"""
AI Voice News Scraper - Production Main Entry Point
"""
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

from scrapers.news_scraper import scrape_news_sources
from scrapers.reddit_scraper import scrape_reddit
from scrapers.twitter_scraper import scrape_twitter
from processors.content_processor import process_content
from processors.sentiment_analyzer import analyze_sentiment
from storage.db_manager import store_news_item, store_reaction, get_recent_news
from notifiers.slack_notifier import send_slack_digest
from notifiers.email_notifier import send_email_digest

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_voice_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIVoiceNewsScraper:
    def __init__(self):
        self.stats = {
            'news_items_processed': 0,
            'news_items_relevant': 0,
            'reddit_reactions': 0,
            'twitter_reactions': 0,
            'total_reactions': 0
        }
    
    async def run_news_pipeline(self):
        """Run the news monitoring pipeline"""
        logger.info("🔄 Starting news monitoring pipeline")
        
        try:
            # Step 1: Scrape news sources
            raw_news_items = await scrape_news_sources()
            self.stats['news_items_processed'] = len(raw_news_items)
            logger.info(f"📰 Scraped {len(raw_news_items)} raw news items")
            
            # Step 2: Process and filter content
            processed_items = []
            for item in raw_news_items:
                try:
                    processed_item = await process_content(item)
                    if processed_item:  # Only keep relevant items
                        processed_items.append(processed_item)
                except Exception as e:
                    logger.warning(f"Error processing item {item.get('title', 'Unknown')}: {str(e)}")
                    continue
            
            self.stats['news_items_relevant'] = len(processed_items)
            logger.info(f"🎯 Filtered to {len(processed_items)} relevant news items")
            
            # Step 3: Store in database
            stored_count = 0
            for item in processed_items:
                try:
                    if await store_news_item(item):
                        stored_count += 1
                except Exception as e:
                    logger.warning(f"Error storing item {item.get('title', 'Unknown')}: {str(e)}")
            
            logger.info(f"💾 Stored {stored_count} news items in database")
            return processed_items
            
        except Exception as e:
            logger.error(f"❌ News pipeline failed: {str(e)}")
            return []
    
    async def run_reaction_pipeline(self):
        """Run the developer reaction monitoring pipeline"""
        logger.info("🔄 Starting developer reaction pipeline")
        
        try:
            # Get recent news to match reactions against
            recent_news = await get_recent_news(days=3)
            logger.info(f"📚 Found {len(recent_news)} recent news items for reaction matching")
            
            all_reactions = []
            
            # Step 1: Scrape Reddit (if configured)
            if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
                try:
                    reddit_reactions = await scrape_reddit(recent_news)
                    self.stats['reddit_reactions'] = len(reddit_reactions)
                    all_reactions.extend(reddit_reactions)
                    logger.info(f"🔴 Found {len(reddit_reactions)} Reddit reactions")
                except Exception as e:
                    logger.warning(f"Reddit scraping failed: {str(e)}")
            else:
                logger.info("⚠️ Reddit API not configured, skipping Reddit scraping")
            
            # Step 2: Scrape Twitter (if configured)
            if os.getenv('TWITTER_BEARER_TOKEN'):
                try:
                    twitter_reactions = await scrape_twitter(recent_news)
                    self.stats['twitter_reactions'] = len(twitter_reactions)
                    all_reactions.extend(twitter_reactions)
                    logger.info(f"🐦 Found {len(twitter_reactions)} Twitter reactions")
                except Exception as e:
                    logger.warning(f"Twitter scraping failed: {str(e)}")
            else:
                logger.info("⚠️ Twitter API not configured, skipping Twitter scraping")
            
            self.stats['total_reactions'] = len(all_reactions)
            logger.info(f"💬 Total reactions found: {len(all_reactions)}")
            
            # Step 3: Analyze sentiment and store
            stored_reactions = 0
            for reaction in all_reactions:
                try:
                    reaction['sentiment'] = await analyze_sentiment(reaction['content'])
                    if await store_reaction(reaction):
                        stored_reactions += 1
                except Exception as e:
                    logger.warning(f"Error processing reaction: {str(e)}")
            
            logger.info(f"💾 Stored {stored_reactions} reactions in database")
            return all_reactions
            
        except Exception as e:
            logger.error(f"❌ Reaction pipeline failed: {str(e)}")
            return []
    
    async def generate_and_send_digest(self, news_items, reactions):
        """Generate and send daily digest"""
        logger.info("📧 Generating and sending digest")
        
        # Format digest
        digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': news_items,
            'reactions': reactions,
            'stats': self.stats
        }
        
        logger.info(f"📊 Digest stats: {self.stats['news_items_relevant']} news items, {self.stats['total_reactions']} reactions")
        
        # Send notifications
        notification_results = {'slack': False, 'email': False}
        
        # Send Slack notification (if configured)
        if os.getenv('SLACK_API_TOKEN'):
            try:
                notification_results['slack'] = await send_slack_digest(digest)
                logger.info(f"📱 Slack notification: {'✅ Success' if notification_results['slack'] else '❌ Failed'}")
            except Exception as e:
                logger.error(f"Slack notification failed: {str(e)}")
        
        # Send email notification (if configured)
        email_vars = ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_TO']
        if all(os.getenv(var) for var in email_vars):
            try:
                notification_results['email'] = await send_email_digest(digest)
                logger.info(f"📧 Email notification: {'✅ Success' if notification_results['email'] else '❌ Failed'}")
            except Exception as e:
                logger.error(f"Email notification failed: {str(e)}")
        
        return notification_results
    
    async def run_full_pipeline(self):
        """Run the complete pipeline"""
        start_time = datetime.now()
        logger.info("🚀 Starting AI Voice News Scraper")
        logger.info("=" * 60)
        
        try:
            # Run both pipelines
            news_items = await self.run_news_pipeline()
            reactions = await self.run_reaction_pipeline()
            
            # Generate and send digest
            notification_results = await self.generate_and_send_digest(news_items, reactions)
            
            # Log completion
            duration = datetime.now() - start_time
            logger.info("=" * 60)
            logger.info(f"✅ Pipeline completed in {duration.total_seconds():.1f} seconds")
            logger.info(f"📊 Final stats: {self.stats}")
            
            # Check if any notifications were sent
            if any(notification_results.values()):
                logger.info("🎉 Digest sent successfully!")
            else:
                logger.warning("⚠️ No notifications were sent (check configuration)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            return False

async def main():
    """Main entry point"""
    scraper = AIVoiceNewsScraper()
    
    # Check if this is a one-time run or scheduled
    run_once = os.getenv('RUN_ONCE', 'true').lower() == 'true'
    
    if run_once:
        logger.info("🔄 Running once (set RUN_ONCE=false for continuous mode)")
        await scraper.run_full_pipeline()
    else:
        logger.info("🔄 Running in continuous mode (daily)")
        while True:
            await scraper.run_full_pipeline()
            # Wait 24 hours
            logger.info("😴 Sleeping for 24 hours...")
            await asyncio.sleep(24 * 60 * 60)

if __name__ == "__main__":
    asyncio.run(main())
