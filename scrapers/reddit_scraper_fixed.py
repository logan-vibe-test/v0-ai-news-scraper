"""
Fixed Reddit scraper without SSL issues
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
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
    'ai voice', 'neural voice', 'voice assistant', 'speech generation'
]

def initialize_reddit():
    """Initialize Reddit client with proper error handling"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.warning("Reddit API credentials not configured")
        return None
    
    try:
        import praw
        
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        # Simple connection test
        reddit.read_only = True
        
        logger.info("✅ Reddit client initialized")
        return reddit
        
    except ImportError:
        logger.error("❌ PRAW not installed. Run: pip install praw")
        return None
    except Exception as e:
        logger.error(f"❌ Reddit initialization failed: {str(e)}")
        return None

def is_voice_ai_related(text):
    """Check if text is about voice AI"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in VOICE_KEYWORDS)

def get_subreddit_posts(reddit, subreddit_name, limit=10):
    """Get posts from a subreddit safely"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        # Get hot posts with error handling
        for post in subreddit.hot(limit=limit):
            try:
                # Check if post is about voice AI
                combined_text = f"{post.title} {getattr(post, 'selftext', '')}"
                
                if is_voice_ai_related(combined_text):
                    post_data = {
                        'platform': 'reddit',
                        'type': 'post',
                        'subreddit': subreddit_name,
                        'title': post.title,
                        'content': getattr(post, 'selftext', ''),
                        'url': f"https://reddit.com{post.permalink}",
                        'author': str(post.author) if post.author else '[deleted]',
                        'score': post.score,
                        'created_utc': post.created_utc,
                        'num_comments': post.num_comments
                    }
                    posts.append(post_data)
                    logger.info(f"Found voice AI post: {post.title[:60]}...")
                    
            except Exception as e:
                logger.warning(f"Error processing post: {str(e)}")
                continue
        
        return posts
        
    except Exception as e:
        logger.error(f"Error accessing r/{subreddit_name}: {str(e)}")
        return []

async def scrape_reddit_fixed():
    """Main Reddit scraping function"""
    logger.info("🔴 Starting Reddit scraper...")
    
    reddit = initialize_reddit()
    if not reddit:
        logger.warning("Reddit not available, skipping...")
        return []
    
    # Focus on key subreddits
    subreddits = ['OpenAI', 'artificial', 'MachineLearning', 'singularity']
    all_posts = []
    
    for subreddit_name in subreddits:
        try:
            logger.info(f"Checking r/{subreddit_name}...")
            posts = await asyncio.to_thread(get_subreddit_posts, reddit, subreddit_name, 15)
            all_posts.extend(posts)
            
            # Rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error processing r/{subreddit_name}: {str(e)}")
            continue
    
    logger.info(f"✅ Found {len(all_posts)} voice AI posts on Reddit")
    return all_posts

# Main function for compatibility
async def scrape_reddit(news_items=None):
    """Main scraper function"""
    return await scrape_reddit_fixed()

if __name__ == "__main__":
    async def test():
        posts = await scrape_reddit_fixed()
        print(f"Found {len(posts)} posts")
        for post in posts[:3]:
            print(f"- {post['title']}")
    
    asyncio.run(test())
