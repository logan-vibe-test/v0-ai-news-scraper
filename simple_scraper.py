"""
Simplified scraper that just gets articles without complex filtering
"""
import asyncio
import logging
import sys
import aiohttp
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Simple list of news sources
SIMPLE_SOURCES = [
    # General tech news
    {
        'name': 'TechCrunch',
        'url': 'https://techcrunch.com',
        'type': 'web',
        'selector': 'article h2 a'
    },
    {
        'name': 'The Verge',
        'url': 'https://www.theverge.com',
        'type': 'web',
        'selector': 'h2 a'
    },
    # Voice AI specific
    {
        'name': 'ElevenLabs Blog',
        'url': 'https://elevenlabs.io/blog',
        'type': 'web',
        'selector': 'a.blog-card'
    },
    # RSS feeds
    {
        'name': 'Hacker News',
        'url': 'https://news.ycombinator.com/rss',
        'type': 'rss'
    },
    {
        'name': 'AI News',
        'url': 'https://artificialintelligence-news.com/feed/',
        'type': 'rss'
    }
]

async def simple_web_scrape(session, source):
    """Simple web scraper without complex error handling"""
    try:
        async with session.get(source['url']) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                articles = []
                elements = soup.select(source['selector'])
                
                logger.info(f"Found {len(elements)} elements from {source['name']}")
                
                for element in elements[:5]:  # Just get the first 5
                    title = element.get_text().strip()
                    link = element.get('href', '')
                    
                    # Handle relative URLs
                    if link and link.startswith('/'):
                        domain = '/'.join(source['url'].split('/')[:3])
                        link = domain + link
                    
                    if title and link:
                        articles.append({
                            'source': source['name'],
                            'title': title,
                            'url': link
                        })
                        logger.info(f"Article: {title} - {link}")
                
                return articles
            else:
                logger.error(f"Failed to fetch {source['name']}: HTTP {response.status}")
                return []
    except Exception as e:
        logger.error(f"Error scraping {source['name']}: {str(e)}")
        return []

async def simple_rss_scrape(source):
    """Simple RSS scraper"""
    try:
        feed = feedparser.parse(source['url'])
        
        articles = []
        for entry in feed.entries[:5]:  # Just get the first 5
            title = entry.title
            link = entry.link
            
            articles.append({
                'source': source['name'],
                'title': title,
                'url': link
            })
            logger.info(f"RSS Article: {title} - {link}")
        
        return articles
    except Exception as e:
        logger.error(f"Error scraping RSS {source['name']}: {str(e)}")
        return []

async def run_simple_scraper():
    """Run the simple scraper"""
    logger.info("Starting simple scraper")
    
    all_articles = []
    
    async with aiohttp.ClientSession() as session:
        for source in SIMPLE_SOURCES:
            logger.info(f"Scraping {source['name']} from {source['url']}")
            
            if source['type'] == 'web':
                articles = await simple_web_scrape(session, source)
            else:  # RSS
                articles = await simple_rss_scrape(source)
            
            all_articles.extend(articles)
    
    logger.info(f"Total articles found: {len(all_articles)}")
    
    # Print all articles
    for i, article in enumerate(all_articles):
        print(f"{i+1}. {article['source']} - {article['title']}")
        print(f"   URL: {article['url']}")
        print()
    
    return all_articles

if __name__ == "__main__":
    asyncio.run(run_simple_scraper())
