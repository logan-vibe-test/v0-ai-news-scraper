"""
AI Voice News Scraper - Main Entry Point (Fixed Imports)
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

async def run_pipeline(logger):
    """Run the main pipeline"""
    logger.info("🚀 Starting AI Voice News Scraper")
    
    # Import components (import here to avoid circular imports)
    try:
        from scrapers.news_scraper import scrape_news_sources
        from scrapers.reddit_scraper import scrape_reddit
        from processors.content_processor import process_content
        from storage.db_manager import store_news_item, store_reaction, store_run_summary
        from notifiers.slack_notifier import send_slack_digest
        from notifiers.email_notifier import send_email_digest
        from processors.trends_analyzer import analyze_current_trends
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required files are in the correct directories")
        return {"error": str(e)}
    
    # Step 1: Scrape news
    logger.info("📰 Scraping news sources...")
    try:
        news_items = await scrape_news_sources()
        logger.info(f"Found {len(news_items)} articles")
    except Exception as e:
        logger.error(f"News scraping failed: {e}")
        news_items = []
    
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
    
    # Step 3: Scrape Reddit (if configured)
    reactions = []
    total_reddit_scanned = 0
    if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
        logger.info("💬 Scraping Reddit for AI voice topics...")
        try:
            reactions = await scrape_reddit()
            
            # Extract scanning metadata if available
            if reactions and '_metadata' in reactions[0]:
                metadata = reactions[0]['_metadata']
                total_reddit_scanned = metadata.get('total_scanned', 0)
                logger.info(f"📊 Reddit scanning stats: {total_reddit_scanned} posts scanned, {len(reactions)} relevant")
                # Remove metadata before storing
                del reactions[0]['_metadata']
            
            for reaction in reactions:
                await store_reaction(reaction)
            logger.info(f"Found {len(reactions)} Reddit posts about AI voice")
        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
    else:
        logger.info("Reddit API credentials not configured, skipping Reddit scraping")
    
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
        'total_reddit_scanned': total_reddit_scanned,
        'sentiment_summary': sentiment_counts,
        'subreddit_activity': subreddit_activity
    }

    # Store this run's summary for future trend analysis
    try:
        await store_run_summary(current_run_data)
        logger.info("📊 Stored run summary for trends analysis")
    except Exception as e:
        logger.error(f"Failed to store run summary: {e}")
    
    # Step 4: Send notifications
    if processed_items or reactions:
        digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': processed_items,
            'reactions': reactions,
            'total_reddit_scanned': total_reddit_scanned
        }
        
        # Email
        if all([os.getenv('SMTP_SERVER'), os.getenv('EMAIL_FROM'), os.getenv('EMAIL_TO')]):
            try:
                await send_email_digest(digest)
                logger.info("✅ Email sent")
            except Exception as e:
                logger.error(f"Email failed: {e}")
        else:
            logger.info("Email configuration incomplete, skipping email")
        
        # Slack
        if os.getenv('SLACK_API_TOKEN'):
            try:
                await send_slack_digest(digest)
                logger.info("✅ Slack sent")
            except Exception as e:
                logger.error(f"Slack failed: {e}")
        else:
            logger.info("Slack not configured, skipping Slack notification")
    else:
        logger.info("No content found, skipping notifications")
    
    logger.info("✅ Pipeline complete")
    return {
        "articles_found": len(news_items),
        "articles_processed": len(processed_items),
        "reddit_posts": len(reactions),
        "total_reddit_scanned": total_reddit_scanned
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
        
        if "error" in results:
            print(f"\n❌ Error: {results['error']}")
            print("Please check the file structure and imports")
            return 1
        
        print("\n📊 Results:")
        print(f"  Articles found: {results['articles_found']}")
        print(f"  Articles processed: {results['articles_processed']} (relevant to voice AI)")
        print(f"  Reddit posts found: {results['reddit_posts']}")
        if results.get('total_reddit_scanned', 0) > 0:
            print(f"  Reddit posts scanned: {results['total_reddit_scanned']}")
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
