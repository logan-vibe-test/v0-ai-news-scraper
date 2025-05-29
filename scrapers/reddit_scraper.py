"""
Reddit scraper for AI Voice News Scraper
"""
import asyncio
import logging
import praw
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')

# Subreddits to monitor
SUBREDDITS = [
    'MachineLearning',
    'LanguageTechnology',
    'artificial',
    'AIVoice',
    'OpenAI',
    'ElevenLabs'
]

async def initialize_reddit():
    """Initialize Reddit API client"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
        logger.error("Reddit API credentials not configured")
        return None
    
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        return reddit
    except Exception as e:
        logger.error(f"Error initializing Reddit client: {str(e)}")
        return None

def is_relevant_to_news(post_or_comment, news_items):
    """Check if a post or comment is relevant to our tracked news items"""
    # This is a simplified relevance check
    # In production, use vector embeddings or more sophisticated matching
    
    text = f"{post_or_comment.title if hasattr(post_or_comment, 'title') else ''} {post_or_comment.body if hasattr(post_or_comment, 'body') else ''}"
    text = text.lower()
    
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

async def process_subreddit(reddit, subreddit_name, news_items):
    """Process a single subreddit for relevant content"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        reactions = []
        
        # Get hot posts from the last 24 hours
        for post in subreddit.hot(limit=50):
            # Skip posts older than 24 hours
            post_time = datetime.fromtimestamp(post.created_utc)
            if datetime.now() - post_time > timedelta(hours=24):
                continue
                
            if is_relevant_to_news(post, news_items):
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
                
                # Find which news items it's related to
                for news in news_items:
                    if (news['title'].lower() in post.title.lower() or 
                        news['title'].lower() in post.selftext.lower()):
                        post_data['related_news'].append(news['_id'])
                
                reactions.append(post_data)
                
                # Get top comments
                post.comments.replace_more(limit=0)  # Remove MoreComments
                for comment in post.comments.list()[:10]:  # Top 10 comments
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
                        'related_news': post_data['related_news']
                    }
                    reactions.append(comment_data)
        
        logger.info(f"Processed r/{subreddit_name}: found {len(reactions)} relevant items")
        return reactions
    except Exception as e:
        logger.error(f"Error processing subreddit {subreddit_name}: {str(e)}")
        return []

async def scrape_reddit(news_items):
    """Scrape Reddit for reactions to news items"""
    reddit = await initialize_reddit()
    if not reddit:
        return []
    
    all_reactions = []
    tasks = []
    
    # Process each subreddit
    for subreddit in SUBREDDITS:
        # Note: Reddit API operations are synchronous, so we run them in a thread pool
        task = asyncio.to_thread(process_subreddit, reddit, subreddit, news_items)
        tasks.append(task)
    
    # Gather results
    results = await asyncio.gather(*tasks)
    for result in results:
        all_reactions.extend(result)
    
    logger.info(f"Total Reddit reactions found: {len(all_reactions)}")
    return all_reactions
