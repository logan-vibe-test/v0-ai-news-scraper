"""
Debug script to identify why no articles are being returned
"""
import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("debug")

# Import components
from ai_voice_scraper.scrapers.news_scraper import scrape_news_sources, NEWS_SOURCES
from ai_voice_scraper.processors.content_processor import process_content, is_relevant_to_voice_ai
from ai_voice_scraper.config.keywords import PRIMARY_VOICE_AI_KEYWORDS, ALL_VOICE_AI_KEYWORDS

async def debug_news_sources():
    """Debug individual news sources"""
    logger.info("🔍 Debugging individual news sources...")
    
    for i, source in enumerate(NEWS_SOURCES):
        logger.info(f"Testing source {i+1}/{len(NEWS_SOURCES)}: {source['name']} ({source['type']})")
        
        try:
            if source['type'] == 'rss':
                from ai_voice_scraper.scrapers.news_scraper import scrape_rss_source
                articles = await scrape_rss_source(source)
            else:
                import aiohttp
                from ai_voice_scraper.scrapers.news_scraper import scrape_web_source, create_ssl_context
                
                ssl_context = create_ssl_context()
                connector = aiohttp.TCPConnector(ssl=ssl_context, verify_ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    articles = await scrape_web_source(session, source)
            
            logger.info(f"✅ {source['name']}: Found {len(articles)} articles")
            
            if articles:
                logger.info(f"  Sample: {articles[0]['title'][:60]}...")
            else:
                logger.warning(f"  No articles found from {source['name']}")
                
        except Exception as e:
            logger.error(f"❌ {source['name']} failed: {str(e)}")
    
    logger.info("Individual source testing complete")

async def debug_content_processor():
    """Debug content processor with sample articles"""
    logger.info("🔍 Debugging content processor...")
    
    # Get some articles first
    logger.info("Fetching sample articles...")
    all_articles = await scrape_news_sources(test_mode=True)
    
    if not all_articles:
        logger.error("❌ No articles found to test content processor")
        return
    
    logger.info(f"Testing content processor with {len(all_articles)} articles")
    
    for i, article in enumerate(all_articles[:5]):  # Test first 5 articles
        logger.info(f"Processing article {i+1}: {article['title']}")
        
        # Test keyword matching directly
        content = article.get('content', '')
        if not content and 'url' in article:
            from ai_voice_scraper.processors.content_processor import fetch_article_content
            logger.info(f"Fetching content from {article['url']}")
            content = await fetch_article_content(article['url'])
            if content:
                logger.info(f"Content fetched: {len(content)} characters")
                article['content'] = content
            else:
                logger.warning(f"Could not fetch content for {article['url']}")
        
        # Check relevance
        if content:
            is_relevant = is_relevant_to_voice_ai(content)
            logger.info(f"Relevance check: {'✅ RELEVANT' if is_relevant else '❌ NOT RELEVANT'}")
            
            # Count keyword matches
            content_lower = content.lower()
            primary_matches = [kw for kw in PRIMARY_VOICE_AI_KEYWORDS if kw in content_lower]
            all_matches = [kw for kw in ALL_VOICE_AI_KEYWORDS if kw in content_lower]
            
            logger.info(f"Primary keyword matches: {len(primary_matches)}")
            if primary_matches:
                logger.info(f"  Matched: {', '.join(primary_matches[:5])}")
            
            logger.info(f"All keyword matches: {len(all_matches)}")
            if all_matches:
                logger.info(f"  Matched: {', '.join(all_matches[:5])}")
        else:
            logger.warning("No content available to check relevance")
    
    logger.info("Content processor testing complete")

async def debug_full_pipeline():
    """Debug the full pipeline with verbose logging"""
    logger.info("🚀 Starting full pipeline debug...")
    
    # Step 1: Scrape news
    logger.info("📰 Scraping news sources...")
    news_items = await scrape_news_sources()
    logger.info(f"Found {len(news_items)} articles")
    
    if not news_items:
        logger.error("❌ No articles found - check news sources")
        return
    
    # Step 2: Process content
    logger.info("🔍 Processing content...")
    processed_items = []
    for item in news_items:
        try:
            logger.info(f"Processing: {item['title']}")
            processed = await process_content(item)
            if processed:
                processed_items.append(processed)
                logger.info(f"✅ Article relevant: {item['title']}")
            else:
                logger.info(f"❌ Article not relevant: {item['title']}")
        except Exception as e:
            logger.error(f"Error processing {item.get('title', 'Unknown')}: {e}")
    
    logger.info(f"Processed {len(processed_items)} relevant articles")
    
    # Print results
    if processed_items:
        logger.info("\n🎯 RELEVANT ARTICLES FOUND:")
        for i, item in enumerate(processed_items):
            logger.info(f"{i+1}. {item['title']}")
            logger.info(f"   Source: {item['source']}")
            logger.info(f"   URL: {item['url']}")
            if 'summary' in item:
                logger.info(f"   Summary: {item['summary'][:100]}...")
            logger.info("")
    else:
        logger.error("❌ NO RELEVANT ARTICLES FOUND - check keyword filtering")

async def main():
    """Main debug function"""
    print("\n==== AI VOICE NEWS SCRAPER DEBUGGER ====\n")
    print("1. Debug news sources")
    print("2. Debug content processor")
    print("3. Debug full pipeline")
    print("4. Run all debug tests")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        await debug_news_sources()
    elif choice == '2':
        await debug_content_processor()
    elif choice == '3':
        await debug_full_pipeline()
    elif choice == '4':
        await debug_news_sources()
        await debug_content_processor()
        await debug_full_pipeline()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
