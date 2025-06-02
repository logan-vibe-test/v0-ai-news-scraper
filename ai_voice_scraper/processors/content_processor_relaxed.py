"""
Relaxed content processor for debugging - temporarily more permissive
"""
import logging
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import ssl
import certifi

from ai_voice_scraper.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

async def fetch_article_content(url):
    """Fetch the full content of an article with better error handling"""
    try:
        # Create a more permissive SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"Error fetching article {url}: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.extract()
                
                # Try to find main content areas
                content_selectors = [
                    'article', '.article-content', '.post-content', 
                    '.entry-content', 'main', '.content', '#content'
                ]
                
                content_text = ""
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content_text = content_elem.get_text()
                        break
                
                # Fallback to body if no specific content area found
                if not content_text:
                    content_text = soup.get_text()
                
                # Clean up the text
                lines = (line.strip() for line in content_text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                logger.info(f"Fetched {len(text)} characters from {url}")
                return text
                
    except Exception as e:
        logger.error(f"Error fetching article content from {url}: {str(e)}")
        return None

def is_relevant_to_voice_ai_relaxed(text):
    """Much more relaxed relevance check for debugging"""
    if not text:
        return False
        
    text_lower = text.lower()
    
    # Very broad keywords - if ANY of these appear, consider it relevant
    broad_keywords = [
        # Core AI terms
        'ai', 'artificial intelligence', 'machine learning', 'deep learning',
        
        # Voice/Audio terms
        'voice', 'speech', 'audio', 'sound', 'tts', 'text-to-speech',
        'voice assistant', 'voice ai', 'speech synthesis', 'voice generation',
        
        # Company names
        'openai', 'elevenlabs', 'eleven labs', 'anthropic', 'google ai',
        'microsoft', 'amazon alexa', 'siri', 'cortana',
        
        # Technology terms
        'chatbot', 'assistant', 'conversation', 'dialogue', 'natural language',
        'nlp', 'neural', 'model', 'api', 'sdk',
        
        # Applications
        'podcast', 'audiobook', 'voiceover', 'dubbing', 'narration'
    ]
    
    # Count matches
    matches = sum(1 for keyword in broad_keywords if keyword in text_lower)
    
    logger.info(f"Found {matches} keyword matches in content")
    
    # Very low threshold - just need 1 match
    return matches >= 1

async def summarize_content_simple(content, title):
    """Simplified summarization that works without OpenAI if needed"""
    if not OPENAI_API_KEY:
        # Simple extractive summary - take first few sentences
        sentences = content.split('.')[:3]
        return '. '.join(sentences) + '.'
    
    try:
        # Use OpenAI if available
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text(content)
        docs = [Document(page_content=t) for t in texts]
        
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        
        prompt_template = """
        Summarize this article in 2-3 sentences, focusing on the main points:
        
        {text}
        
        SUMMARY:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
        summary = chain.run({"input_documents": docs})
        return summary.strip()
        
    except Exception as e:
        logger.error(f"Error summarizing content: {str(e)}")
        # Fallback to simple summary
        sentences = content.split('.')[:3]
        return '. '.join(sentences) + '.'

async def process_content_relaxed(news_item):
    """Process content with relaxed filtering for debugging"""
    logger.info(f"Processing (relaxed): {news_item['title']}")
    
    # Fetch the full article content
    content = await fetch_article_content(news_item['url'])
    if not content:
        logger.warning(f"Could not fetch content for {news_item['url']}")
        return None
    
    # Store the content
    news_item['content'] = content
    
    # Use relaxed relevance check
    if not is_relevant_to_voice_ai_relaxed(content):
        logger.info(f"Article not relevant (relaxed check): {news_item['title']}")
        return None
    
    # Summarize the content
    summary = await summarize_content_simple(content, news_item['title'])
    news_item['summary'] = summary
    
    logger.info(f"Successfully processed article: {news_item['title']}")
    return news_item
