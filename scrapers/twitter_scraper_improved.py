"""
Improved Twitter/X scraper for AI Voice News Scraper
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Twitter accounts to monitor
TWITTER_ACCOUNTS = [
    'OpenAI',
    'ElevenLabs',
    'AndrewYNg',
    'ylecun',
    'sama',
    'karpathy',
    'GoogleAI',
    'MetaAI',
    'Anthropic',
    'DeepMind',
    'Microsoft',
    'AmazonScience',
    'ResembleAI',
    'Descript',
    'WellSaidLabs',
    'PlayHT',
    'Synthesia',
    'RunwayML',
    'HuggingFace'
]

# Twitter hashtags to monitor
TWITTER_HASHTAGS = [
    'AIVoice',
    'VoiceAI',
    'TextToSpeech',
    'TTS',
    'VoiceSynthesis',
    'AIAudio',
    'VoiceCloning',
    'SpeechSynthesis',
    'AIVoiceOver',
    'SyntheticVoice'
]

# Voice AI keywords for filtering
VOICE_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis', 
    'voice synthesis', 'voice model', 'voice generation',
    'elevenlabs', 'openai voice', 'audio generation',
    'voice clone', 'voice cloning', 'synthetic voice',
    'ai voice', 'neural voice', 'voice assistant'
]

def initialize_twitter():
    """Initialize Twitter API client with better error handling"""
    if not TWITTER_BEARER_TOKEN:
        logger.error("Twitter API credentials not configured")
        return None
    
    try:
        # Try with OAuth 1.0a if available (better API limits)
        if all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
            client = tweepy.Client(
                bearer_token=TWITTER_BEARER_TOKEN,
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET
            )
            logger.info("Initialized Twitter client with OAuth 1.0a")
        else:
            # Fall back to bearer token only
            client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            logger.info("Initialized Twitter client with bearer token only")
        
        return client
    except Exception as e:
        logger.error(f"Error initializing Twitter client: {str(e)}")
        return None

def is_relevant_to_voice_ai(text):
    """Check if text is relevant to voice AI"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in VOICE_KEYWORDS)

async def search_twitter_with_retry(client, query, max_results=10, retries=3):
    """Search Twitter with retry logic"""
    for attempt in range(retries):
        try:
            # Get tweets from the last 7 days (maximum allowed by recent search)
            tweets = client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'text']
            )
            
            if not tweets.data:
                logger.info(f"No tweets found for query: {query}")
                return []
            
            return tweets.data
        except tweepy.TooManyRequests:
            wait_time = 60 * (attempt + 1)  # Progressive backoff
            logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except tweepy.TwitterServerError:
            wait_time = 30 * (attempt + 1)
            logger.warning(f"Twitter server error. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"Error searching Twitter for {query}: {str(e)}")
            return []
    
    logger.error(f"Failed to search Twitter after {retries} attempts")
    return []

async def scrape_twitter(news_items=None):
    """Scrape Twitter for voice AI content"""
    logger.info("Starting Twitter scraper")
    
    # Initialize Twitter client
    client = initialize_twitter()
    if not client:
        logger.error("Failed to initialize Twitter client")
        return []
    
    all_reactions = []
    
    # Search for each account
    for account in TWITTER_ACCOUNTS:
        try:
            query = f"from:{account}"
            logger.info(f"Searching tweets from {account}")
            
            tweets = await search_twitter_with_retry(client, query)
            
            # Filter for voice AI relevance
            for tweet in tweets:
                if is_relevant_to_voice_ai(tweet.text):
                    tweet_data = {
                        'platform': 'twitter',
                        'type': 'tweet',
                        'content': tweet.text,
                        'url': f"https://twitter.com/user/status/{tweet.id}",
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'related_news': []
                    }
                    
                    all_reactions.append(tweet_data)
                    logger.info(f"Found relevant tweet from {account}: {tweet.text[:100]}...")
            
            # Rate limiting to avoid API issues
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error processing account {account}: {str(e)}")
    
    # Search for each hashtag (if we have API calls left)
    if len(all_reactions) < 50:  # Limit total API calls
        for hashtag in TWITTER_HASHTAGS:
            try:
                query = f"#{hashtag}"
                logger.info(f"Searching tweets with {query}")
                
                tweets = await search_twitter_with_retry(client, query, max_results=5)
                
                # Filter for voice AI relevance (already implied by hashtag, but double-check)
                for tweet in tweets:
                    tweet_data = {
                        'platform': 'twitter',
                        'type': 'tweet',
                        'content': tweet.text,
                        'url': f"https://twitter.com/user/status/{tweet.id}",
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'related_news': []
                    }
                    
                    all_reactions.append(tweet_data)
                    logger.info(f"Found tweet with #{hashtag}: {tweet.text[:100]}...")
                
                # Rate limiting to avoid API issues
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error processing hashtag {hashtag}: {str(e)}")
    
    # Match reactions to news items if provided
    if news_items:
        for reaction in all_reactions:
            for news in news_items:
                # Check if reaction mentions news title
                if news['title'].lower() in reaction['content'].lower():
                    reaction['related_news'].append(news['_id'])
    
    logger.info(f"Total Twitter reactions found: {len(all_reactions)}")
    return all_reactions

async def test_twitter_scraper():
    """Test the Twitter scraper functionality"""
    logger.info("Testing Twitter scraper")
    reactions = await scrape_twitter()
    
    print(f"\n{'='*60}")
    print(f"Found {len(reactions)} voice AI related tweets")
    print(f"{'='*60}")
    
    for i, reaction in enumerate(reactions[:10]):  # Show first 10
        print(f"\n{i+1}. Tweet")
        print(f"   Content: {reaction['content'][:150]}...")
        print(f"   URL: {reaction['url']}")
        print(f"   Likes: {reaction['like_count']}")
    
    return reactions

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test
    asyncio.run(test_twitter_scraper())
