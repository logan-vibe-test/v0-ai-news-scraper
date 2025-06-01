"""
Script to test and fix CSS selectors for news sources
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Updated news sources with better selectors
UPDATED_NEWS_SOURCES = [
    {
        'name': 'TechCrunch AI',
        'url': 'https://techcrunch.com/category/artificial-intelligence/',
        'type': 'web',
        'selector': 'h2.post-block__title a, h3.post-block__title a'
    },
    {
        'name': 'The Verge AI',
        'url': 'https://www.theverge.com/ai-artificial-intelligence',
        'type': 'web',
        'selector': 'h2 a[data-analytics-link="article"]'
    },
    {
        'name': 'VentureBeat AI',
        'url': 'https://venturebeat.com/ai/',
        'type': 'web',
        'selector': 'h2.ArticleListing__title a, h3.ArticleListing__title a'
    },
    {
        'name': 'Ars Technica AI',
        'url': 'https://arstechnica.com/tag/artificial-intelligence/',
        'type': 'web',
        'selector': 'h2 a, .listing h4 a'
    },
    {
        'name': 'OpenAI Blog',
        'url': 'https://openai.com/blog',
        'type': 'web',
        'selector': 'a[href*="/blog/"]'
    },
    {
        'name': 'Google AI Blog',
        'url': 'https://blog.google/technology/ai/',
        'type': 'web',
        'selector': 'h3 a, .article-card a'
    },
    {
        'name': 'ElevenLabs Blog',
        'url': 'https://elevenlabs.io/blog',
        'type': 'web',
        'selector': 'a[href*="/blog/"]'
    },
    {
        'name': 'Anthropic News',
        'url': 'https://www.anthropic.com/news',
        'type': 'web',
        'selector': 'a[href*="/news/"]'
    },
    {
        'name': 'Hacker News',
        'url': 'https://news.ycombinator.com/rss',
        'type': 'rss'
    },
    {
        'name': 'AI News RSS',
        'url': 'https://artificialintelligence-news.com/feed/',
        'type': 'rss'
    }
]

async def test_and_suggest_selectors(session, source):
    """Test selectors and suggest alternatives if they don't work"""
    print(f"\n{'='*60}")
    print(f"Testing: {source['name']}")
    print(f"URL: {source['url']}")
    print(f"Current selector: {source['selector']}")
    
    try:
        async with session.get(source['url'], timeout=10) as response:
            if response.status != 200:
                print(f"❌ HTTP Error: {response.status}")
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Test current selector
            elements = soup.select(source['selector'])
            print(f"Current selector found: {len(elements)} elements")
            
            if len(elements) > 0:
                print("✅ Current selector works!")
                # Show first few results
                for i, element in enumerate(elements[:3]):
                    title = element.get_text().strip()
                    link = element.get('href', 'No href')
                    print(f"  {i+1}. {title[:60]}... -> {link}")
                return source
            
            # If current selector doesn't work, try alternatives
            print("❌ Current selector doesn't work. Trying alternatives...")
            
            alternative_selectors = [
                'h1 a', 'h2 a', 'h3 a', 'h4 a',
                'article h2 a', 'article h3 a',
                '.post-title a', '.entry-title a',
                '.article-title a', '.headline a',
                'a[href*="/blog/"]', 'a[href*="/news/"]',
                'a[href*="/article/"]', 'a[href*="/post/"]',
                '.post a', '.article a', '.entry a',
                '[class*="title"] a', '[class*="headline"] a'
            ]
            
            best_selector = None
            best_count = 0
            
            for selector in alternative_selectors:
                try:
                    elements = soup.select(selector)
                    count = len(elements)
                    
                    if count > best_count and count <= 50:  # Not too many, not too few
                        # Check if elements actually have meaningful content
                        sample_element = elements[0] if elements else None
                        if sample_element:
                            text = sample_element.get_text().strip()
                            href = sample_element.get('href', '')
                            
                            # Basic quality check
                            if len(text) > 10 and href:
                                best_selector = selector
                                best_count = count
                                print(f"  {selector}: {count} elements ✓")
                            else:
                                print(f"  {selector}: {count} elements (low quality)")
                    elif count > 0:
                        print(f"  {selector}: {count} elements")
                except:
                    pass
            
            if best_selector:
                print(f"🔧 Suggested selector: {best_selector} ({best_count} elements)")
                
                # Test the suggested selector
                elements = soup.select(best_selector)
                print("Sample results:")
                for i, element in enumerate(elements[:3]):
                    title = element.get_text().strip()
                    link = element.get('href', 'No href')
                    print(f"  {i+1}. {title[:60]}... -> {link}")
                
                # Return updated source
                updated_source = source.copy()
                updated_source['selector'] = best_selector
                return updated_source
            else:
                print("❌ No good alternative selectors found")
                return None
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def main():
    """Test all selectors and generate updated configuration"""
    print("Testing and fixing CSS selectors for news sources")
    
    working_sources = []
    
    async with aiohttp.ClientSession() as session:
        for source in UPDATED_NEWS_SOURCES:
            if source['type'] == 'web':
                result = await test_and_suggest_selectors(session, source)
                if result:
                    working_sources.append(result)
            else:  # RSS
                print(f"\n{'='*60}")
                print(f"RSS Source: {source['name']} - {source['url']}")
                working_sources.append(source)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Working sources: {len(working_sources)}")
    
    # Generate updated NEWS_SOURCES for the scraper
    print("\nUpdated NEWS_SOURCES configuration:")
    print("NEWS_SOURCES = [")
    for source in working_sources:
        print(f"    {{")
        print(f"        'name': '{source['name']}',")
        print(f"        'url': '{source['url']}',")
        print(f"        'type': '{source['type']}',")
        if source['type'] == 'web':
            print(f"        'selector': '{source['selector']}'")
        print(f"    }},")
    print("]")

if __name__ == "__main__":
    asyncio.run(main())
