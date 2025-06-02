"""
Simple test script to verify the news scraper is working
"""
import ssl
import logging
import urllib3
import asyncio

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Import after SSL configuration
from ai_voice_scraper.scrapers.news_scraper import scrape_news_sources
from ai_voice_scraper.processors.content_processor import is_relevant_to_voice_ai

async def main():
    print("Starting news scraper test...")
    
    # Fetch articles
    print("Fetching articles...")
    articles = await scrape_news_sources(test_mode=True)  # Use test mode to limit sources
    
    print(f"Found {len(articles)} raw articles")
    
    # Process each article
    relevant_articles = []
    for i, article in enumerate(articles[:20]):  # Process first 20 only
        print(f"\nArticle {i+1}:")
        print(f"Title: {article.get('title', 'No title')}")
        print(f"URL: {article.get('url', 'No URL')}")
        
        # Check relevance
        content = article.get('title', '') + ' ' + article.get('content', '')
        is_relevant = is_relevant_to_voice_ai(content)
        print(f"Relevant to voice AI: {is_relevant}")
        
        if is_relevant:
            relevant_articles.append(article)
    
    print(f"\nFound {len(relevant_articles)} relevant articles out of {len(articles)} total")
    
    if relevant_articles:
        print("\nFirst relevant article:")
        print(f"Title: {relevant_articles[0].get('title', 'No title')}")
        print(f"URL: {relevant_articles[0].get('url', 'No URL')}")
        print(f"Content: {relevant_articles[0].get('content', 'No content')[:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
