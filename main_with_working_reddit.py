"""
Main script using the working Reddit scraper
"""
import asyncio
import logging
from datetime import datetime

from scrapers.news_scraper import scrape_news_sources
from processors.content_processor import process_content
from storage.db_manager import store_news_item, store_reaction
from notifiers.email_notifier import send_email_digest
from notifiers.slack_notifier import send_slack_digest
from reddit_scraper_working import scrape_reddit_working

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

async def run_complete_pipeline():
    """Run the complete pipeline with working Reddit scraper"""
    logger.info("Starting complete AI Voice News pipeline")
    
    # Step 1: Scrape news sources
    logger.info("=== STEP 1: Scraping News ===")
    raw_news_items = await scrape_news_sources()
    logger.info(f"Scraped {len(raw_news_items)} raw news items")
    
    # Step 2: Process and filter content
    logger.info("=== STEP 2: Processing Content ===")
    processed_items = []
    for item in raw_news_items:
        processed_item = await process_content(item)
        if processed_item:  # Only keep relevant items
            processed_items.append(processed_item)
    
    logger.info(f"Processed and filtered to {len(processed_items)} relevant news items")
    
    # Step 3: Store news in database
    logger.info("=== STEP 3: Storing News ===")
    for item in processed_items:
        await store_news_item(item)
    
    # Step 4: Scrape Reddit reactions
    logger.info("=== STEP 4: Scraping Reddit ===")
    reddit_reactions = await scrape_reddit_working(processed_items)
    
    # Step 5: Store reactions
    logger.info("=== STEP 5: Storing Reactions ===")
    for reaction in reddit_reactions:
        await store_reaction(reaction)
    
    return processed_items, reddit_reactions

async def generate_complete_digest():
    """Generate and send complete digest with news and Reddit reactions"""
    logger.info("Generating complete digest")
    
    # Run the complete pipeline
    news_items, reactions = await run_complete_pipeline()
    
    # Format digest
    digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': news_items,
        'reactions': reactions
    }
    
    logger.info(f"Digest contains {len(news_items)} news items and {len(reactions)} reactions")
    
    # Send notifications
    logger.info("Sending notifications...")
    
    try:
        email_result = await send_email_digest(digest)
        logger.info(f"Email result: {email_result}")
    except Exception as e:
        logger.error(f"Email notification failed: {str(e)}")
    
    try:
        slack_result = await send_slack_digest(digest)
        logger.info(f"Slack result: {slack_result}")
    except Exception as e:
        logger.error(f"Slack notification failed: {str(e)}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("COMPLETE PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"📰 News Articles: {len(news_items)}")
    print(f"💬 Reddit Reactions: {len(reactions)}")
    
    if news_items:
        print(f"\nLatest Voice AI News:")
        for i, item in enumerate(news_items[:3], 1):
            print(f"{i}. {item['source']} - {item['title']}")
    
    if reactions:
        print(f"\nReddit Discussions:")
        for i, reaction in enumerate(reactions[:3], 1):
            print(f"{i}. r/{reaction['subreddit']} - {reaction['title']}")
    
    logger.info("Complete pipeline finished")

async def main():
    """Main entry point"""
    logger.info("Starting AI Voice News Scraper with Working Reddit")
    
    # Run the complete pipeline
    await generate_complete_digest()

if __name__ == "__main__":
    asyncio.run(main())
