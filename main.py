"""
AI Voice News Scraper - Main entry point
"""
import asyncio
import logging
from datetime import datetime

from scrapers.news_scraper import scrape_news_sources
from scrapers.reddit_scraper import scrape_reddit
from scrapers.twitter_scraper import scrape_twitter
from processors.content_processor import process_content
from processors.sentiment_analyzer import analyze_sentiment
from storage.db_manager import store_news_item, store_reaction, get_recent_news
from notifiers.slack_notifier import send_slack_digest
from notifiers.email_notifier import send_email_digest

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

async def run_reaction_pipeline():
    """Run the developer reaction monitoring pipeline"""
    logger.info("Starting developer reaction pipeline")
    
    # Get recent news to match reactions against
    recent_news = await get_recent_news(days=3)
    
    # Step 1: Scrape Reddit
    reddit_reactions = await scrape_reddit(recent_news)
    
    # Step 2: Scrape Twitter/X
    twitter_reactions = await scrape_twitter(recent_news)
    
    # Combine reactions
    all_reactions = reddit_reactions + twitter_reactions
    logger.info(f"Found {len(all_reactions)} relevant reactions")
    
    # Step 3: Analyze sentiment
    for reaction in all_reactions:
        reaction['sentiment'] = await analyze_sentiment(reaction['content'])
        await store_reaction(reaction)
    
    return all_reactions

async def generate_digest():
    """Generate and send daily digest"""
    logger.info("Generating daily digest")
    
    # Run both pipelines
    news_items = await run_news_pipeline()
    reactions = await run_reaction_pipeline()
    
    # Format digest
    digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': news_items,
        'reactions': reactions
    }
    
    # Send notifications
    await send_slack_digest(digest)
    await send_email_digest(digest)
    
    logger.info("Daily digest sent successfully")

async def main():
    """Main entry point"""
    logger.info("Starting AI Voice News Scraper")
    
    # For testing, just run once
    await generate_digest()
    
    # Uncomment for scheduled runs:
    # while True:
    #     await generate_digest()
    #     # Run daily
    #     await asyncio.sleep(24 * 60 * 60)

if __name__ == "__main__":
    asyncio.run(main())
