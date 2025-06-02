"""
Content processor for AI Voice News Scraper - Fixed version
"""
import logging
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import ssl
import certifi

# Fix the import path
try:
    from config.keywords import ALL_VOICE_AI_KEYWORDS, PRIMARY_VOICE_AI_KEYWORDS, CONTEXT_KEYWORDS
except ImportError:
    # Fallback if config module not found
    PRIMARY_VOICE_AI_KEYWORDS = [
        'voice ai', 'ai voice', 'voice artificial intelligence',
        'text-to-speech', 'tts', 'speech synthesis', 'voice synthesis',
        'voice generation', 'voice model', 'neural voice',
        'voice cloning', 'voice clone', 'synthetic voice',
        'voice assistant', 'voice bot', 'conversational ai',
        'voice interface', 'voice api', 'voice sdk',
        'audio generation', 'speech generation', 'voice streaming',
        'real-time voice', 'voice conversion', 'voice transformer',
        'elevenlabs', 'eleven labs', 'openai voice', 'openai whisper',
        'google voice', 'google speech', 'amazon polly', 'azure speech',
        'microsoft speech', 'anthropic voice', 'meta voice',
        'nvidia voice', 'adobe voice', 'murf', 'speechify',
        'resemble ai', 'descript', 'wellsaid', 'lovo'
    ]
    
    ALL_VOICE_AI_KEYWORDS = PRIMARY_VOICE_AI_KEYWORDS
    
    CONTEXT_KEYWORDS = [
        'ai', 'artificial intelligence', 'machine learning', 'deep learning',
        'neural network', 'model', 'algorithm', 'training', 'dataset',
        'api', 'sdk', 'platform', 'technology', 'innovation',
        'startup', 'funding', 'release', 'launch', 'announcement'
    ]

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Replace the existing VOICE_AI_KEYWORDS with:
VOICE_AI_KEYWORDS = ALL_VOICE_AI_KEYWORDS

async def fetch_article_content(url):
    """Fetch the full content of an article"""
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_OPTIONAL
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=10) as response:
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
    """Check if the content is relevant to voice AI with LENIENT logic"""
    if not text:
        return False
        
    text_lower = text.lower()
    
    # Check for ANY voice AI keyword matches (more lenient)
    keyword_matches = sum(1 for keyword in VOICE_AI_KEYWORDS if keyword in text_lower)
    
    # If we have any voice AI keywords, it's relevant
    if keyword_matches > 0:
        logger.info(f"Found {keyword_matches} voice AI keywords - marking as relevant")
        return True
    
    # Also check for AI + voice combinations
    has_ai = any(word in text_lower for word in ['ai', 'artificial intelligence'])
    has_voice = any(word in text_lower for word in ['voice', 'speech', 'audio'])
    
    if has_ai and has_voice:
        logger.info("Found AI + voice combination - marking as relevant")
        return True
    
    return False

async def summarize_content(content, title):
    """Summarize the article content - simplified version"""
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured - using simple summary")
        # Simple fallback summary
        sentences = content.split('.')[:3]
        return '. '.join(sentences) + '.'
    
    try:
        # Try to use OpenAI for summarization
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.documents import Document
        from langchain.chains.summarize import load_summarize_chain
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text(content)
        
        # Create documents
        docs = [Document(page_content=t) for t in texts]
        
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        
        # Create the summarization chain
        prompt_template = """
        You are an AI assistant that summarizes news articles about voice AI technology.
        
        Write a concise summary of the following article about voice AI technology:
        
        {text}
        
        The article title is: {title}
        
        Focus on the key points related to voice AI technology, including:
        - New features or capabilities
        - Technical improvements
        - Company announcements
        - Potential applications
        
        SUMMARY:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text", "title"]
        )
        
        chain = load_summarize_chain(
            llm,
            chain_type="stuff",
            prompt=prompt
        )
        
        # Run the chain
        summary = chain.run({"input_documents": docs, "title": title})
        return summary.strip()
    except Exception as e:
        logger.error(f"Error summarizing content: {str(e)}")
        # Fallback to simple summary
        sentences = content.split('.')[:3]
        return '. '.join(sentences) + '.'

async def process_content(news_item):
    """Process a news item: fetch content, check relevance, summarize"""
    logger.info(f"Processing: {news_item['title']}")
    
    # First check title for relevance
    if is_relevant_to_voice_ai(news_item['title']):
        logger.info(f"Title is relevant to voice AI: {news_item['title']}")
        
        # Try to fetch the full article content
        content = await fetch_article_content(news_item['url'])
        if content:
            news_item['content'] = content
            
            # Double-check with full content
            if is_relevant_to_voice_ai(content):
                # Summarize the content
                summary = await summarize_content(content, news_item['title'])
                news_item['summary'] = summary
                
                logger.info(f"Processed article: {news_item['title']}")
                return news_item
            else:
                logger.info(f"Full content not relevant to voice AI: {news_item['title']}")
        else:
            # If we can't fetch content but title is relevant, still include it
            logger.warning(f"Could not fetch content but title is relevant: {news_item['title']}")
            news_item['content'] = news_item.get('content', '')
            news_item['summary'] = f"Summary not available. Title: {news_item['title']}"
            return news_item
    
    logger.info(f"Article not relevant to voice AI: {news_item['title']}")
    return None
