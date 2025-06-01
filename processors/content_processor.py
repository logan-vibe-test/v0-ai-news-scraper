"""
Content processor for AI Voice News Scraper
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
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
import os
from dotenv import load_dotenv

# Add this import at the top
from config.keywords import ALL_VOICE_AI_KEYWORDS, PRIMARY_VOICE_AI_KEYWORDS, CONTEXT_KEYWORDS

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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
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
    """Check if the content is relevant to voice AI with improved logic"""
    text_lower = text.lower()
    
    # Check for primary keyword matches (must have at least one)
    primary_matches = sum(1 for keyword in PRIMARY_VOICE_AI_KEYWORDS if keyword in text_lower)
    
    if primary_matches == 0:
        return False  # No primary voice AI keywords found
    
    # If we have primary matches, check for additional context
    all_keyword_matches = sum(1 for keyword in VOICE_AI_KEYWORDS if keyword in text_lower)
    context_matches = sum(1 for keyword in CONTEXT_KEYWORDS if keyword in text_lower)
    
    # Strong relevance: multiple voice AI keywords OR voice AI + context
    if all_keyword_matches >= 2 or (primary_matches >= 1 and context_matches >= 1):
        return True
    
    # For single primary match, look for context in the same sentence
    if primary_matches == 1:
        sentences = re.split(r'[.!?]+', text_lower)
        for sentence in sentences:
            if any(keyword in sentence for keyword in PRIMARY_VOICE_AI_KEYWORDS):
                if any(context in sentence for context in CONTEXT_KEYWORDS):
                    return True
    
    return False

async def summarize_content(content, title):
    """Summarize the article content using LangChain and OpenAI"""
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not configured")
        return "Summary not available (API key not configured)"
    
    try:
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
        return "Error generating summary"

async def process_content(news_item):
    """Process a news item: fetch content, check relevance, summarize"""
    logger.info(f"Processing: {news_item['title']}")
    
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
    
    # Summarize the content
    summary = await summarize_content(content, news_item['title'])
    news_item['summary'] = summary
    
    logger.info(f"Processed article: {news_item['title']}")
    return news_item
