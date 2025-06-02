"""
Simple test script with VERY lenient relevance filtering
"""
import ssl
import logging
import urllib3
import asyncio
import re

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
from ai_voice_scraper.config.keywords import PRIMARY_VOICE_AI_KEYWORDS, ALL_VOICE_AI_KEYWORDS, CONTEXT_KEYWORDS

# Super lenient relevance check - just look for ANY keyword
def super_lenient_relevance_check(text):
    """Check if text contains ANY voice AI related term"""
    text_lower = text.lower()
    
    # Check for ANY voice AI keyword
    for keyword in ALL_VOICE_AI_KEYWORDS:
        if keyword.lower() in text_lower:
            print(f"MATCH FOUND: '{keyword}' in text")
            return True
            
    # Check for ANY AI-related term
    ai_terms = ["ai", "artificial intelligence", "machine learning", "neural", "model"]
    for term in ai_terms:
        if term in text_lower:
            print(f"AI TERM FOUND: '{term}' in text")
            return True
    
    return False

async def main():
    print("Starting news scraper test with LENIENT filtering...")
    
    # Fetch articles
    print("Fetching articles...")
    articles = await scrape_news_sources(test_mode=True)
    
    print(f"Found {len(articles)} raw articles")
    
    # Print all article titles
    print("\nALL ARTICLE TITLES:")
    for i, article in enumerate(articles):
        print(f"{i+1}. {article.get('title', 'No title')}")
    
    # Process each article with LENIENT filtering
    relevant_articles = []
    for i, article in enumerate(articles):
        title = article.get('title', '')
        content = article.get('content', '')
        full_text = title + ' ' + content
        
        # Use super lenient relevance check
        is_relevant = super_lenient_relevance_check(full_text)
        
        if is_relevant:
            print(f"\nRELEVANT ARTICLE FOUND: {title}")
            relevant_articles.append(article)
    
    print(f"\nFound {len(relevant_articles)} relevant articles out of {len(articles)} total")
    
    if relevant_articles:
        print("\nFirst relevant article:")
        print(f"Title: {relevant_articles[0].get('title', 'No title')}")
        print(f"URL: {relevant_articles[0].get('url', 'No URL')}")
        print(f"Content: {relevant_articles[0].get('content', 'No content')[:200]}...")
    else:
        print("\nNo relevant articles found. Let's check for ANY AI content...")
        
        # Look for ANY AI content
        ai_articles = []
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            if 'ai' in title.lower() or 'ai' in content.lower():
                ai_articles.append(article)
        
        print(f"Found {len(ai_articles)} articles with 'AI' mentioned")
        if ai_articles:
            print(f"Example: {ai_articles[0].get('title', 'No title')}")

if __name__ == "__main__":
    asyncio.run(main())
