"""
Twitter/X scraper for AI Voice News Scraper
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Twitter accounts and hashtags to monitor
TWITTER_ACCOUNTS = [
    'OpenAI',
    'ElevenLabs',
    'AndrewYNg',
    'ylecun',
    'sama',
    'karpathy',
    'GoogleAI',
    'MetaAI'
]

TWITTER_HASHTAGS = [
    'AIVoice',
    'VoiceAI',
    'TextToSpeech',
    'TTS',
    'VoiceSynthesis',
    'AIAudio'
]

async def initialize_twitter():
    """Initialize Twitter API client"""
    if not TWITTER_BEARER_TOKEN:
        logger.error("Twitter API credentials not configured")
        return None
    
    try:
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        return client
    except Exception as e:
        logger.error(f"Error initializing Twitter client: {str(e)}")
        return None

def is_relevant_to_news(tweet_text, news_items):
    """Check if a tweet is relevant to our tracked news items"""
    # Similar to Reddit relevance check
    text = tweet_text.lower()
    
    # Keywords related to voice AI
    voice_keywords = ['voice ai', 'text-to-speech', 'tts', 'speech synthesis', 
                      'voice synthesis', 'voice model', 'voice generation',
                      'elevenlabs', 'openai voice', 'audio generation']
    
    # Check for voice AI keywords
    if not any(keyword in text for keyword in voice_keywords):
        return False
    
    # Check if it references any of our tracked news
    for news in news_items:
        # Check for title match
        if news['title'].lower() in text:
            return True
        
        # Check for URL match
        if news['url'].lower() in text:
            return True
        
        # Check for source name match with context
        if news['source'].lower() in text and any(kw in text for kw in voice_keywords):
            return True
    
    return False

async def search_twitter(client, query, news_items):
    """Search Twitter for a specific query"""
    try:
        # Get tweets from the last 24 hours
        start_time = datetime.utcnow() - timedelta(hours=24)
        
        # Search recent tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=100,
            tweet_fields=['created_at', 'public_metrics', 'author_id']
        )
        
        if not tweets.data:
            return []
        
        reactions = []
        for tweet in tweets.data:
            if is_relevant_to_news(tweet.text, news_items):
                tweet_data = {
                    'platform': 'twitter',
                    'type': 'tweet',
                    'content': tweet.text,
                    'url': f"https://twitter.com/user/status/{tweet.id}",
                    'author_id': tweet.author_id,
                    'created_at': tweet.created_at.isoformat(),
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'like_count': tweet.public_metrics['like_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'related_news': []
                }
                
                # Find which news items it's related to
                for news in news_items:
                    if (news['title'].lower() in tweet.text.lower()):
                        tweet_data['related_news'].append(news['_id'])
                
                reactions.append(tweet_data)
        
        return reactions
    except Exception as e:
        logger.error(f"Error searching Twitter for {query}: {str(e)}")
        return []

async def scrape_twitter(news_items):
    """Scrape Twitter for reactions to news items"""
    client = await initialize_twitter()
    if not client:
        return []
    
    all_reactions = []
    tasks = []
    
    # Search for each account
    for account in TWITTER_ACCOUNTS:
        query = f"from:{account}"
        task = asyncio.to_thread(search_twitter, client, query, news_items)
        tasks.append(task)
    
    # Search for each hashtag
    for hashtag in TWITTER_HASHTAGS:
        query = f"#{hashtag}"
        task = asyncio.to_thread(search_twitter, client, query, news_items)
        tasks.append(task)
    
    # Gather results
    results = await asyncio.gather(*tasks)
    for result in results:
        all_reactions.extend(result)
    
    logger.info(f"Total Twitter reactions found: {len(all_reactions)}")
    return all_reactions
