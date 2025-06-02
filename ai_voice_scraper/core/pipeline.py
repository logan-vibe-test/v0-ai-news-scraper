"""
Main pipeline for AI Voice News Scraper
"""
import asyncio
import logging
from datetime import datetime
import os

from ai_voice_scraper.scrapers.news_scraper import scrape_news_sources
from ai_voice_scraper.scrapers.reddit_scraper import scrape_reddit
from ai_voice_scraper.processors.content_processor import process_content
from ai_voice_scraper.storage.db_manager import store_news_item, store_reaction, store_run_summary
from ai_voice_scraper.notifiers.email_notifier import send_email_digest
from ai_voice_scraper.notifiers.slack_notifier import send_slack_digest
from ai_voice_scraper.processors.trends_analyzer import analyze_current_trends
from ai_voice_scraper.config import OPENAI_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, SMTP_SERVER, EMAIL_FROM, EMAIL_TO, SLACK_API_TOKEN

async def run_pipeline(logger, options=None):
    """Run the main pipeline"""
    options = options or {}
    logger.info("🚀 Starting AI Voice News Scraper")
    
    # Step 1: Scrape news
    logger.info("📰 Scraping news sources...")
    try:
        news_items = await scrape_news_sources(test_mode=options.get('test_mode', False))
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
    if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
        logger.info("💬 Scraping Reddit for AI voice topics...")
        try:
            reactions = await scrape_reddit(test_mode=options.get('test_mode', False))
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
            'reactions': reactions
        }
        
        # Email
        if not options.get('skip_email', False) and all([SMTP_SERVER, EMAIL_FROM, EMAIL_TO]):
            try:
                await send_email_digest(digest)
                logger.info("✅ Email sent")
            except Exception as e:
                logger.error(f"Email failed: {e}")
        else:
            logger.info("Email skipped or configuration incomplete")
        
        # Slack
        if not options.get('skip_slack', False) and SLACK_API_TOKEN:
            try:
                await send_slack_digest(digest)
                logger.info("✅ Slack sent")
            except Exception as e:
                logger.error(f"Slack failed: {e}")
        else:
            logger.info("Slack skipped or not configured")
    else:
        logger.info("No content found, skipping notifications")
    
    logger.info("✅ Pipeline complete")
    return {
        "articles_found": len(news_items),
        "articles_processed": len(processed_items),
        "reddit_posts": len(reactions)
    }
