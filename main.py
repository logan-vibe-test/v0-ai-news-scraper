"""
AI Voice News Scraper - Main Entry Point
"""
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Import components
from scrapers.news_scraper import scrape_news_sources
from scrapers.reddit_scraper import scrape_reddit
from processors.content_processor import process_content
from storage.db_manager import store_news_item, store_reaction, store_run_summary
from notifiers.slack_notifier import send_slack_digest
from notifiers.email_notifier import send_email_digest
from processors.trends_analyzer import analyze_current_trends

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_voice_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main pipeline"""
    logger.info("🚀 Starting AI Voice News Scraper")
    
    # Step 1: Scrape news
    logger.info("📰 Scraping news sources...")
    news_items = await scrape_news_sources()
    logger.info(f"Found {len(news_items)} articles")
    
    # Step 2: Process content
    logger.info("🔍 Processing content...")
    processed_items = []
    for item in news_items:
        try:
            processed = await process_content(item)
            if processed:
                processed_items.append(processed)
                await store_news_item(processed)
        except Exception as e:
            logger.error(f"Error processing {item.get('title', 'Unknown')}: {e}")
    
    logger.info(f"Processed {len(processed_items)} relevant articles")
    
    # Step 3: Scrape Reddit (if configured) - now independent of news items
    reactions = []
    if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
        logger.info("💬 Scraping Reddit for AI voice topics...")
        try:
            reactions = await scrape_reddit()  # No longer passing processed_items
            for reaction in reactions:
                await store_reaction(reaction)
            logger.info(f"Found {len(reactions)} Reddit posts about AI voice")
        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
    
    # Step 4: Send notifications
    if processed_items or reactions:
        digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': processed_items,
            'reactions': reactions
        }
        
        # Email
        if all([os.getenv('SMTP_SERVER'), os.getenv('EMAIL_FROM'), os.getenv('EMAIL_TO')]):
            try:
                await send_email_digest(digest)
                logger.info("✅ Email sent")
            except Exception as e:
                logger.error(f"Email failed: {e}")
        
        # Slack
        if os.getenv('SLACK_API_TOKEN'):
            try:
                await send_slack_digest(digest)
                logger.info("✅ Slack sent")
            except Exception as e:
                logger.error(f"Slack failed: {e}")
    
    logger.info("✅ Pipeline complete")

if __name__ == "__main__":
    asyncio.run(main())
