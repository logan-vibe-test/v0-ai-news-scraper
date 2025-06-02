"""
News scraper module for AI Voice News Scraper
"""
import asyncio
import logging
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import feedparser
import ssl
import certifi
import urllib3
import re
import random

logger = logging.getLogger(__name__)

def create_ssl_context():
    """Create a more permissive SSL context for problematic sites"""
    # Create SSL context with certifi for most sites
    context = ssl.create_default_context(cafile=certifi.where())
    
    # Make it slightly more permissive for problematic sites
    context.check_hostname = False
    context.verify_mode = ssl.CERT_OPTIONAL
    
    return context

# Clean news sources without duplicates
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
        'url': 'https://techcrunch.com/category/artificial-intelligence/feed/',
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
    # General tech news that might cover voice AI
    {
        'name': 'TechRadar',
        'url': 'https://www.techradar.com/rss',
        'type': 'rss'
    },
    {
        'name': 'Engadget',
        'url': 'https://www.engadget.com/rss.xml',
        'type': 'rss'
    },
    {
        'name': 'CNET',
        'url': 'https://www.cnet.com/rss/news/',
        'type': 'rss'
    },
    # Company blogs (web scraping as backup)
    {
        'name': 'OpenAI Blog',
        'url': 'https://openai.com/blog',
        'type': 'web',
        'selector': 'a[href*="/blog/"]'
    },
    {
        'name': 'Google AI Blog',
        'url': 'https://ai.googleblog.com/',
        'type': 'web',
        'selector': 'div.post'
    },
    {
        'name': 'Anthropic Blog',
        'url': 'https://www.anthropic.com/news',
        'type': 'web',
        'selector': 'a[href*="/news/"]'
    },
    {
        'name': 'ElevenLabs Blog',
        'url': 'https://elevenlabs.io/blog',
        'type': 'web',
        'selector': 'a[href*="/blog/"]'
    },
    {
        'name': 'Resemble AI Blog',
        'url': 'https://www.resemble.ai/blog/',
        'type': 'web',
        'selector': 'article'
    }
]

# User agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

async def scrape_web_source(session, source):
    """Scrape a web-based news source with SSL handling"""
    try:
        # Create SSL context
        ssl_context = create_ssl_context()
        
        # Special handling for problematic domains
        ssl_verify = True
        if any(domain in source['url'] for domain in ['googleblog.com', 'ai.google']):
            ssl_verify = False
        
        # Use random user agent
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        async with session.get(
            source['url'], 
            timeout=15, 
            ssl=ssl_context, 
            verify_ssl=ssl_verify,
            headers=headers
        ) as response:
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
                title_element = element.find('h1') or element.find('h2') or element.find('h3') or element
                title = title_element.get_text().strip()
                
                # Find link - either the element itself is a link, or it contains a link
                link = None
                if element.name == 'a':
                    link = element.get('href', '')
                else:
                    link_element = element.find('a')
                    if link_element:
                        link = link_element.get('href', '')
                
                # Handle relative URLs
                if link and link.startswith('/'):
                    # Extract domain from source URL
                    domain = '/'.join(source['url'].split('/')[:3])
                    link = domain + link
                
                if title and link and len(title) > 5:  # Less restrictive quality check
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
        feedparser.USER_AGENT = random.choice(USER_AGENTS)
        
        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Use a more permissive approach for problematic domains
        if any(domain in source['url'] for domain in ['googleblog.com', 'ai.google']):
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
            
            # Get content
            content = ''
            if 'content' in entry:
                content = entry.content[0].value
            elif 'summary' in entry:
                content = entry.summary
            
            # Skip entries older than 7 days
            try:
                if 'published_parsed' in entry and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if datetime.now() - pub_date > timedelta(days=7):
                        continue
            except Exception:
                # If date parsing fails, include the entry anyway
                pass
            
            articles.append({
                'source': source['name'],
                'title': entry.title,
                'url': entry.link,
                'published_date': published_date,
                'content': content,
                'raw_html': content
            })
        
        logger.info(f"Scraped {len(articles)} articles from {source['name']} RSS")
        return articles
    except Exception as e:
        logger.error(f"Error scraping RSS {source['name']}: {str(e)}")
        return []

async def scrape_news_sources(test_mode=False):
    """Scrape all configured news sources"""
    all_articles = []
    
    # Limit sources in test mode
    sources = NEWS_SOURCES[:5] if test_mode else NEWS_SOURCES
    
    # Process RSS sources first (more reliable)
    rss_tasks = []
    for source in sources:
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
    connector = aiohttp.TCPConnector(ssl=ssl_context, verify_ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        web_tasks = []
        for source in sources:
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
