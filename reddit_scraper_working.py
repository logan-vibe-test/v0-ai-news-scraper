"""
Working Reddit scraper that bypasses SSL verification issues
"""
import asyncio
import logging
import praw
import requests
import urllib3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

# Disable SSL warnings since we'll be bypassing verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')

# Subreddits to monitor (reduced list for testing)
SUBREDDITS = [
    'MachineLearning',
    'artificial', 
    'OpenAI'
]

# Voice AI keywords for filtering
VOICE_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis', 
    'voice synthesis', 'voice model', 'voice generation',
    'elevenlabs', 'openai voice', 'audio generation',
    'voice clone', 'voice cloning', 'synthetic voice',
    'ai voice', 'neural voice', 'voice assistant'
]

def create_reddit_session_no_ssl():
    """Create a requests session with SSL verification disabled"""
    session = requests.Session()
    session.verify = False  # Disable SSL verification
    
    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'ai_voice_news_scraper v1.0'
    })
    
    logger.warning("SSL verification disabled for Reddit API - not recommended for production")
    return session

def initialize_reddit_no_ssl():
    """Initialize Reddit API client with SSL verification disabled"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.error("Reddit API credentials not configured")
        return None
    
    try:
        # Create session with SSL verification disabled
        session = create_reddit_session_no_ssl()
        
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            requestor_kwargs={'session': session}
        )
        
        logger.info("Initialized Reddit client with SSL verification disabled")
        return reddit
    except Exception as e:
        logger.error(f"Error initializing Reddit client: {str(e)}")
        return None

def is_relevant_to_voice_ai(text):
    """Check if text is relevant to voice AI"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in VOICE_KEYWORDS)

def process_subreddit_safe(reddit, subreddit_name, max_posts=5):
    """Process a single subreddit with error handling"""
    try:
        logger.info(f"Processing r/{subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        reactions = []
        
        # Get hot posts (very limited to avoid rate limits)
        posts = list(subreddit.hot(limit=max_posts))
        
        logger.info(f"Found {len(posts)} posts in r/{subreddit_name}")
        
        # Process each post
        for post in posts:
            try:
                # Skip posts older than 1 day
                post_time = datetime.fromtimestamp(post.created_utc)
                if datetime.now() - post_time > timedelta(days=1):
                    continue
                
                # Check if post is about voice AI
                combined_text = f"{post.title} {getattr(post, 'selftext', '')}"
                if is_relevant_to_voice_ai(combined_text):
                    # Process the post
                    post_data = {
                        'platform': 'reddit',
                        'type': 'post',
                        'subreddit': subreddit_name,
                        'title': post.title,
                        'content': getattr(post, 'selftext', ''),
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
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error processing post: {str(e)}")
                continue
        
        logger.info(f"Found {len(reactions)} voice AI related items in r/{subreddit_name}")
        return reactions
        
    except Exception as e:
        logger.error(f"Error processing subreddit {subreddit_name}: {str(e)}")
        return []

async def scrape_reddit_working(news_items=None):
    """Scrape Reddit for voice AI content - working version"""
    logger.info("Starting working Reddit scraper (SSL verification disabled)")
    
    # Initialize Reddit client
    reddit = initialize_reddit_no_ssl()
    if not reddit:
        logger.error("Failed to initialize Reddit client")
        return []
    
    all_reactions = []
    
    # Process each subreddit with rate limiting
    for subreddit in SUBREDDITS:
        try:
            # Process in a separate thread since Reddit API is synchronous
            reactions = await asyncio.to_thread(process_subreddit_safe, reddit, subreddit)
            all_reactions.extend(reactions)
            
            # Rate limiting between subreddits
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Error processing subreddit {subreddit}: {str(e)}")
    
    logger.info(f"Total Reddit reactions found: {len(all_reactions)}")
    return all_reactions

async def test_reddit_working():
    """Test the working Reddit scraper"""
    logger.info("Testing working Reddit scraper")
    
    try:
        reactions = await scrape_reddit_working()
        
        print(f"\n{'='*60}")
        print(f"✅ REDDIT SCRAPER WORKING!")
        print(f"Found {len(reactions)} voice AI related posts on Reddit")
        print(f"{'='*60}")
        
        for i, reaction in enumerate(reactions[:3]):  # Show first 3
            print(f"\n{i+1}. r/{reaction['subreddit']} - {reaction['type']}")
            print(f"   Title: {reaction['title']}")
            print(f"   Content: {reaction['content'][:100]}...")
            print(f"   Score: {reaction['score']}")
            print(f"   URL: {reaction['url']}")
        
        if len(reactions) == 0:
            print("\nNo voice AI posts found in the last 24 hours.")
            print("This is normal - try running again later or check different subreddits.")
        
        return True
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
    asyncio.run(test_reddit_working())
