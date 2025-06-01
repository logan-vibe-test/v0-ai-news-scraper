"""
Improved Reddit scraper for AI Voice News Scraper
"""
import asyncio
import logging
import praw
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

# Subreddits to monitor - expanded list
SUBREDDITS = [
    'MachineLearning',
    'LanguageTechnology',
    'artificial',
    'AIVoice',
    'OpenAI',
    'ElevenLabs',
    'TextToSpeech',
    'VoiceActing',  # May have discussions about AI replacing voice actors
    'audioengineering',  # Sometimes discusses voice AI
    'VoiceOver',
    'AIGeneratedContent',
    'AIArt',  # Sometimes includes audio/voice discussions
    'GPT4',
    'LocalLLaMA',  # Open source AI community
    'AnthropicAI'
]

# Voice AI keywords for filtering
VOICE_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis', 
    'voice synthesis', 'voice model', 'voice generation',
    'elevenlabs', 'openai voice', 'audio generation',
    'voice clone', 'voice cloning', 'synthetic voice',
    'ai voice', 'neural voice', 'voice assistant'
]

def initialize_reddit():
    """Initialize Reddit API client with better error handling"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.error("Reddit API credentials not configured")
        return None
    
    try:
        # Try with username/password if available (better API limits)
        if REDDIT_USERNAME and REDDIT_PASSWORD:
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD
            )
            logger.info("Initialized Reddit client with user authentication")
        else:
            # Fall back to read-only mode
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
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

def process_subreddit(reddit, subreddit_name, max_posts=25):
    """Process a single subreddit for voice AI content"""
    try:
        logger.info(f"Processing r/{subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        reactions = []
        
        # Get hot and new posts
        posts = list(subreddit.hot(limit=max_posts))
        posts.extend(list(subreddit.new(limit=max_posts)))
        
        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in posts:
            if post.id not in seen_ids:
                seen_ids.add(post.id)
                unique_posts.append(post)
        
        logger.info(f"Found {len(unique_posts)} unique posts in r/{subreddit_name}")
        
        # Process each post
        for post in unique_posts:
            # Skip posts older than 3 days
            post_time = datetime.fromtimestamp(post.created_utc)
            if datetime.now() - post_time > timedelta(days=3):
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
                
                # Get top comments (with rate limiting)
                try:
                    post.comments.replace_more(limit=0)  # Remove MoreComments
                    for comment in list(post.comments)[:10]:  # Top 10 comments
                        if is_relevant_to_voice_ai(comment.body):
                            comment_data = {
                                'platform': 'reddit',
                                'type': 'comment',
                                'subreddit': subreddit_name,
                                'parent_id': post.id,
                                'content': comment.body,
                                'url': f"https://reddit.com{comment.permalink}",
                                'author': comment.author.name if comment.author else '[deleted]',
                                'score': comment.score,
                                'created_utc': comment.created_utc,
                                'related_news': []
                            }
                            reactions.append(comment_data)
                except Exception as e:
                    logger.warning(f"Error processing comments for {post.title}: {str(e)}")
                
                # Rate limiting to avoid API issues
                time.sleep(0.5)
        
        logger.info(f"Found {len(reactions)} voice AI related items in r/{subreddit_name}")
        return reactions
    except Exception as e:
        logger.error(f"Error processing subreddit {subreddit_name}: {str(e)}")
        return []

async def scrape_reddit(news_items=None):
    """Scrape Reddit for voice AI content"""
    logger.info("Starting Reddit scraper")
    
    # Initialize Reddit client
    reddit = initialize_reddit()
    if not reddit:
        logger.error("Failed to initialize Reddit client")
        return []
    
    all_reactions = []
    
    # Process each subreddit
    for subreddit in SUBREDDITS:
        try:
            # Process in a separate thread since Reddit API is synchronous
            reactions = await asyncio.to_thread(process_subreddit, reddit, subreddit)
            all_reactions.extend(reactions)
            
            # Rate limiting between subreddits
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error processing subreddit {subreddit}: {str(e)}")
    
    # Match reactions to news items if provided
    if news_items:
        for reaction in all_reactions:
            for news in news_items:
                # Check if reaction mentions news title
                if news['title'].lower() in reaction['content'].lower():
                    reaction['related_news'].append(news['_id'])
    
    logger.info(f"Total Reddit reactions found: {len(all_reactions)}")
    return all_reactions

async def test_reddit_scraper():
    """Test the Reddit scraper functionality"""
    logger.info("Testing Reddit scraper")
    reactions = await scrape_reddit()
    
    print(f"\n{'='*60}")
    print(f"Found {len(reactions)} voice AI related posts/comments on Reddit")
    print(f"{'='*60}")
    
    for i, reaction in enumerate(reactions[:10]):  # Show first 10
        print(f"\n{i+1}. r/{reaction['subreddit']} - {reaction['type']}")
        if reaction['type'] == 'post':
            print(f"   Title: {reaction['title']}")
        print(f"   Content: {reaction['content'][:150]}...")
        print(f"   URL: {reaction['url']}")
        print(f"   Score: {reaction['score']}")
    
    return reactions

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the test
    asyncio.run(test_reddit_scraper())
