"""
AI Voice News Scraper - Main Entry Point
"""
import asyncio
import logging
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging(log_level=None):
    """Set up logging with the specified level"""
    level = getattr(logging, log_level or os.getenv('LOG_LEVEL', 'INFO'))
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("ai_voice_scraper.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Import components
from ai_voice_scraper.scrapers.news_scraper import scrape_news_sources
from ai_voice_scraper.scrapers.reddit_scraper import scrape_reddit
from ai_voice_scraper.processors.content_processor import process_content
from ai_voice_scraper.storage.db_manager import store_news_item
from ai_voice_scraper.notifiers.slack_notifier import send_slack_digest
from ai_voice_scraper.notifiers.email_notifier import send_email_digest
from ai_voice_scraper.processors.trends_analyzer import analyze_current_trends
from ai_voice_scraper.storage.db_manager import store_run_summary, store_reaction

async def run_pipeline(logger):
    """Run the main pipeline"""
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
    
    # Calculate sentiment summary for trends
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    subreddit_activity = {}

    for reaction in reactions:
        sentiment = reaction.get('sentiment', 'neutral')
        sentiment_counts[sentiment] += 1
        
        subreddit = reaction.get('subreddit', 'unknown')
        subreddit_activity[subreddit] = subreddit_activity.get(subreddit, 0) + 1

    # Prepare run data for trends analysis
    current_run_data = {
        'articles_found': len(news_items),
        'articles_processed': len(processed_items),
        'reddit_posts': len(reactions),
        'sentiment_summary': sentiment_counts,
        'subreddit_activity': subreddit_activity
    }

    # Store this run's summary for future trend analysis
    await store_run_summary(current_run_data)
    
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
    return {
        "articles_found": len(news_items),
        "articles_processed": len(processed_items),
        "reddit_posts": len(reactions)
    }

def main_cli():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='AI Voice News Scraper')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Run the main pipeline
    try:
        results = asyncio.run(run_pipeline(logger))
        print("\n📊 Results:")
        print(f"  Articles found: {results['articles_found']}")
        print(f"  Articles processed: {results['articles_processed']} (relevant to voice AI)")
        print(f"  Reddit posts found: {results['reddit_posts']}")
        return 0
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        return 1

# Entry point for running the script directly
if __name__ == "__main__":
    sys.exit(main_cli())
