"""
Optimized AI Voice News Scraper - Focused on voice AI with better filtering
"""
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

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

async def run_optimized_pipeline():
    """Run an optimized pipeline focused on voice AI"""
    logger.info("Starting optimized AI Voice News pipeline")
    
    # Step 1: Scrape news sources
    from scrapers.news_scraper import scrape_news_sources
    raw_news_items = await scrape_news_sources()
    logger.info(f"Scraped {len(raw_news_items)} total articles")
    
    # Step 2: Pre-filter by title for voice AI keywords
    voice_ai_candidates = []
    from config.keywords import PRIMARY_VOICE_AI_KEYWORDS, ALL_VOICE_AI_KEYWORDS
    
    for item in raw_news_items:
        title_lower = item['title'].lower()
        content_lower = item.get('content', '').lower()
        combined_text = f"{title_lower} {content_lower}"
        
        # Check if title or initial content mentions voice AI
        if any(keyword in combined_text for keyword in PRIMARY_VOICE_AI_KEYWORDS):
            voice_ai_candidates.append(item)
            logger.info(f"Voice AI candidate: {item['title']}")
    
    logger.info(f"Found {len(voice_ai_candidates)} voice AI candidates")
    
    # Step 3: Process the candidates (fetch full content and summarize)
    processed_items = []
    from processors.content_processor import process_content
    
    for item in voice_ai_candidates:
        try:
            processed_item = await process_content(item)
            if processed_item:
                processed_items.append(processed_item)
                logger.info(f"✅ Processed: {processed_item['title']}")
            else:
                logger.info(f"❌ Filtered out: {item['title']}")
        except Exception as e:
            logger.error(f"Error processing {item['title']}: {str(e)}")
    
    logger.info(f"Successfully processed {len(processed_items)} voice AI articles")
    
    # Step 4: Store in database
    from storage.db_manager import store_news_item
    stored_count = 0
    for item in processed_items:
        try:
            result = await store_news_item(item)
            if result:
                stored_count += 1
        except Exception as e:
            logger.error(f"Error storing item: {str(e)}")
    
    logger.info(f"Stored {stored_count} articles in database")
    
    return processed_items

async def send_notifications(news_items):
    """Send notifications with the processed news"""
    if not news_items:
        logger.info("No voice AI news to send")
        return
    
    # Create digest
    digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': news_items,
        'reactions': []  # Skip reactions for now to focus on news
    }
    
    logger.info(f"Sending digest with {len(news_items)} voice AI articles")
    
    # Send email notification
    try:
        from notifiers.email_notifier import send_email_digest
        email_result = await send_email_digest(digest)
        if email_result:
            logger.info("✅ Email digest sent successfully")
        else:
            logger.error("❌ Email digest failed")
    except Exception as e:
        logger.error(f"Email notification error: {str(e)}")
    
    # Send Slack notification (if configured)
    try:
        from notifiers.slack_notifier import send_slack_digest
        slack_result = await send_slack_digest(digest)
        if slack_result:
            logger.info("✅ Slack digest sent successfully")
        else:
            logger.info("⚠️ Slack digest not sent (likely not configured)")
    except Exception as e:
        logger.error(f"Slack notification error: {str(e)}")

async def main():
    """Main optimized pipeline"""
    logger.info("Starting Optimized AI Voice News Scraper")
    
    # Run the news pipeline
    voice_ai_news = await run_optimized_pipeline()
    
    # Send notifications
    await send_notifications(voice_ai_news)
    
    # Print summary
    print(f"\n{'='*60}")
    print("VOICE AI NEWS SUMMARY")
    print(f"{'='*60}")
    print(f"Found {len(voice_ai_news)} voice AI articles:")
    
    for i, item in enumerate(voice_ai_news, 1):
        print(f"\n{i}. {item['source']} - {item['title']}")
        print(f"   URL: {item['url']}")
        print(f"   Summary: {item.get('summary', 'No summary')[:150]}...")
    
    logger.info("Optimized pipeline completed")

if __name__ == "__main__":
    asyncio.run(main())
