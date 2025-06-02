"""
Simplified Reddit scraper without spacy/nltk dependencies
"""
import asyncio
import logging
import os
import ssl
import certifi
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper_v1.0')

# Voice AI keywords for filtering
VOICE_AI_KEYWORDS = [
    'voice ai', 'ai voice', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'voice generation', 'voice model', 'neural voice',
    'voice cloning', 'voice clone', 'synthetic voice', 'artificial voice',
    'elevenlabs', 'eleven labs', 'openai voice', 'whisper ai',
    'murf ai', 'speechify', 'resemble ai', 'wellsaid labs'
]

# Target subreddits
TARGET_SUBREDDITS = [
    'MachineLearning', 'artificial', 'OpenAI', 'technology',
    'futurology', 'singularity', 'LocalLLaMA'
]

def simple_sentiment_analysis(text: str) -> tuple[str, str]:
    """Simple sentiment analysis without NLTK"""
    text_lower = text.lower()
    
    positive_words = [
        'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'incredible',
        'breakthrough', 'impressive', 'revolutionary', 'game-changing',
        'love', 'perfect', 'brilliant', 'outstanding', 'wonderful'
    ]
    
    negative_words = [
        'terrible', 'awful', 'bad', 'horrible', 'disappointing', 'useless',
        'broken', 'failed', 'worst', 'hate', 'sucks', 'garbage',
        'concerning', 'worried', 'dangerous', 'scary'
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
    """Simple text summarization without spacy"""
    if not text:
        return "No content available"
    
    # Split into sentences (simple approach)
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Take first 2-3 sentences or until we hit max_length
    summary = ""
    for sentence in sentences[:3]:
        if len(summary + sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip() or text[:max_length] + "..."

class SimpleRedditScraper:
    """Simplified Reddit scraper without heavy dependencies"""
    
    def __init__(self):
        self.reddit = None
        self._initialize_reddit()
    
    def _initialize_reddit(self) -> bool:
        """Initialize Reddit API client"""
        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
            logger.warning("Reddit API credentials not configured")
            return False
        
        try:
            import praw
            import requests
            
            # Create session with SSL fixes
            session = requests.Session()
            session.verify = False
            
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                read_only=True,
                requestor_kwargs={'session': session}
            )
            
            logger.info("✅ Reddit API connection successful")
            return True
            
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
        
        for keyword in VOICE_AI_KEYWORDS:
            if keyword in text_lower:
                matched_keywords.append(keyword)
        
        return len(matched_keywords) > 0, matched_keywords
    
    async def scrape_reddit(self, news_items: Optional[List] = None) -> List[Dict]:
        """Scrape Reddit for voice AI content"""
        if not self.reddit:
            logger.warning("Reddit not available, returning empty results")
            return []
        
        logger.info(f"🚀 Starting Reddit scraping across {len(TARGET_SUBREDDITS)} subreddits...")
        
        all_posts = []
        
        for subreddit_name in TARGET_SUBREDDITS:
            try:
                logger.info(f"🔍 Scanning r/{subreddit_name}...")
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get top 1 post from hot
                for post in subreddit.hot(limit=10):  # Check more to find voice AI content
                    # Check if post is about voice AI
                    combined_text = f"{post.title} {getattr(post, 'selftext', '')}"
                    is_relevant, matched_keywords = self._is_voice_ai_related(combined_text)
                    
                    if is_relevant:
                        # Analyze sentiment
                        sentiment, sentiment_emoji = simple_sentiment_analysis(combined_text)
                        
                        # Create summary
                        summary = simple_summarize(combined_text)
                        
                        post_data = {
                            'platform': 'reddit',
                            'subreddit': subreddit_name,
                            'title': post.title,
                            'content': getattr(post, 'selftext', '')[:300],
                            'url': f"https://reddit.com{post.permalink}",
                            'author': str(post.author) if post.author else '[deleted]',
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_date': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M'),
                            'sentiment': sentiment,
                            'sentiment_emoji': sentiment_emoji,
                            'summary': summary,
                            'matched_keywords': matched_keywords,
                            'external_url': post.url if post.url != f"https://reddit.com{post.permalink}" else None
                        }
                        
                        all_posts.append(post_data)
                        logger.info(f"📝 Found: {post.title[:60]}... (sentiment: {sentiment})")
                        break  # Only take 1 post per subreddit
                
            except Exception as e:
                logger.error(f"❌ Error processing r/{subreddit_name}: {str(e)}")
                continue
        
        logger.info(f"🎯 Reddit scraping completed: {len(all_posts)} posts found")
        return all_posts

# Create global instance
_simple_reddit_scraper = SimpleRedditScraper()

# Main function for compatibility
async def scrape_reddit(news_items: Optional[List] = None) -> List[Dict]:
    """Scrape Reddit for voice AI discussions (simplified version)"""
    return await _simple_reddit_scraper.scrape_reddit(news_items)
