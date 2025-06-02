import asyncio
import os
import logging
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv

from api_client import fetch_news
from data_processor import process_article, summarize_sentiment, aggregate_subreddit_activity
from database import store_article, store_reaction, get_stored_urls
from reddit_scraper import scrape_reddit
from sentiment_model import load_model

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    Main function to orchestrate news fetching, processing, and storage.
    """
    logger.info("Starting the news aggregation and sentiment analysis pipeline...")

    # Step 1: Load the sentiment analysis model
    try:
        sentiment_model = load_model()
        logger.info("Sentiment analysis model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load sentiment analysis model: {e}")
        return

    # Step 2: Fetch news articles
    news_api_key = os.getenv('NEWS_API_KEY')
    news_sources = os.getenv('NEWS_SOURCES', 'bbc-news,reuters').split(',')  # Use a comma-separated string in .env
    news_items = []
    try:
        news_items = await fetch_news(news_api_key, sources=news_sources)
        logger.info(f"Fetched {len(news_items)} news articles from the API.")
    except Exception as e:
        logger.error(f"Failed to fetch news articles: {e}")

    # Step 2.5: Get stored URLs
    try:
        stored_urls = await get_stored_urls()
        logger.info(f"Fetched {len(stored_urls)} URLs from the database.")
    except Exception as e:
        logger.error(f"Failed to fetch stored URLs from the database: {e}")
        stored_urls = []

    # Step 3: Process and store news articles
    processed_items = []
    sentiment_counts = {}
    subreddit_activity = {}
    for item in news_items:
        if item['url'] not in stored_urls:
            try:
                processed_item = await process_article(item, sentiment_model)
                if processed_item:
                    await store_article(processed_item)
                    processed_items.append(processed_item)

                    # Aggregate sentiment
                    sentiment = processed_item.get('sentiment', 'neutral')
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

                    # Aggregate subreddit activity
                    subreddit = processed_item.get('subreddit', 'none')
                    subreddit_activity = aggregate_subreddit_activity(subreddit_activity, subreddit)
            except Exception as e:
                logger.error(f"Failed to process or store article: {e}")
        else:
            logger.info(f"Article already stored: {item['url']}")

    logger.info(f"Processed and stored {len(processed_items)} new articles.")

    # Step 4: Summarize sentiment
    sentiment_summary = summarize_sentiment(sentiment_counts)
    logger.info(f"Sentiment Summary: {sentiment_summary}")

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
            
            for reaction in reactions:
                # Remove metadata before storing
                if '_metadata' in reaction:
                    del reaction['_metadata']
                await store_reaction(reaction)
            logger.info(f"Found {len(reactions)} Reddit posts about AI voice")
        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
    else:
        logger.info("Reddit API credentials not configured, skipping Reddit scraping")

    # Update current_run_data to include scanning stats
    current_run_data = {
        'articles_found': len(news_items),
        'articles_processed': len(processed_items),
        'reddit_posts': len(reactions),
        'total_reddit_scanned': total_reddit_scanned,
        'sentiment_summary': sentiment_counts,
        'subreddit_activity': subreddit_activity
    }

    # Update digest creation
    if processed_items or reactions:
        digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': processed_items,
            'reactions': reactions,
            'total_reddit_scanned': total_reddit_scanned
        }

    logger.info("Pipeline execution completed.")

if __name__ == "__main__":
    asyncio.run(main())
