"""
Debug script to trace where articles are being lost in the pipeline
"""
import asyncio
import logging
from ai_voice_scraper.scrapers.news_scraper import scrape_news_sources
from ai_voice_scraper.processors.content_processor import process_content, is_relevant_to_voice_ai, fetch_article_content
from ai_voice_scraper.config.keywords import PRIMARY_VOICE_AI_KEYWORDS, ALL_VOICE_AI_KEYWORDS

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_pipeline():
    """Debug the entire pipeline step by step"""
    print("🔍 DEBUGGING AI VOICE NEWS SCRAPER PIPELINE")
    print("=" * 50)
    
    # Step 1: Test news scraping
    print("\n📰 STEP 1: Testing news scraping...")
    try:
        news_items = await scrape_news_sources(test_mode=True)  # Use test mode for faster debugging
        print(f"✅ Successfully scraped {len(news_items)} articles")
        
        if len(news_items) == 0:
            print("❌ NO ARTICLES SCRAPED - This is the problem!")
            return
        
        # Show first few articles
        print("\n📋 First 3 articles found:")
        for i, item in enumerate(news_items[:3]):
            print(f"  {i+1}. {item['title'][:80]}...")
            print(f"     Source: {item['source']}")
            print(f"     URL: {item['url']}")
            
    except Exception as e:
        print(f"❌ News scraping failed: {e}")
        return
    
    # Step 2: Test content fetching
    print(f"\n🔍 STEP 2: Testing content fetching for first article...")
    test_article = news_items[0]
    try:
        content = await fetch_article_content(test_article['url'])
        if content:
            print(f"✅ Successfully fetched content ({len(content)} characters)")
            print(f"📝 Content preview: {content[:200]}...")
        else:
            print("❌ Failed to fetch article content")
            return
    except Exception as e:
        print(f"❌ Content fetching failed: {e}")
        return
    
    # Step 3: Test keyword matching
    print(f"\n🔑 STEP 3: Testing keyword matching...")
    print(f"Looking for these PRIMARY keywords: {PRIMARY_VOICE_AI_KEYWORDS[:5]}...")
    
    content_lower = content.lower()
    found_keywords = []
    for keyword in PRIMARY_VOICE_AI_KEYWORDS:
        if keyword in content_lower:
            found_keywords.append(keyword)
    
    print(f"Found {len(found_keywords)} primary keywords: {found_keywords}")
    
    # Test relevance
    is_relevant = is_relevant_to_voice_ai(content)
    print(f"Is relevant to voice AI: {is_relevant}")
    
    if not is_relevant:
        print("❌ ARTICLE FILTERED OUT - Keywords too restrictive!")
        print("Let's check what keywords are in the content...")
        
        # Check for any AI-related terms
        ai_terms = ['ai', 'artificial intelligence', 'machine learning', 'voice', 'speech', 'audio']
        found_ai_terms = [term for term in ai_terms if term in content_lower]
        print(f"Found general AI terms: {found_ai_terms}")
    
    # Step 4: Test full processing
    print(f"\n⚙️ STEP 4: Testing full content processing...")
    try:
        processed = await process_content(test_article.copy())
        if processed:
            print("✅ Article successfully processed!")
            print(f"📄 Summary: {processed.get('summary', 'No summary')[:100]}...")
        else:
            print("❌ Article was filtered out during processing")
    except Exception as e:
        print(f"❌ Content processing failed: {e}")
    
    # Step 5: Test with relaxed keywords
    print(f"\n🔧 STEP 5: Testing with relaxed keyword matching...")
    
    def is_relevant_relaxed(text):
        """More relaxed relevance check"""
        text_lower = text.lower()
        relaxed_keywords = [
            'ai', 'voice', 'speech', 'audio', 'tts', 'text-to-speech',
            'openai', 'elevenlabs', 'anthropic', 'google', 'microsoft',
            'assistant', 'chatbot', 'conversation', 'synthesis'
        ]
        
        matches = sum(1 for keyword in relaxed_keywords if keyword in text_lower)
        return matches >= 1
    
    relaxed_relevant = is_relevant_relaxed(content)
    print(f"Would pass with relaxed keywords: {relaxed_relevant}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")

if __name__ == "__main__":
    asyncio.run(debug_pipeline())
