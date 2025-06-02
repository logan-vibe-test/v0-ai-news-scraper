"""
Simple Reddit scraper that actually works
"""
import asyncio
import logging
import os
import ssl
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')

# Voice AI keywords
VOICE_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'elevenlabs', 'openai voice', 'voice cloning',
    'eleven labs', 'whisper', 'voice clone', 'synthetic voice',
    'ai voice', 'neural voice', 'voice assistant'
]

def initialize_reddit_with_ssl_fix():
    """Initialize Reddit with SSL certificate fix"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.error("Reddit API credentials not configured")
        return None
    
    try:
        import praw
        import prawcore
        
        # Create SSL context with proper certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Configure prawcore to use our SSL context
        prawcore.sessions.session = prawcore.sessions.Session()
        
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            check_for_async=False
        )
        
        # Test connection
        reddit.user.me()
        logger.info("✅ Reddit API connection successful")
        return reddit
        
    except Exception as e:
        logger.error(f"❌ Reddit connection failed: {str(e)}")
        return None

def is_voice_ai_related(text):
    """Simple check if text is about voice AI"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in VOICE_KEYWORDS)

def get_reddit_posts_simple(reddit, subreddit_name, limit=10):
    """Get posts from a subreddit with error handling"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        # Get hot posts only to avoid rate limiting
        for post in subreddit.hot(limit=limit):
            if is_voice_ai_related(f"{post.title} {post.selftext}"):
                posts.append({
                    'platform': 'reddit',
                    'type': 'post',
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'content': post.selftext,
                    'url': f"https://reddit.com{post.permalink}",
                    'author': post.author.name if post.author else '[deleted]',
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments
                })
                logger.info(f"Found voice AI post in r/{subreddit_name}: {post.title[:60]}...")
        
        return posts
        
    except Exception as e:
        logger.warning(f"Error getting posts from r/{subreddit_name}: {str(e)}")
        return []

async def scrape_reddit_simple():
    """Simple Reddit scraper that works"""
    logger.info("🔴 Starting simple Reddit scraper...")
    
    reddit = initialize_reddit_with_ssl_fix()
    if not reddit:
        return []
    
    # Focus on just a few key subreddits
    subreddits = ['OpenAI', 'artificial', 'MachineLearning']
    all_posts = []
    
    for subreddit_name in subreddits:
        logger.info(f"Checking r/{subreddit_name}...")
        posts = await asyncio.to_thread(get_reddit_posts_simple, reddit, subreddit_name, 20)
        all_posts.extend(posts)
        
        # Small delay to be nice to Reddit
        await asyncio.sleep(1)
    
    logger.info(f"✅ Found {len(all_posts)} voice AI posts on Reddit")
    return all_posts

# For compatibility with main scraper
async def scrape_reddit(news_items=None):
    """Main scraper function"""
    return await scrape_reddit_simple()

if __name__ == "__main__":
    async def test():
        posts = await scrape_reddit_simple()
        print(f"Found {len(posts)} posts")
        for post in posts[:3]:
            print(f"- {post['title']}")
    
    asyncio.run(test())
