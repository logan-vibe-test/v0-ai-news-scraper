"""
Debug script to identify issues with the AI Voice News Scraper
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
from bs4 import BeautifulSoup
import json

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import scraper modules
from scrapers.news_scraper import NEWS_SOURCES, scrape_web_source, scrape_rss_source

async def debug_web_scraping():
    """Debug the web scraping functionality"""
    logger.info("=== DEBUGGING WEB SCRAPING ===")
    
    # Test each news source individually
    async with aiohttp.ClientSession() as session:
        for source in NEWS_SOURCES:
            if source['type'] == 'web':
                logger.info(f"Testing source: {source['name']} - {source['url']}")
                
                try:
                    # First, just try to fetch the URL
                    async with session.get(source['url']) as response:
                        status = response.status
                        logger.info(f"HTTP Status: {status}")
                        
                        if status != 200:
                            logger.error(f"Failed to fetch {source['name']}: HTTP {status}")
                            continue
                        
                        # Get the HTML content
                        html = await response.text()
                        logger.info(f"Received {len(html)} bytes of HTML")
                        
                        # Parse with BeautifulSoup
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Try to find elements using the selector
                        elements = soup.select(source['selector'])
                        logger.info(f"Found {len(elements)} elements matching selector: {source['selector']}")
                        
                        if len(elements) == 0:
                            logger.error(f"Selector '{source['selector']}' found no elements!")
                            logger.info("First 500 chars of HTML:")
                            logger.info(html[:500])
                            
                            # Try some common selectors as a fallback
                            common_selectors = ['article', 'div.post', '.article', '.entry', 'h2 a']
                            logger.info("Trying common selectors as fallback:")
                            for selector in common_selectors:
                                elements = soup.select(selector)
                                logger.info(f"  {selector}: {len(elements)} elements")
                        else:
                            # Show the first element found
                            logger.info("First element found:")
                            logger.info(str(elements[0])[:200])
                            
                            # Try to extract title and link
                            title_element = elements[0].find(['h1', 'h2', 'h3']) or elements[0]
                            link_element = elements[0].find('a') or elements[0]
                            
                            title = title_element.get_text().strip() if title_element else "No title found"
                            link = link_element.get('href', '') if link_element else "No link found"
                            
                            logger.info(f"Title: {title}")
                            logger.info(f"Link: {link}")
                    
                    # Now try the actual scraper function
                    logger.info("Testing scraper function...")
                    articles = await scrape_web_source(session, source)
                    logger.info(f"Scraper returned {len(articles)} articles")
                    
                    if articles:
                        logger.info("First article:")
                        logger.info(json.dumps(articles[0], indent=2))
                    
                except Exception as e:
                    logger.error(f"Error testing {source['name']}: {str(e)}")
            
            elif source['type'] == 'rss':
                logger.info(f"Testing RSS source: {source['name']} - {source['url']}")
                
                try:
                    articles = await scrape_rss_source(source)
                    logger.info(f"RSS scraper returned {len(articles)} articles")
                    
                    if articles:
                        logger.info("First article:")
                        logger.info(json.dumps(articles[0], indent=2))
                        
                except Exception as e:
                    logger.error(f"Error testing RSS {source['name']}: {str(e)}")
            
            logger.info("-" * 50)

async def debug_content_processing():
    """Debug the content processing functionality"""
    logger.info("=== DEBUGGING CONTENT PROCESSING ===")
    
    # Import the necessary functions
    from processors.content_processor import fetch_article_content, is_relevant_to_voice_ai
    from config.keywords import PRIMARY_VOICE_AI_KEYWORDS, ALL_VOICE_AI_KEYWORDS
    
    # Log the keywords being used
    logger.info(f"Primary keywords: {PRIMARY_VOICE_AI_KEYWORDS}")
    logger.info(f"Total keywords: {len(ALL_VOICE_AI_KEYWORDS)}")
    
    # Test with a known voice AI article
    test_urls = [
        "https://elevenlabs.io/blog/eleven-multilingual-v2/",
        "https://openai.com/blog/new-models-and-developer-products-announced-at-devday",
        "https://www.theverge.com/2023/11/6/23948426/openai-gpt4-turbo-assistant-api-devday"
    ]
    
    for url in test_urls:
        logger.info(f"Testing content processing with URL: {url}")
        
        try:
            # Fetch the content
            content = await fetch_article_content(url)
            
            if not content:
                logger.error(f"Failed to fetch content from {url}")
                continue
                
            logger.info(f"Fetched {len(content)} characters of content")
            logger.info(f"First 200 chars: {content[:200]}")
            
            # Check relevance
            is_relevant = is_relevant_to_voice_ai(content)
            logger.info(f"Is relevant: {is_relevant}")
            
            # Check which keywords were found
            content_lower = content.lower()
            found_primary = [kw for kw in PRIMARY_VOICE_AI_KEYWORDS if kw in content_lower]
            found_all = [kw for kw in ALL_VOICE_AI_KEYWORDS if kw in content_lower]
            
            logger.info(f"Found primary keywords: {found_primary}")
            logger.info(f"Found all keywords: {found_all}")
            
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
        
        logger.info("-" * 50)

async def debug_with_manual_article():
    """Debug with a manually created article"""
    logger.info("=== DEBUGGING WITH MANUAL ARTICLE ===")
    
    # Import necessary functions
    from processors.content_processor import process_content, is_relevant_to_voice_ai
    
    # Create a test article with known voice AI content
    test_article = {
        'title': 'New Voice AI Technology Released',
        'url': 'https://example.com/test-article',
        'source': 'Test Source',
        'published_date': datetime.now().isoformat(),
        'content': """
        A new voice AI technology has been released today that promises to revolutionize
        text-to-speech capabilities. The new system uses advanced neural networks to generate
        highly realistic voice synthesis that can mimic human speech patterns with unprecedented
        accuracy. This voice generation technology will be available through an API for developers.
        
        The voice cloning capabilities allow users to create custom voices with just a few minutes
        of sample audio. This has applications in audiobook production, accessibility tools, and
        customer service automation.
        """,
        'raw_html': '<div>Test HTML</div>'
    }
    
    logger.info("Testing with manually created article")
    logger.info(f"Title: {test_article['title']}")
    
    # Check relevance directly
    is_relevant = is_relevant_to_voice_ai(test_article['content'])
    logger.info(f"Is relevant (direct check): {is_relevant}")
    
    # Process the article
    try:
        processed = await process_content(test_article)
        
        if processed:
            logger.info("Article was processed successfully")
            logger.info(f"Summary: {processed.get('summary', 'No summary')}")
        else:
            logger.error("Article was rejected during processing")
        
    except Exception as e:
        logger.error(f"Error processing manual article: {str(e)}")

async def main():
    """Run all debugging functions"""
    logger.info("Starting AI Voice News Scraper Debugging")
    
    # Debug web scraping
    await debug_web_scraping()
    
    # Debug content processing
    await debug_content_processing()
    
    # Debug with manual article
    await debug_with_manual_article()
    
    logger.info("Debugging completed")

if __name__ == "__main__":
    asyncio.run(main())
