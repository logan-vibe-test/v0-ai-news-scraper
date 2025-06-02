"""
News scraper module for AI Voice News Scraper - Fixed version
"""
import asyncio
import logging
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import feedparser
import ssl
import certifi
import urllib3

logger = logging.getLogger(__name__)

def create_ssl_context():
    """Create a more permissive SSL context for problematic sites"""
    # Create SSL context with certifi for most sites
    context = ssl.create_default_context(cafile=certifi.where())
    
    # Make it slightly more permissive for problematic sites
    context.check_hostname = False
    context.verify_mode = ssl.CERT_OPTIONAL
    
    return context

# Clean news sources without duplicates - WORKING SOURCES
NEWS_SOURCES = [
    # RSS feeds (more reliable than web scraping)
    {
        'name': 'Hacker News',
        'url': 'https://news.ycombinator.com/rss',
        'type': 'rss'
    },
    {
        'name': 'AI News',
        'url': 'https://artificialintelligence-news.com/feed/',
        'type': 'rss'
    },
    {
        'name': 'VentureBeat AI RSS',
        'url': 'https://venturebeat.com/category/ai/feed/',
        'type': 'rss'
    },
    {
        'name': 'TechCrunch AI RSS',
        'url': 'https://techcrunch.com/category/artificial_intelligence/feed/',
        'type': 'rss'
    },
    {
        'name': 'The Verge RSS',
        'url': 'https://www.theverge.com/rss/index.xml',
        'type': 'rss'
    },
    {
        'name': 'Ars Technica RSS',
        'url': 'https://feeds.arstechnica.com/arstechnica/index',
        'type': 'rss'
    },
    {
        'name': 'MIT Technology Review AI',
        'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
        'type': 'rss'
    },
    {
        'name': 'Wired AI RSS',
        'url': 'https://www.wired.com/feed/tag/ai/latest/rss',
        'type': 'rss'
    },
    {
        'name': 'Google AI Blog',
        'url': 'https://ai.googleblog.com/feeds/posts/default',
        'type': 'rss'
    }
]

async def scrape_web_source(session, source):
    """Scrape a web-based news source with SSL handling"""
    try:
        # Create SSL context
        ssl_context = create_ssl_context()
        
        async with session.get(source['url'], timeout=10, ssl=ssl_context) as response:
            if response.status != 200:
                logger.error(f"Error fetching {source['name']}: {response.status}")
                return []
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            articles = []
            elements = soup.select(source['selector'])
            
            logger.info(f"Found {len(elements)} elements from {source['name']}")
            
            for element in elements:
                # Extract data based on source-specific selectors
                title = element.get_text().strip()
                link = element.get('href', '')
                
                # Handle relative URLs
                if link and link.startswith('/'):
                    # Extract domain from source URL
                    domain = '/'.join(source['url'].split('/')[:3])
                    link = domain + link
                
                if title and link and len(title) > 10:  # Basic quality check
                    articles.append({
                        'source': source['name'],
                        'title': title,
                        'url': link,
                        'published_date': datetime.now().isoformat(),
                        'content': '',
                        'raw_html': str(element)
                    })
            
            logger.info(f"Scraped {len(articles)} articles from {source['name']}")
            return articles
    except Exception as e:
        logger.error(f"Error scraping {source['name']}: {str(e)}")
        return []

async def scrape_rss_source(source):
    """Scrape an RSS feed source with better error handling"""
    try:
        # Set user agent for feedparser
        feedparser.USER_AGENT = "AI Voice News Scraper 1.0"
        
        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Use a more permissive approach for problematic domains
        if 'googleblog.com' in source['url']:
            feed = feedparser.parse(source['url'], ssl_verify=False)
        else:
            feed = feedparser.parse(source['url'])
        
        if not feed.entries:
            logger.warning(f"No entries found in RSS feed: {source['name']}")
            return []
        
        articles = []
        for entry in feed.entries:
            # Get published date
            published_date = entry.get('published', entry.get('updated', datetime.now().isoformat()))
            
            articles.append({
                'source': source['name'],
                'title': entry.title,
                'url': entry.link,
                'published_date': published_date,
                'content': entry.get('summary', ''),
                'raw_html': entry.get('summary', '')
            })
        
        logger.info(f"Scraped {len(articles)} articles from {source['name']} RSS")
        return articles
    except Exception as e:
        logger.error(f"Error scraping RSS {source['name']}: {str(e)}")
        return []

async def scrape_news_sources():
    """Scrape all configured news sources"""
    all_articles = []
    
    # Process RSS sources first (more reliable)
    rss_tasks = []
    for source in NEWS_SOURCES:
        if source['type'] == 'rss':
            rss_tasks.append(scrape_rss_source(source))
    
    if rss_tasks:
        logger.info(f"Processing {len(rss_tasks)} RSS sources...")
        rss_results = await asyncio.gather(*rss_tasks, return_exceptions=True)
        for result in rss_results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                logger.error(f"RSS task failed: {result}")
    
    # Process web sources
    ssl_context = create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        web_tasks = []
        for source in NEWS_SOURCES:
            if source['type'] == 'web':
                web_tasks.append(scrape_web_source(session, source))
        
        if web_tasks:
            logger.info(f"Processing {len(web_tasks)} web sources...")
            web_results = await asyncio.gather(*web_tasks, return_exceptions=True)
            for result in web_results:
                if isinstance(result, list):
                    all_articles.extend(result)
                else:
                    logger.error(f"Web task failed: {result}")
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    logger.info(f"Total unique articles scraped: {len(unique_articles)}")
    return unique_articles
