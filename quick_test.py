"""
Quick test to see if we can get ANY articles through the pipeline
"""
import asyncio
import logging
from ai_voice_scraper.scrapers.news_scraper import scrape_news_sources
from ai_voice_scraper.processors.content_processor_relaxed import process_content_relaxed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def quick_test():
    print("🚀 Quick test with relaxed filtering...")
    
    # Get articles
    print("📰 Scraping news...")
    articles = await scrape_news_sources(test_mode=True)
    print(f"Found {len(articles)} raw articles")
    
    if len(articles) == 0:
        print("❌ No articles scraped at all!")
        return
    
    # Process first 3 articles with relaxed filtering
    print("🔍 Processing with relaxed filtering...")
    processed_count = 0
    
    for i, article in enumerate(articles[:5]):  # Test first 5
        print(f"\nProcessing article {i+1}: {article['title'][:60]}...")
        try:
            processed = await process_content_relaxed(article)
            if processed:
                processed_count += 1
                print(f"✅ PASSED: {processed['title'][:60]}...")
            else:
                print(f"❌ FILTERED OUT")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n📊 RESULTS: {processed_count}/{len(articles[:5])} articles passed relaxed filtering")
    
    if processed_count == 0:
        print("🔧 Even relaxed filtering found nothing - checking raw content...")
        # Let's see what's actually in the first article
        first_article = articles[0]
        print(f"First article title: {first_article['title']}")
        print(f"First article URL: {first_article['url']}")
        print(f"First article source: {first_article['source']}")

if __name__ == "__main__":
    asyncio.run(quick_test())
