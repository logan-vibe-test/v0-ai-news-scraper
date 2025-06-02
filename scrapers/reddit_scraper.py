"""
Reddit scraper for AI Voice News Scraper - SSL FIXED VERSION
Gets top posts from target subreddits with AI summaries and sentiment analysis
"""
import asyncio
import logging
import os
import ssl
import certifi
import urllib3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper_v1.0')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Subreddits to monitor - focused on AI, tech, and voice-related communities
TARGET_SUBREDDITS = [
    # AI/ML focused
    'MachineLearning',
    'artificial',
    'OpenAI',
    'singularity',
    'LocalLLaMA',
    'LanguageTechnology',
    
    # Tech and media
    'technology',
    'futurology',
    'MediaSynthesis',
    'AudioEngineering',
    'podcasting',
    
    # Voice/Audio specific
    'VoiceActing',
    'audiobooks',
    
    # Startup/Business
    'startups',
    'entrepreneur'
]

def fix_ssl_context():
    """Fix SSL context for Reddit API"""
    try:
        # Create a custom SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Set the SSL context globally
        ssl._create_default_https_context = lambda: ssl_context
        
        logger.info("✅ SSL context configured successfully")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not configure SSL context: {e}")
        return False

class RedditScraper:
    """Reddit scraper that gets top posts with summaries and sentiment analysis - SSL FIXED"""
    
    def __init__(self):
        self.reddit = None
        self.openai_client = None
        # Fix SSL first
        fix_ssl_context()
        self._initialize_reddit()
        self._initialize_openai()
    
    def _initialize_reddit(self) -> bool:
        """Initialize Reddit API client with SSL fixes"""
        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
            logger.warning("Reddit API credentials not configured")
            return False
        
        try:
            import praw
            import prawcore
            
            # Configure requestor with SSL fixes
            requestor_kwargs = {
                'session': self._create_session_with_ssl_fix()
            }
            
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                read_only=True,
                requestor_kwargs=requestor_kwargs
            )
            
            # Test the connection with error handling
            try:
                # Try to access a simple endpoint
                self.reddit.user.me()
                logger.info("✅ Reddit API connection successful")
                return True
            except Exception as auth_error:
                logger.warning(f"Reddit auth test failed: {auth_error}")
                # Try without authentication test
                try:
                    # Test with a simple subreddit access
                    test_sub = self.reddit.subreddit('test')
                    list(test_sub.hot(limit=1))
                    logger.info("✅ Reddit API connection successful (without auth test)")
                    return True
                except Exception as e:
                    logger.error(f"Reddit connection completely failed: {e}")
                    return False
            
        except ImportError:
            logger.error("❌ PRAW not installed. Run: pip install praw")
            return False
        except Exception as e:
            logger.error(f"❌ Reddit initialization failed: {str(e)}")
            return False
    
    def _create_session_with_ssl_fix(self):
        """Create a requests session with SSL fixes"""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            
            # Configure retries
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            # Create adapter with SSL verification disabled
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Disable SSL verification for this session
            session.verify = False
            
            # Set headers
            session.headers.update({
                'User-Agent': REDDIT_USER_AGENT
            })
            
            logger.info("✅ Created session with SSL fixes")
            return session
            
        except Exception as e:
            logger.warning(f"Could not create custom session: {e}")
            return None
    
    def _initialize_openai(self) -> bool:
        """Initialize OpenAI client for summarization and sentiment analysis"""
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured - summaries and sentiment will be basic")
            return False
        
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ OpenAI client initialized")
            return True
        except ImportError:
            logger.error("❌ OpenAI package not installed. Run: pip install openai")
            return False
        except Exception as e:
            logger.error(f"❌ OpenAI initialization failed: {str(e)}")
            return False
    
    def _analyze_sentiment_basic(self, title: str, content: str) -> Tuple[str, str]:
        """Basic sentiment analysis using keyword matching"""
        text = f"{title} {content}".lower()
        
        # Positive indicators
        positive_words = [
            'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'love', 'best',
            'incredible', 'breakthrough', 'revolutionary', 'impressive', 'wonderful',
            'excited', 'thrilled', 'perfect', 'outstanding', 'brilliant', 'success',
            'achievement', 'progress', 'innovation', 'advance', 'improvement'
        ]
        
        # Negative indicators
        negative_words = [
            'terrible', 'awful', 'bad', 'worst', 'hate', 'horrible', 'disappointing',
            'failed', 'failure', 'problem', 'issue', 'concern', 'worried', 'scary',
            'dangerous', 'threat', 'risk', 'decline', 'crisis', 'controversy',
            'criticism', 'backlash', 'outrage', 'angry', 'frustrated'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count and positive_count > 0:
            return "positive", "😊"
        elif negative_count > positive_count and negative_count > 0:
            return "negative", "😟"
        else:
            return "neutral", "😐"
    
    async def _generate_summary_and_sentiment(self, title: str, content: str, url: str) -> Tuple[str, str, str]:
        """Generate AI summary and sentiment analysis"""
        if not self.openai_client:
            # Fallback to basic analysis
            summary = self._create_basic_summary(title, content)
            sentiment, emoji = self._analyze_sentiment_basic(title, content)
            return summary, sentiment, emoji
        
        try:
            # Prepare content for analysis
            post_text = f"Title: {title}\n\nContent: {content[:1000]}"  # Limit content length
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI assistant that analyzes Reddit posts. For each post, provide:
1. A concise 2-3 sentence summary of the main points
2. The overall sentiment (positive, negative, or neutral)

Format your response as:
SUMMARY: [your summary here]
SENTIMENT: [positive/negative/neutral]

Guidelines for sentiment:
- Positive: Excitement, praise, good news, achievements, breakthroughs
- Negative: Criticism, concerns, problems, disappointments, fears
- Neutral: Factual discussions, questions, balanced viewpoints"""
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze this Reddit post:\n\n{post_text}"
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse the response
            summary = ""
            sentiment = "neutral"
            
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('SENTIMENT:'):
                    sentiment = line.replace('SENTIMENT:', '').strip().lower()
            
            # If parsing failed, use the whole response as summary
            if not summary:
                summary = response_text
            
            # Map sentiment to emoji
            emoji_map = {
                'positive': '😊',
                'negative': '😟',
                'neutral': '😐'
            }
            emoji = emoji_map.get(sentiment, '😐')
            
            return summary, sentiment, emoji
            
        except Exception as e:
            logger.warning(f"Error generating AI analysis: {str(e)}")
            # Fallback to basic analysis
            summary = self._create_basic_summary(title, content)
            sentiment, emoji = self._analyze_sentiment_basic(title, content)
            return summary, sentiment, emoji
    
    def _create_basic_summary(self, title: str, content: str) -> str:
        """Create a basic summary when AI is not available"""
        if content and len(content) > 100:
            # Take first 150 characters of content
            summary = content[:150].strip()
            if not summary.endswith('.'):
                summary += "..."
            return summary
        else:
            return "Discussion post - see full content at link."
    
    def _safe_reddit_operation(self, operation, *args, **kwargs):
        """Safely execute Reddit operations with error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Reddit operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
    
    async def _get_top_posts_from_subreddit(self, subreddit_name: str, limit: int = 5) -> List[Dict]:
        """Get top posts from a specific subreddit with sentiment analysis - SSL SAFE"""
        if not self.reddit:
            return []
        
        try:
            logger.info(f"🔍 Getting top {limit} posts from r/{subreddit_name}...")
            
            # Safely get subreddit
            subreddit = self._safe_reddit_operation(self.reddit.subreddit, subreddit_name)
            posts = []
            
            # Get hot posts with error handling
            try:
                hot_posts = self._safe_reddit_operation(lambda: list(subreddit.hot(limit=limit * 2)))
            except Exception as e:
                logger.error(f"Failed to get hot posts from r/{subreddit_name}: {e}")
                return []
            
            for post in hot_posts:
                try:
                    # Skip stickied posts (announcements, rules, etc.)
                    if getattr(post, 'stickied', False):
                        continue
                    
                    # Skip very old posts (older than 7 days)
                    post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)
                    if post_age > timedelta(days=7):
                        continue
                    
                    # Get post content safely
                    content = getattr(post, 'selftext', '') or ''
                    
                    # If it's a link post, note that
                    post_url = getattr(post, 'url', '')
                    post_permalink = getattr(post, 'permalink', '')
                    reddit_url = f"https://reddit.com{post_permalink}"
                    
                    if not content and post_url != reddit_url:
                        content = f"Link post: {post_url}"
                    
                    post_data = {
                        'platform': 'reddit',
                        'type': 'post',
                        'subreddit': subreddit_name,
                        'title': getattr(post, 'title', 'No title'),
                        'content': content[:500],  # Limit content length
                        'full_content': content,  # Keep full content for analysis
                        'url': reddit_url,
                        'external_url': post_url if post_url != reddit_url else None,
                        'author': str(getattr(post, 'author', '[deleted]')),
                        'score': getattr(post, 'score', 0),
                        'created_utc': getattr(post, 'created_utc', 0),
                        'num_comments': getattr(post, 'num_comments', 0),
                        'created_date': datetime.fromtimestamp(getattr(post, 'created_utc', 0)).strftime('%Y-%m-%d %H:%M'),
                        'summary': '',
                        'sentiment': 'neutral',
                        'sentiment_emoji': '😐'
                    }
                    
                    # Generate summary and sentiment analysis
                    summary, sentiment, emoji = await self._generate_summary_and_sentiment(
                        post_data['title'], 
                        post_data['full_content'], 
                        post_data['url']
                    )
                    
                    post_data['summary'] = summary
                    post_data['sentiment'] = sentiment
                    post_data['sentiment_emoji'] = emoji
                    
                    posts.append(post_data)
                    logger.info(f"📝 Added: {post_data['title'][:50]}... (score: {post_data['score']}, sentiment: {sentiment} {emoji})")
                    
                    # Stop when we have enough posts
                    if len(posts) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing individual post: {e}")
                    continue
            
            logger.info(f"✅ Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error getting posts from r/{subreddit_name}: {str(e)}")
            return []
    
    async def scrape_reddit(self, news_items: Optional[List] = None) -> List[Dict]:
        """
        Get top 5 posts from each target subreddit with AI summaries and sentiment - SSL SAFE
        
        Args:
            news_items: Optional list of news items (not used, kept for compatibility)
            
        Returns:
            List of top Reddit posts with summaries and sentiment analysis
        """
        if not self.reddit:
            logger.warning("Reddit not available, returning empty results")
            return []
        
        logger.info(f"🚀 Getting top 5 posts from {len(TARGET_SUBREDDITS)} subreddits with sentiment analysis...")
        
        all_posts = []
        
        # Process subreddits one by one to avoid SSL issues
        for subreddit_name in TARGET_SUBREDDITS:
            try:
                logger.info(f"Processing r/{subreddit_name}...")
                posts = await self._get_top_posts_from_subreddit(subreddit_name, limit=5)
                all_posts.extend(posts)
                
                # Small delay between subreddits to be nice to Reddit
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to process r/{subreddit_name}: {e}")
                continue
        
        # Sort by score (popularity) within each subreddit, but maintain subreddit grouping
        subreddit_groups = {}
        for post in all_posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_groups:
                subreddit_groups[subreddit] = []
            subreddit_groups[subreddit].append(post)
        
        # Sort posts within each subreddit by score
        for subreddit in subreddit_groups:
            subreddit_groups[subreddit].sort(key=lambda x: x['score'], reverse=True)
        
        # Flatten back to a single list, maintaining subreddit order
        organized_posts = []
        for subreddit in TARGET_SUBREDDITS:
            if subreddit in subreddit_groups:
                organized_posts.extend(subreddit_groups[subreddit])
        
        logger.info(f"🎯 Reddit scraping completed: {len(organized_posts)} total posts collected")
        
        # Log summary by subreddit and sentiment
        if organized_posts:
            logger.info("📊 Posts collected by subreddit:")
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for subreddit in TARGET_SUBREDDITS:
                subreddit_posts = [p for p in organized_posts if p['subreddit'] == subreddit]
                if subreddit_posts:
                    sentiments = [p['sentiment'] for p in subreddit_posts]
                    pos = sentiments.count('positive')
                    neg = sentiments.count('negative')
                    neu = sentiments.count('neutral')
                    
                    logger.info(f"  r/{subreddit}: {len(subreddit_posts)} posts (😊{pos} 😟{neg} 😐{neu})")
                    
                    # Update overall counts
                    sentiment_counts['positive'] += pos
                    sentiment_counts['negative'] += neg
                    sentiment_counts['neutral'] += neu
            
            logger.info(f"📈 Overall sentiment: 😊{sentiment_counts['positive']} 😟{sentiment_counts['negative']} 😐{sentiment_counts['neutral']}")
        
        return organized_posts

# Create global instance
_reddit_scraper = RedditScraper()

# Main function for compatibility with existing code
async def scrape_reddit(news_items: Optional[List] = None) -> List[Dict]:
    """
    Scrape Reddit for top posts with summaries and sentiment analysis - SSL FIXED
    
    Args:
        news_items: Optional list of news items (not used, kept for compatibility)
        
    Returns:
        List of top Reddit posts with AI-generated summaries and sentiment
    """
    return await _reddit_scraper.scrape_reddit(news_items)

# For testing
async def main():
    """Test the Reddit scraper - SSL FIXED"""
    posts = await scrape_reddit()
    print(f"\n📊 Results: {len(posts)} posts collected")
    
    if posts:
        # Group by subreddit for display
        current_subreddit = None
        for i, post in enumerate(posts):
            if post['subreddit'] != current_subreddit:
                current_subreddit = post['subreddit']
                print(f"\n🔥 r/{current_subreddit}")
                print("=" * 50)
            
            print(f"\n{i+1}. {post['title']}")
            print(f"   👍 {post['score']} upvotes | 💬 {post['num_comments']} comments | 📅 {post['created_date']}")
            print(f"   🎭 Sentiment: {post['sentiment'].title()} {post['sentiment_emoji']}")
            print(f"   📝 Summary: {post['summary']}")
            print(f"   🔗 Reddit: {post['url']}")
            if post.get('external_url'):
                print(f"   🌐 External: {post['external_url']}")

if __name__ == "__main__":
    asyncio.run(main())
