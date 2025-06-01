"""
AI Voice News Scraper - Version that works without social media
"""
import asyncio
import logging
from datetime import datetime

from scrapers.news_scraper import scrape_news_sources
from processors.content_processor import process_content
from storage.db_manager import store_news_item
from notifiers.email_notifier import send_email_digest
from notifiers.slack_notifier import send_slack_digest

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

async def run_news_pipeline():
    """Run the news monitoring pipeline"""
    logger.info("Starting news monitoring pipeline")
    
    # Step 1: Scrape news sources
    raw_news_items = await scrape_news_sources()
    logger.info(f"Scraped {len(raw_news_items)} raw news items")
    
    # Step 2: Process and filter content
    processed_items = []
    for item in raw_news_items:
        processed_item = await process_content(item)
        if processed_item:  # Only keep relevant items
            processed_items.append(processed_item)
    
    logger.info(f"Processed and filtered to {len(processed_items)} relevant news items")
    
    # Step 3: Store in database
    for item in processed_items:
        await store_news_item(item)
    
    return processed_items

async def generate_digest():
    """Generate and send daily digest"""
    logger.info("Generating daily digest")
    
    # Run news pipeline
    news_items = await run_news_pipeline()
    
    # Format digest
    digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': news_items,
        'reactions': []  # No social media reactions
    }
    
    logger.info(f"Digest contains {len(news_items)} news items")
    
    # Send notifications
    logger.info("Sending Slack digest...")
    slack_result = await send_slack_digest(digest)
    logger.info(f"Slack result: {slack_result}")
    
    logger.info("Sending email digest...")
    email_result = await send_email_digest(digest)
    logger.info(f"Email result: {email_result}")
    
    logger.info("Daily digest process completed")

async def main():
    """Main entry point"""
    logger.info("Starting AI Voice News Scraper (No Social Media)")
    
    # For testing, just run once
    await generate_digest()
    
    # Uncomment for scheduled runs:
    # while True:
    #     await generate_digest()
    #     # Run daily
    #     await asyncio.sleep(24 * 60 * 60)

if __name__ == "__main__":
    asyncio.run(main())
