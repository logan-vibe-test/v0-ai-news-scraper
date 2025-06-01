"""
Better news sources with more reliable selectors and RSS feeds
"""

# More reliable news sources focused on AI and tech
BETTER_NEWS_SOURCES = [
    # RSS feeds are more reliable than web scraping
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
    
    # Company blogs (web scraping)
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
        'selector': 'h2.post-title a'
    },
    {
        'name': 'DeepMind Blog',
        'url': 'https://deepmind.com/blog',
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
        'name': 'ElevenLabs Blog',
        'url': 'https://elevenlabs.io/blog',
        'type': 'web',
        'selector': 'a[href*="/blog/"]'
    }
]

async def test_better_sources():
    """Test the better news sources"""
    import asyncio
    import aiohttp
    import feedparser
    from bs4 import BeautifulSoup
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    async def test_rss_source(source):
        """Test RSS source"""
        try:
            feed = feedparser.parse(source['url'])
            articles = []
            
            for entry in feed.entries[:5]:  # Get first 5
                articles.append({
                    'source': source['name'],
                    'title': entry.title,
                    'url': entry.link,
                    'published': entry.get('published', 'Unknown')
                })
            
            logger.info(f"✅ {source['name']}: {len(articles)} articles")
            for article in articles:
                logger.info(f"   - {article['title'][:60]}...")
            
            return articles
        except Exception as e:
            logger.error(f"❌ {source['name']}: {str(e)}")
            return []
    
    async def test_web_source(session, source):
        """Test web source"""
        try:
            async with session.get(source['url']) as response:
                if response.status != 200:
                    logger.error(f"❌ {source['name']}: HTTP {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                elements = soup.select(source['selector'])
                
                articles = []
                for element in elements[:5]:  # Get first 5
                    title = element.get_text().strip()
                    link = element.get('href', '')
                    
                    if link and link.startswith('/'):
                        domain = '/'.join(source['url'].split('/')[:3])
                        link = domain + link
                    
                    if title and link:
                        articles.append({
                            'source': source['name'],
                            'title': title,
                            'url': link
                        })
                
                logger.info(f"✅ {source['name']}: {len(articles)} articles")
                for article in articles:
                    logger.info(f"   - {article['title'][:60]}...")
                
                return articles
        except Exception as e:
            logger.error(f"❌ {source['name']}: {str(e)}")
            return []
    
    all_articles = []
    
    # Test RSS sources
    for source in BETTER_NEWS_SOURCES:
        if source['type'] == 'rss':
            articles = await test_rss_source(source)
            all_articles.extend(articles)
    
    # Test web sources
    async with aiohttp.ClientSession() as session:
        for source in BETTER_NEWS_SOURCES:
            if source['type'] == 'web':
                articles = await test_web_source(session, source)
                all_articles.extend(articles)
    
    logger.info(f"\nTotal articles found: {len(all_articles)}")
    return all_articles

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_better_sources())
