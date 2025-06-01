"""
Reddit scraper with SSL certificate fix
"""
import asyncio
import logging
import praw
import requests
import certifi
import urllib3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

# Subreddits to monitor
SUBREDDITS = [
    'MachineLearning',
    'artificial',
    'OpenAI',
    'ElevenLabs',
    'TextToSpeech',
    'AIVoice'
]

# Voice AI keywords for filtering
VOICE_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis', 
    'voice synthesis', 'voice model', 'voice generation',
    'elevenlabs', 'openai voice', 'audio generation',
    'voice clone', 'voice cloning', 'synthetic voice',
    'ai voice', 'neural voice', 'voice assistant'
]

def create_reddit_session():
    """Create a requests session with proper SSL configuration"""
    session = requests.Session()
    
    try:
        # Try to use proper certificates
        session.verify = certifi.where()
        logger.info("Using proper SSL certificates")
    except Exception as e:
        logger.warning(f"Could not set up SSL certificates: {e}")
        # Fallback: disable SSL verification (not recommended for production)
        session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warning("SSL verification disabled - not recommended for production")
    
    return session

def initialize_reddit():
    """Initialize Reddit API client with SSL fix"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.error("Reddit API credentials not configured")
        return None
    
    try:
        # Create session with SSL fix
        session = create_reddit_session()
        
        # Try with username/password if available
        if REDDIT_USERNAME and REDDIT_PASSWORD:
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD,
                requestor_kwargs={'session': session}
            )
            logger.info("Initialized Reddit client with user authentication")
        else:
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                requestor_kwargs={'session': session}
            )
            logger.info("Initialized Reddit client in read-only mode")
        
        return reddit
    except Exception as e:
        logger.error(f"Error initializing Reddit client: {str(e)}")
        return None

def is_relevant_to_voice_ai(text):
    """Check if text is relevant to voice AI"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in VOICE_KEYWORDS)

def process_subreddit(reddit, subreddit_name, max_posts=10):
    """Process a single subreddit for voice AI content"""
    try:
        logger.info(f"Processing r/{subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        reactions = []
        
        # Get hot posts (reduced number to avoid rate limits)
        posts = list(subreddit.hot(limit=max_posts))
        
        logger.info(f"Found {len(posts)} posts in r/{subreddit_name}")
        
        # Process each post
        for post in posts:
            # Skip posts older than 2 days
            post_time = datetime.fromtimestamp(post.created_utc)
            if datetime.now() - post_time > timedelta(days=2):
                continue
            
            # Check if post is about voice AI
            combined_text = f"{post.title} {post.selftext}"
            if is_relevant_to_voice_ai(combined_text):
                # Process the post
                post_data = {
                    'platform': 'reddit',
                    'type': 'post',
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'content': post.selftext,
                    'url': f"https://reddit.com{post.permalink}",
                    'author': post.author.name if post.author else '[deleted]',
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments,
                    'related_news': []
                }
                
                reactions.append(post_data)
                logger.info(f"Found relevant post: {post.title}")
                
                # Rate limiting to avoid API issues
                time.sleep(1)
        
        logger.info(f"Found {len(reactions)} voice AI related items in r/{subreddit_name}")
        return reactions
    except Exception as e:
        logger.error(f"Error processing subreddit {subreddit_name}: {str(e)}")
        return []

async def scrape_reddit(news_items=None):
    """Scrape Reddit for voice AI content with SSL fix"""
    logger.info("Starting Reddit scraper with SSL fix")
    
    # Initialize Reddit client
    reddit = initialize_reddit()
    if not reddit:
        logger.error("Failed to initialize Reddit client")
        return []
    
    all_reactions = []
    
    # Process each subreddit (reduced list to avoid rate limits)
    limited_subreddits = SUBREDDITS[:3]  # Only process first 3 subreddits
    
    for subreddit in limited_subreddits:
        try:
            # Process in a separate thread since Reddit API is synchronous
            reactions = await asyncio.to_thread(process_subreddit, reddit, subreddit)
            all_reactions.extend(reactions)
            
            # Rate limiting between subreddits
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error processing subreddit {subreddit}: {str(e)}")
    
    logger.info(f"Total Reddit reactions found: {len(all_reactions)}")
    return all_reactions

async def test_reddit_scraper_ssl():
    """Test the Reddit scraper with SSL fix"""
    logger.info("Testing Reddit scraper with SSL fix")
    
    try:
        reactions = await scrape_reddit()
        
        print(f"\n{'='*60}")
        print(f"Found {len(reactions)} voice AI related posts/comments on Reddit")
        print(f"{'='*60}")
        
        for i, reaction in enumerate(reactions[:5]):  # Show first 5
            print(f"\n{i+1}. r/{reaction['subreddit']} - {reaction['type']}")
            if reaction['type'] == 'post':
                print(f"   Title: {reaction['title']}")
            print(f"   Content: {reaction['content'][:100]}...")
            print(f"   Score: {reaction['score']}")
        
        return len(reactions) > 0
    except Exception as e:
        logger.error(f"Reddit scraper test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test
    asyncio.run(test_reddit_scraper_ssl())
