"""
News scraper module for AI Voice News Scraper
"""
import asyncio
import logging
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import feedparser

logger = logging.getLogger(__name__)

# Define news sources
NEWS_SOURCES = [
    {
        'name': 'TechCrunch',
        'url': 'https://techcrunch.com/category/artificial-intelligence/',
        'type': 'web',
        'selector': 'article.post-block'
    },
    {
        'name': 'The Verge',
        'url': 'https://www.theverge.com/ai-artificial-intelligence',
        'type': 'web',
        'selector': 'div.duet--content-cards--content-card'
    },
    {
        'name': 'VentureBeat',
        'url': 'https://venturebeat.com/category/ai/',
        'type': 'web',
        'selector': 'article.Article'
    },
    {
        'name': 'ArsTechnica',
        'url': 'https://arstechnica.com/tag/artificial-intelligence/',
        'type': 'web',
        'selector': 'article.article'
    },
    {
        'name': 'OpenAI Blog',
        'url': 'https://openai.com/blog',
        'type': 'web',
        'selector': 'a.ui-link'
    },
    {
        'name': 'Google AI Blog',
        'url': 'https://blog.google/technology/ai/',
        'type': 'web',
        'selector': 'a.article-card'
    },
    {
        'name': 'ElevenLabs Blog',
        'url': 'https://elevenlabs.io/blog',
        'type': 'web',
        'selector': 'div.blog-post'
    },
    {
        'name': 'Hacker News',
        'url': 'https://news.ycombinator.com/rss',
        'type': 'rss'
    }
]

async def scrape_web_source(session, source):
    """Scrape a web-based news source"""
    try:
        async with session.get(source['url']) as response:
            if response.status != 200:
                logger.error(f"Error fetching {source['name']}: {response.status}")
                return []
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            articles = []
            for element in soup.select(source['selector']):
                # Extract data based on source-specific selectors
                # This is simplified and would need customization per site
                title_element = element.find(['h1', 'h2', 'h3']) or element
                link_element = element.find('a') or element
                
                title = title_element.get_text().strip()
                link = link_element.get('href', '')
                
                # Handle relative URLs
                if link and link.startswith('/'):
                    # Extract domain from source URL
                    domain = '/'.join(source['url'].split('/')[:3])
                    link = domain + link
                
                if title and link:
                    articles.append({
                        'source': source['name'],
                        'title': title,
                        'url': link,
                        'published_date': datetime.now().isoformat(),  # Placeholder, would extract from page
                        'content': '',  # Will be filled when processing
                        'raw_html': str(element)
                    })
            
            logger.info(f"Scraped {len(articles)} articles from {source['name']}")
            return articles
    except Exception as e:
        logger.error(f"Error scraping {source['name']}: {str(e)}")
        return []

async def scrape_rss_source(source):
    """Scrape an RSS feed source"""
    try:
        feed = feedparser.parse(source['url'])
        
        articles = []
        for entry in feed.entries:
            articles.append({
                'source': source['name'],
                'title': entry.title,
                'url': entry.link,
                'published_date': entry.get('published', datetime.now().isoformat()),
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
    
    async with aiohttp.ClientSession() as session:
        web_tasks = []
        rss_tasks = []
        
        # Create tasks for each source
        for source in NEWS_SOURCES:
            if source['type'] == 'web':
                web_tasks.append(scrape_web_source(session, source))
            elif source['type'] == 'rss':
                rss_tasks.append(scrape_rss_source(source))
        
        # Gather web scraping results
        if web_tasks:
            web_results = await asyncio.gather(*web_tasks)
            for result in web_results:
                all_articles.extend(result)
        
        # Gather RSS results
        if rss_tasks:
            rss_results = await asyncio.gather(*rss_tasks)
            for result in rss_results:
                all_articles.extend(result)
    
    logger.info(f"Total articles scraped: {len(all_articles)}")
    return all_articles
