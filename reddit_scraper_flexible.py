"""
More flexible Reddit scraper that finds more relevant posts
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
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')

# Expanded subreddits list
SUBREDDITS = [
    'MachineLearning',
    'artificial', 
    'OpenAI',
    'singularity',
    'ArtificialIntelligence',
    'MediaSynthesis',
    'deeplearning',
    'LocalLLaMA',
    'ChatGPT',
    'technology'
]

# More flexible keywords - broader AI terms that might lead to voice discussions
BROAD_AI_KEYWORDS = [
    # Direct voice terms
    'voice', 'speech', 'audio', 'sound', 'tts', 'text-to-speech',
    'voice ai', 'ai voice', 'voice synthesis', 'speech synthesis',
    'voice generation', 'voice model', 'voice clone', 'voice cloning',
    
    # Company names (these often have voice products)
    'elevenlabs', 'eleven labs', 'openai', 'anthropic', 'google',
    'microsoft', 'amazon', 'meta', 'nvidia',
    
    # AI model names that might relate to voice
    'whisper', 'gpt', 'claude', 'gemini', 'llama',
    
    # General AI terms that might include voice discussions
    'multimodal', 'audio generation', 'synthetic media',
    'ai assistant', 'chatbot', 'conversational ai',
    
    # Voice-adjacent terms
    'podcast', 'audiobook', 'narration', 'dubbing',
    'accessibility', 'text reader', 'voice over'
]

# High-value keywords that are more likely to be voice-related
HIGH_VALUE_KEYWORDS = [
    'voice ai', 'ai voice', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'voice generation', 'voice model', 'voice clone',
    'elevenlabs', 'eleven labs', 'openai voice', 'whisper'
]

def create_reddit_session_no_ssl():
    """Create a requests session with SSL verification disabled"""
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'ai_voice_news_scraper v1.0'
    })
    return session

def initialize_reddit_flexible():
    """Initialize Reddit API client"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.error("Reddit API credentials not configured")
        return None
    
    try:
        session = create_reddit_session_no_ssl()
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            requestor_kwargs={'session': session}
        )
        logger.info("Initialized Reddit client")
        return reddit
    except Exception as e:
        logger.error(f"Error initializing Reddit client: {str(e)}")
        return None

def calculate_relevance_score(text):
    """Calculate how relevant a post is to voice AI (0-100)"""
    if not text:
        return 0
    
    text_lower = text.lower()
    score = 0
    
    # High value keywords get more points
    for keyword in HIGH_VALUE_KEYWORDS:
        if keyword in text_lower:
            score += 20
    
    # Broad keywords get fewer points
    for keyword in BROAD_AI_KEYWORDS:
        if keyword in text_lower:
            score += 5
    
    # Bonus for multiple keyword matches
    keyword_count = sum(1 for keyword in BROAD_AI_KEYWORDS if keyword in text_lower)
    if keyword_count > 2:
        score += 10
    
    return min(score, 100)  # Cap at 100

def is_potentially_relevant(text, min_score=15):
    """Check if text might be relevant to voice AI"""
    return calculate_relevance_score(text) >= min_score

def process_subreddit_flexible(reddit, subreddit_name, max_posts=20):
    """Process a subreddit with flexible matching"""
    try:
        logger.info(f"Processing r/{subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        reactions = []
        
        # Get more posts and from longer time period
        posts = list(subreddit.hot(limit=max_posts))
        
        logger.info(f"Checking {len(posts)} posts in r/{subreddit_name}")
        
        for post in posts:
            try:
                # Extend time window to 7 days
                post_time = datetime.fromtimestamp(post.created_utc)
                if datetime.now() - post_time > timedelta(days=7):
                    continue
                
                # Check relevance with flexible scoring
                combined_text = f"{post.title} {getattr(post, 'selftext', '')}"
                relevance_score = calculate_relevance_score(combined_text)
                
                if relevance_score >= 15:  # Lower threshold
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
                        'relevance_score': relevance_score,
                        'related_news': []
                    }
                    
                    reactions.append(post_data)
                    logger.info(f"Found relevant post (score: {relevance_score}): {post.title}")
                
                time.sleep(0.3)  # Reduced delay
                
            except Exception as e:
                logger.warning(f"Error processing post: {str(e)}")
                continue
        
        logger.info(f"Found {len(reactions)} potentially relevant items in r/{subreddit_name}")
        return reactions
        
    except Exception as e:
        logger.error(f"Error processing subreddit {subreddit_name}: {str(e)}")
        return []

async def scrape_reddit_flexible(news_items=None):
    """Flexible Reddit scraper that finds more posts"""
    logger.info("Starting flexible Reddit scraper")
    
    reddit = initialize_reddit_flexible()
    if not reddit:
        return []
    
    all_reactions = []
    
    # Process more subreddits
    for subreddit in SUBREDDITS:
        try:
            reactions = await asyncio.to_thread(process_subreddit_flexible, reddit, subreddit)
            all_reactions.extend(reactions)
            await asyncio.sleep(2)  # Rate limiting
        except Exception as e:
            logger.error(f"Error processing subreddit {subreddit}: {str(e)}")
    
    # Sort by relevance score
    all_reactions.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    logger.info(f"Total Reddit reactions found: {len(all_reactions)}")
    return all_reactions

async def test_reddit_flexible():
    """Test the flexible Reddit scraper"""
    logger.info("Testing flexible Reddit scraper")
    
    try:
        reactions = await scrape_reddit_flexible()
        
        print(f"\n{'='*60}")
        print(f"FLEXIBLE REDDIT SCRAPER RESULTS")
        print(f"Found {len(reactions)} potentially relevant posts")
        print(f"{'='*60}")
        
        if reactions:
            print(f"\nTop {min(5, len(reactions))} most relevant posts:")
            for i, reaction in enumerate(reactions[:5]):
                print(f"\n{i+1}. r/{reaction['subreddit']} (Score: {reaction['relevance_score']})")
                print(f"   Title: {reaction['title']}")
                print(f"   Content: {reaction['content'][:100]}...")
                print(f"   Score: {reaction['score']} | Comments: {reaction['num_comments']}")
                print(f"   URL: {reaction['url']}")
        else:
            print("\n🔍 No posts found. Let's debug this...")
            
            # Debug: Try a simple test
            reddit = initialize_reddit_flexible()
            if reddit:
                print("✅ Reddit connection working")
                
                # Test with a popular subreddit
                test_subreddit = reddit.subreddit('artificial')
                test_posts = list(test_subreddit.hot(limit=5))
                
                print(f"✅ Found {len(test_posts)} posts in r/artificial")
                
                if test_posts:
                    print("Sample posts:")
                    for i, post in enumerate(test_posts[:3]):
                        score = calculate_relevance_score(f"{post.title} {getattr(post, 'selftext', '')}")
                        print(f"  {i+1}. {post.title} (Relevance: {score})")
                else:
                    print("❌ No posts found in test subreddit")
            else:
                print("❌ Reddit connection failed")
        
        return len(reactions) > 0
    except Exception as e:
        logger.error(f"Flexible Reddit test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(test_reddit_flexible())
