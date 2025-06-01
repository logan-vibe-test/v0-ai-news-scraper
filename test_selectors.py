"""
Test script to check if the CSS selectors for each news source are working
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

# Import the news sources
from scrapers.news_scraper import NEWS_SOURCES

async def test_selector(session, source):
    """Test if a selector works for a given source"""
    print(f"\n=== Testing {source['name']} ===")
    print(f"URL: {source['url']}")
    print(f"Selector: {source['selector']}")
    
    try:
        async with session.get(source['url']) as response:
            if response.status != 200:
                print(f"❌ Failed to fetch URL: HTTP {response.status}")
                return False
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            elements = soup.select(source['selector'])
            
            if not elements:
                print(f"❌ Selector found 0 elements")
                
                # Try some common selectors
                common_selectors = ['article', 'h2 a', '.post', '.article', '.entry']
                print("Trying common selectors:")
                for selector in common_selectors:
                    count = len(soup.select(selector))
                    print(f"  {selector}: {count} elements")
                
                return False
            
            print(f"✅ Selector found {len(elements)} elements")
            
            # Show the first 3 elements
            for i, element in enumerate(elements[:3]):
                title_element = element.find(['h1', 'h2', 'h3']) or element
                link_element = element.find('a') or element
                
                title = title_element.get_text().strip()
                link = link_element.get('href', '') if link_element else "No link"
                
                print(f"  {i+1}. {title[:50]}... - {link}")
            
            return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    """Test all selectors"""
    print("Testing CSS selectors for all news sources")
    
    async with aiohttp.ClientSession() as session:
        for source in NEWS_SOURCES:
            if source['type'] == 'web':
                await test_selector(session, source)

if __name__ == "__main__":
    asyncio.run(main())
