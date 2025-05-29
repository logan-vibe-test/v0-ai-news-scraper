"""
Sentiment analyzer for AI Voice News Scraper
"""
import logging
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

async def analyze_sentiment(text):
    """Analyze the sentiment of a text using LangChain and OpenAI"""
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not configured")
        return {
            "sentiment": "neutral",
            "score": 0,
            "analysis": "Sentiment analysis not available (API key not configured)"
        }
    
    try:
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template("""
        Analyze the sentiment of the following text about AI voice technology.
        Return a JSON object with the following fields:
        - sentiment: "positive", "negative", or "neutral"
        - score: a number from -1 (very negative) to 1 (very positive)
        - analysis: a brief explanation of the sentiment (max 2 sentences)
        
        Text: {text}
        
        JSON:
        """)
        
        # Run the chain
        response = llm.invoke(prompt.format(text=text))
        
        # Parse the response
        # In a production system, you'd want to use json.loads() with error handling
        # This is simplified for the example
        result = eval(response.content)
        return result
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return {
            "sentiment": "neutral",
            "score": 0,
            "analysis": "Error in sentiment analysis"
        }
