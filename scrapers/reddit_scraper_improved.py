"""
Improved Reddit scraper for AI Voice News Scraper
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

# Subreddits to monitor - expanded list
SUBREDDITS = [
    'MachineLearning',
    'LanguageTechnology', 
    'artificial',
    'OpenAI',
    'singularity',
    'ArtificialIntelligence',
    'deeplearning',
    'ChatGPT',
    'LocalLLaMA',
    'MediaSynthesis',
    'compsci',
    'technology'
]

# Voice AI keywords for filtering (defined locally to avoid import issues)
PRIMARY_VOICE_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'voice model', 'voice generation',
    'elevenlabs', 'openai voice', 'audio generation',
    'voice cloning', 'speech generation', 'voice assistant',
    'eleven labs', 'whisper', 'voice clone', 'synthetic voice',
    'ai voice', 'neural voice', 'voice bot'
]

SECONDARY_VOICE_KEYWORDS = [
    'speech', 'audio', 'voice', 'speaking', 'pronunciation',
    'accent', 'intonation', 'prosody', 'phoneme', 'vocoder',
    'neural voice', 'ai voice', 'voice over', 'voiceover'
]

COMPANY_KEYWORDS = [
    'eleven labs', 'elevenlabs', 'murf', 'speechify', 'descript',
    'resemble', 'replica', 'tortoise tts', 'bark', 'coqui',
    'festival', 'espeak', 'mary tts', 'wellsaid', 'lovo'
]

TECHNICAL_KEYWORDS = [
    'mel spectrogram', 'vocoder', 'griffin lim', 'wavenet',
    'tacotron', 'fastspeech', 'glow tts', 'neural vocoder',
    'autoregressive', 'transformer', 'diffusion', 'flow'
]

NEGATIVE_KEYWORDS = [
    'music generation', 'image generation', 'video generation',
    'text generation', 'code generation', 'voice actor',
    'voice actress', 'singing voice', 'music voice'
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
        # Test the connection
        reddit.user.me()
        logger.info("Reddit API connection successful")
        return reddit
    except Exception as e:
        logger.error(f"Error initializing Reddit client: {str(e)}")
        return None

def calculate_relevance_score(text):
    """Calculate relevance score for voice AI content"""
    text_lower = text.lower()
    score = 0
    
    # Primary voice AI keywords (high weight)
    for keyword in PRIMARY_VOICE_KEYWORDS:
        if keyword in text_lower:
            score += 10
    
    # Secondary keywords (medium weight)
    for keyword in SECONDARY_VOICE_KEYWORDS:
        if keyword in text_lower:
            score += 3
    
    # Company/product keywords (medium weight)
    for keyword in COMPANY_KEYWORDS:
        if keyword in text_lower:
            score += 5
    
    # Technical terms (low weight)
    for keyword in TECHNICAL_KEYWORDS:
        if keyword in text_lower:
            score += 2
    
    # Negative keywords (reduce score)
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            score -= 5
    
    return max(0, score)  # Don't allow negative scores

def is_relevant_to_voice_ai(post_or_comment, min_score=5):
    """Check if a post or comment is relevant to voice AI"""
    try:
        # Get text content
        title = getattr(post_or_comment, 'title', '')
        body = getattr(post_or_comment, 'body', '') or getattr(post_or_comment, 'selftext', '')
        
        text = f"{title} {body}"
        
        # Skip very short content
        if len(text.strip()) < 20:
            return False, 0
        
        # Calculate relevance score
        score = calculate_relevance_score(text)
        
        # Check if it meets minimum threshold
        is_relevant = score >= min_score
        
        return is_relevant, score
        
    except Exception as e:
        logger.warning(f"Error checking relevance: {str(e)}")
        return False, 0

async def process_subreddit(reddit, subreddit_name, time_filter='day', limit=100):
    """Process a single subreddit for voice AI content"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        reactions = []
        
        logger.info(f"Processing r/{subreddit_name}...")
        
        # Get posts from different time periods
        post_sources = [
            ('hot', subreddit.hot(limit=limit//3)),
            ('new', subreddit.new(limit=limit//3)),
            ('top', subreddit.top(time_filter=time_filter, limit=limit//3))
        ]
        
        processed_urls = set()  # Avoid duplicates
        
        for source_name, posts in post_sources:
            try:
                for post in posts:
                    # Skip if already processed
                    if post.url in processed_urls:
                        continue
                    processed_urls.add(post.url)
                    
                    # Skip posts older than 7 days
                    post_time = datetime.fromtimestamp(post.created_utc)
                    if datetime.now() - post_time > timedelta(days=7):
                        continue
                    
                    # Check relevance
                    is_relevant, score = is_relevant_to_voice_ai(post)
                    
                    if is_relevant:
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
                            'relevance_score': score,
                            'source_type': source_name,
                            'related_news': []
                        }
                        
                        reactions.append(post_data)
                        
                        # Get top comments for highly relevant posts
                        if score >= 15 and post.num_comments > 0:
                            try:
                                post.comments.replace_more(limit=0)
                                for comment in post.comments.list()[:5]:  # Top 5 comments
                                    if len(comment.body) > 50:  # Skip very short comments
                                        comment_relevant, comment_score = is_relevant_to_voice_ai(comment, min_score=3)
                                        
                                        if comment_relevant:
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
                                                'relevance_score': comment_score,
                                                'related_news': []
                                            }
                                            reactions.append(comment_data)
                            except Exception as e:
                                logger.warning(f"Error processing comments for post {post.id}: {str(e)}")
                        
                        # Limit to prevent too many results from one subreddit
                        if len(reactions) >= 20:
                            break
                
                if len(reactions) >= 20:
                    break
                    
            except Exception as e:
                logger.warning(f"Error processing {source_name} posts in r/{subreddit_name}: {str(e)}")
                continue
        
        logger.info(f"Found {len(reactions)} relevant items in r/{subreddit_name}")
        return reactions
        
    except Exception as e:
        logger.error(f"Error processing subreddit {subreddit_name}: {str(e)}")
        return []

async def scrape_reddit(news_items=None):
    """Scrape Reddit for voice AI content"""
    reddit = await initialize_reddit()
    if not reddit:
        logger.warning("Reddit not available, returning empty results")
        return []
    
    logger.info(f"Starting Reddit scraping across {len(SUBREDDITS)} subreddits...")
    
    all_reactions = []
    
    # Process subreddits in smaller batches to avoid rate limiting
    batch_size = 3
    for i in range(0, len(SUBREDDITS), batch_size):
        batch = SUBREDDITS[i:i + batch_size]
        tasks = []
        
        for subreddit in batch:
            task = asyncio.create_task(
                asyncio.to_thread(process_subreddit, reddit, subreddit)
            )
            tasks.append(task)
        
        # Process batch
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_reactions.extend(result)
                else:
                    logger.error(f"Task failed: {result}")
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
        
        # Small delay between batches to be respectful to Reddit API
        if i + batch_size < len(SUBREDDITS):
            await asyncio.sleep(2)
    
    # Sort by relevance score and recency
    all_reactions.sort(key=lambda x: (x.get('relevance_score', 0), x.get('created_utc', 0)), reverse=True)
    
    # Limit total results
    all_reactions = all_reactions[:50]
    
    logger.info(f"Reddit scraping completed: {len(all_reactions)} total reactions found")
    
    # Log some examples
    if all_reactions:
        logger.info("Top Reddit findings:")
        for i, reaction in enumerate(all_reactions[:3]):
            logger.info(f"  {i+1}. r/{reaction['subreddit']}: {reaction.get('title', reaction.get('content', ''))[:80]}... (score: {reaction.get('relevance_score', 0)})")
    
    return all_reactions

# For backward compatibility
async def scrape_reddit_for_news(news_items):
    """Legacy function name - calls the main scrape_reddit function"""
    return await scrape_reddit(news_items)
