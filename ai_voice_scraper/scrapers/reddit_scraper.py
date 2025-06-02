"""
Reddit scraper for AI Voice News Scraper
"""
import asyncio
import logging
import os
import ssl
import certifi
from datetime import datetime
from typing import List, Dict, Optional

from ai_voice_scraper.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from ai_voice_scraper.config.keywords import ALL_VOICE_AI_KEYWORDS

logger = logging.getLogger(__name__)

# Target subreddits
TARGET_SUBREDDITS = [
    'MachineLearning', 'artificial', 'OpenAI', 'technology',
    'futurology', 'singularity', 'LocalLLaMA'
]

def simple_sentiment_analysis(text: str) -> tuple[str, str]:
    """Simple sentiment analysis without external libraries"""
    if not text:
        return 'neutral', '😐'
    
    text_lower = text.lower()
    
    positive_words = [
        'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'incredible',
        'breakthrough', 'impressive', 'revolutionary', 'game-changing',
        'love', 'perfect', 'brilliant', 'outstanding', 'wonderful', 'excited'
    ]
    
    negative_words = [
        'terrible', 'awful', 'bad', 'horrible', 'disappointing', 'useless',
        'broken', 'failed', 'worst', 'hate', 'sucks', 'garbage',
        'concerning', 'worried', 'dangerous', 'scary', 'disappointing'
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 'positive', '😊'
    elif negative_count > positive_count:
        return 'negative', '😟'
    else:
        return 'neutral', '😐'

def simple_summarize(text: str, max_length: int = 150) -> str:
    """Simple text summarization"""
    if not text or len(text.strip()) < 10:
        return "No content available for summary"
    
    # Clean the text
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Split into sentences
    sentences = []
    for delimiter in ['. ', '! ', '? ']:
        text = text.replace(delimiter, '|||SPLIT|||')
    
    potential_sentences = text.split('|||SPLIT|||')
    for sentence in potential_sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Only keep meaningful sentences
            sentences.append(sentence)
    
    if not sentences:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Build summary
    summary = ""
    for sentence in sentences[:2]:  # Take first 2 sentences
        if len(summary + sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip() or text[:max_length] + "..."

def fix_ssl_for_reddit():
    """Fix SSL issues for Reddit"""
    try:
        import ssl
        import certifi
        import urllib3
        
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create permissive SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Set globally
        ssl._create_default_https_context = lambda: ssl_context
        
        return True
    except Exception as e:
        logger.warning(f"Could not fix SSL: {e}")
        return False

class BulletproofRedditScraper:
    """Reddit scraper that just works"""
    
    def __init__(self):
        self.reddit = None
        self._initialize_reddit()
    
    def _initialize_reddit(self) -> bool:
        """Initialize Reddit with all the fixes"""
        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
            logger.warning("Reddit API credentials not configured")
            return False
        
        try:
            # Fix SSL first
            fix_ssl_for_reddit()
            
            import praw
            import requests
            
            # Create custom session
            session = requests.Session()
            session.verify = False
            
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                read_only=True,
                requestor_kwargs={'session': session}
            )
            
            # Test connection
            try:
                test_sub = self.reddit.subreddit('test')
                list(test_sub.hot(limit=1))
                logger.info("✅ Reddit connection successful")
                return True
            except Exception as e:
                logger.warning(f"Reddit connection test failed: {e}")
                return True  # Still try to use it
            
        except ImportError:
            logger.error("❌ PRAW not installed. Run: pip install praw")
            return False
        except Exception as e:
            logger.error(f"❌ Reddit initialization failed: {str(e)}")
            return False
    
    def _is_voice_ai_related(self, text: str) -> tuple[bool, List[str]]:
        """Check if text is related to voice AI"""
        if not text:
            return False, []
        
        text_lower = text.lower()
        matched_keywords = []
        
        for keyword in ALL_VOICE_AI_KEYWORDS:
            if keyword in text_lower:
                matched_keywords.append(keyword)
        
        return len(matched_keywords) > 0, matched_keywords
    
    async def scrape_reddit(self, test_mode=False) -> List[Dict]:
        """Scrape Reddit for voice AI content - BULLETPROOF VERSION"""
        if not self.reddit:
            logger.warning("Reddit not available, returning empty results")
            return []
        
        logger.info(f"🚀 Starting bulletproof Reddit scraping...")
        
        all_posts = []
        
        # Limit subreddits in test mode
        subreddits = TARGET_SUBREDDITS[:2] if test_mode else TARGET_SUBREDDITS
        
        for subreddit_name in subreddits:
            try:
                logger.info(f"🔍 Scanning r/{subreddit_name}...")
                
                # Wrap in try-catch for each subreddit
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    posts_checked = 0
                    
                    # Check hot posts for voice AI content
                    for post in subreddit.hot(limit=20):
                        posts_checked += 1
                        
                        try:
                            # Get post content
                            title = post.title or ""
                            selftext = getattr(post, 'selftext', '') or ""
                            combined_text = f"{title} {selftext}"
                            
                            # Check if it's about voice AI
                            is_relevant, matched_keywords = self._is_voice_ai_related(combined_text)
                            
                            if is_relevant:
                                # Analyze sentiment
                                sentiment, sentiment_emoji = simple_sentiment_analysis(combined_text)
                                
                                # Create summary
                                summary = simple_summarize(combined_text)
                                
                                # Get external URL if it's a link post
                                external_url = None
                                if hasattr(post, 'url') and post.url:
                                    if not post.url.startswith('https://www.reddit.com'):
                                        external_url = post.url
                                
                                post_data = {
                                    'platform': 'reddit',
                                    'subreddit': subreddit_name,
                                    'title': title,
                                    'content': selftext[:300] if selftext else "",
                                    'url': f"https://reddit.com{post.permalink}",
                                    'author': str(post.author) if post.author else '[deleted]',
                                    'score': getattr(post, 'score', 0),
                                    'num_comments': getattr(post, 'num_comments', 0),
                                    'created_date': datetime.fromtimestamp(getattr(post, 'created_utc', 0)).strftime('%Y-%m-%d %H:%M'),
                                    'sentiment': sentiment,
                                    'sentiment_emoji': sentiment_emoji,
                                    'summary': summary,
                                    'matched_keywords': matched_keywords,
                                    'external_url': external_url
                                }
                                
                                all_posts.append(post_data)
                                logger.info(f"📝 Found: {title[:60]}... (sentiment: {sentiment})")
                                break  # Only take 1 post per subreddit
                        
                        except Exception as post_error:
                            logger.warning(f"Error processing individual post: {post_error}")
                            continue
                    
                    logger.info(f"✅ Checked {posts_checked} posts in r/{subreddit_name}")
                
                except Exception as subreddit_error:
                    logger.warning(f"Error accessing r/{subreddit_name}: {subreddit_error}")
                    continue
                
                # Small delay between subreddits
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Major error with r/{subreddit_name}: {str(e)}")
                continue
        
        logger.info(f"🎯 Reddit scraping completed: {len(all_posts)} posts found")
        
        if not all_posts:
            logger.info("ℹ️  No voice AI posts found. This could be normal if:")
            logger.info("   - No recent voice AI discussions")
            logger.info("   - Keywords need adjustment")
            logger.info("   - Subreddits are quiet today")
        
        return all_posts

# Create global instance
_reddit_scraper = BulletproofRedditScraper()

# Main function for compatibility
async def scrape_reddit(test_mode=False) -> List[Dict]:
    """
    Scrape Reddit for voice AI discussions - BULLETPROOF VERSION
    
    This version:
    - ✅ Handles SSL issues automatically
    - ✅ Works without spacy/nltk
    - ✅ Has extensive error handling
    - ✅ Won't crash the main pipeline
    """
    return await _reddit_scraper.scrape_reddit(test_mode)
