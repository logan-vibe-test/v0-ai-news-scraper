"""
Fixed Reddit scraper that focuses solely on AI voice topics
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

# Voice AI keywords - expanded for better coverage
VOICE_KEYWORDS = [
    # Core voice AI terms
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'voice generation', 'voice model', 'neural voice',
    'voice cloning', 'voice clone', 'synthetic voice', 'ai voice',
    
    # Companies and products
    'elevenlabs', 'eleven labs', 'openai voice', 'whisper',
    'murf ai', 'speechify', 'resemble ai', 'wellsaid labs',
    'play.ht', 'coqui', 'bark tts', 'tortoise tts',
    
    # Technical terms
    'vocoder', 'neural vocoder', 'voice transformer',
    'voice conversion', 'speech-to-speech', 'voice streaming',
    
    # Applications
    'ai voiceover', 'ai dubbing', 'voice assistant', 'ai narrator',
    'ai audiobook', 'voice avatar', 'digital voice twin'
]

# Subreddits to check - expanded list focused on AI and tech
VOICE_AI_SUBREDDITS = [
    'MachineLearning',
    'artificial',
    'OpenAI',
    'singularity',
    'LanguageTechnology',
    'AIGeneratedAudio',
    'MediaSynthesis',
    'ElevenLabs',
    'LocalLLaMA',
    'technology',
    'futurology',
    'VoiceActing',  # might discuss AI impact
    'AudioEngineering'  # might discuss AI tools
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

def get_subreddit_posts(reddit, subreddit_name, limit=15, time_filter='week'):
    """Get voice AI related posts from a subreddit"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        # Try different sorting methods to maximize chances of finding relevant content
        sources = [
            ('hot', subreddit.hot(limit=limit)),
            ('new', subreddit.new(limit=limit)),
            ('top', subreddit.top(time_filter=time_filter, limit=limit))
        ]
        
        for source_name, source_posts in sources:
            for post in source_posts:
                try:
                    # Check if post is about voice AI
                    combined_text = f"{post.title} {getattr(post, 'selftext', '')}"
                    
                    if is_voice_ai_related(combined_text):
                        # Extract the specific keywords that matched
                        matched_keywords = [kw for kw in VOICE_KEYWORDS if kw in combined_text.lower()]
                        
                        post_data = {
                            'platform': 'reddit',
                            'type': 'post',
                            'subreddit': subreddit_name,
                            'title': post.title,
                            'content': getattr(post, 'selftext', '')[:500],  # Limit content length
                            'url': f"https://reddit.com{post.permalink}",
                            'author': str(post.author) if post.author else '[deleted]',
                            'score': post.score,
                            'created_utc': post.created_utc,
                            'num_comments': post.num_comments,
                            'matched_keywords': matched_keywords,
                            'source_type': source_name
                        }
                        
                        # Skip if we already have this post (from another source)
                        if not any(p['url'] == post_data['url'] for p in posts):
                            posts.append(post_data)
                            logger.info(f"Found voice AI post in r/{subreddit_name}: {post.title[:60]}...")
                    
                except Exception as e:
                    logger.warning(f"Error processing post: {str(e)}")
                    continue
        
        return posts
        
    except Exception as e:
        logger.error(f"Error accessing r/{subreddit_name}: {str(e)}")
        return []

async def scrape_reddit_fixed():
    """Main Reddit scraping function - now focused solely on finding AI voice content"""
    logger.info("🔴 Starting Reddit scraper for AI voice topics...")
    
    reddit = initialize_reddit()
    if not reddit:
        logger.warning("Reddit not available, skipping...")
        return []
    
    all_posts = []
    
    # Process subreddits in batches to avoid rate limiting
    batch_size = 3
    for i in range(0, len(VOICE_AI_SUBREDDITS), batch_size):
        batch = VOICE_AI_SUBREDDITS[i:i + batch_size]
        
        for subreddit_name in batch:
            try:
                logger.info(f"Checking r/{subreddit_name}...")
                posts = await asyncio.to_thread(get_subreddit_posts, reddit, subreddit_name)
                all_posts.extend(posts)
                
            except Exception as e:
                logger.error(f"Error processing r/{subreddit_name}: {str(e)}")
                continue
            
            # Small delay between subreddits
            await asyncio.sleep(1)
        
        # Larger delay between batches
        if i + batch_size < len(VOICE_AI_SUBREDDITS):
            await asyncio.sleep(2)
    
    # Sort by score and recency
    all_posts.sort(key=lambda x: (x.get('score', 0), x.get('created_utc', 0)), reverse=True)
    
    # Limit to top results
    all_posts = all_posts[:30]
    
    logger.info(f"✅ Found {len(all_posts)} voice AI posts on Reddit")
    return all_posts

# Main function for compatibility with the rest of the system
async def scrape_reddit(news_items=None):
    """Main scraper function - ignores news_items parameter"""
    return await scrape_reddit_fixed()

if __name__ == "__main__":
    async def test():
        posts = await scrape_reddit_fixed()
        print(f"Found {len(posts)} posts")
        for post in posts[:3]:
            print(f"- {post['title']}")
    
    asyncio.run(test())
