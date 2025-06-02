"""
Content processor for AI Voice News Scraper
"""
import logging
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import ssl
import certifi
import random
from datetime import datetime

from ai_voice_scraper.config import OPENAI_API_KEY
from ai_voice_scraper.config.keywords import PRIMARY_VOICE_AI_KEYWORDS, ALL_VOICE_AI_KEYWORDS, CONTEXT_KEYWORDS

logger = logging.getLogger(__name__)

# User agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

async def fetch_article_content(url):
    """Fetch the full content of an article"""
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_OPTIONAL
        
        connector = aiohttp.TCPConnector(ssl=ssl_context, verify_ssl=False)
        
        # Use random user agent
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=15, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Error fetching article: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading and trailing space
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Remove blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
    except Exception as e:
        logger.error(f"Error fetching article content: {str(e)}")
        return None

def is_relevant_to_voice_ai(text):
    """Check if the content is relevant to voice AI with LESS restrictive logic"""
    if not text:
        return False
        
    text_lower = text.lower()
    
    # Check for primary keyword matches (must have at least one)
    primary_matches = [kw for kw in PRIMARY_VOICE_AI_KEYWORDS if kw in text_lower]
    
    # If we have ANY primary match, consider it relevant
    if primary_matches:
        logger.info(f"Found primary voice AI keywords: {', '.join(primary_matches[:3])}")
        return True
    
    # Check for multiple secondary matches
    all_keyword_matches = [kw for kw in ALL_VOICE_AI_KEYWORDS if kw in text_lower]
    
    # If we have multiple secondary matches, consider it relevant
    if len(all_keyword_matches) >= 2:
        logger.info(f"Found multiple voice AI keywords: {', '.join(all_keyword_matches[:3])}")
        return True
    
    # Not relevant
    return False

async def simple_summarize(content, title):
    """Simple text summarization without OpenAI"""
    if not content:
        return "No content available for summary"
    
    # Clean the text
    content = content.replace('\n', ' ').replace('\r', ' ')
    
    # Split into sentences
    sentences = []
    for delimiter in ['. ', '! ', '? ']:
        content = content.replace(delimiter, '|||SPLIT|||')
    
    potential_sentences = content.split('|||SPLIT|||')
    for sentence in potential_sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Only keep meaningful sentences
            sentences.append(sentence)
    
    if not sentences:
        return "No meaningful content found for summarization"
    
    # Build summary
    summary = title + ". "
    
    # Add first 3 sentences or up to 500 chars
    for sentence in sentences[:3]:
        if len(summary + sentence) <= 500:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip()

async def process_content(news_item):
    """Process a news item: fetch content, check relevance, summarize"""
    logger.info(f"Processing: {news_item['title']}")
    
    # Check if the title itself contains voice AI keywords
    title_relevant = is_relevant_to_voice_ai(news_item['title'])
    if title_relevant:
        logger.info(f"Title is relevant to voice AI: {news_item['title']}")
        # If title is relevant, we can skip content fetching if needed
        if 'content' not in news_item or not news_item['content']:
            # Fetch the full article content
            content = await fetch_article_content(news_item['url'])
            if content:
                news_item['content'] = content
            else:
                # Even if we can't fetch content, the title is relevant so proceed
                news_item['content'] = news_item['title']
        
        # Generate a simple summary
        summary = await simple_summarize(news_item.get('content', ''), news_item['title'])
        news_item['summary'] = summary
        
        logger.info(f"Processed article (title match): {news_item['title']}")
        return news_item
    
    # If title isn't relevant, check the content
    if 'content' in news_item and news_item['content']:
        content = news_item['content']
    else:
        # Fetch the full article content
        content = await fetch_article_content(news_item['url'])
        if not content:
            logger.warning(f"Could not fetch content for {news_item['url']}")
            return None
        
        # Store the content
        news_item['content'] = content
    
    # Check if the content is relevant to voice AI
    if not is_relevant_to_voice_ai(content):
        logger.info(f"Article not relevant to voice AI: {news_item['title']}")
        return None
    
    # Generate a simple summary
    summary = await simple_summarize(content, news_item['title'])
    news_item['summary'] = summary
    
    logger.info(f"Processed article (content match): {news_item['title']}")
    return news_item
