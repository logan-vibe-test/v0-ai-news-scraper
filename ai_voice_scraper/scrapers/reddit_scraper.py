"""
Reddit scraper for AI Voice News Scraper
Monitors Reddit for discussions about AI voice technology
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
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
    # Core voice AI terms
    'voice ai', 'ai voice', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'voice generation', 'voice model', 'neural voice',
    'voice cloning', 'voice clone', 'synthetic voice', 'artificial voice',
    
    # Companies and products
    'elevenlabs', 'eleven labs', 'openai voice', 'whisper ai',
    'murf ai', 'speechify', 'resemble ai', 'wellsaid labs',
    'play.ht', 'coqui ai', 'bark tts', 'tortoise tts',
    'replica studios', 'descript overdub', 'lovo ai',
    
    # Technical terms
    'vocoder', 'neural vocoder', 'voice transformer',
    'voice conversion', 'speech-to-speech', 'voice streaming',
    'mel spectrogram', 'voice encoder', 'speaker embedding',
    
    # Applications
    'ai voiceover', 'ai dubbing', 'voice assistant api',
    'ai narrator', 'ai audiobook', 'voice avatar',
    'digital voice twin', 'custom voice model'
]

# Subreddits to monitor for voice AI content
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
    'VoiceActing',  # might discuss AI impact
    'audiobooks',   # might discuss AI narration
    
    # Startup/Business
    'startups',
    'entrepreneur'
]

class RedditScraper:
    """Reddit scraper for AI voice content"""
    
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
            
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                read_only=True  # We only need read access
            )
            
            # Test the connection
            self.reddit.user.me()
            logger.info("✅ Reddit API connection successful")
            return True
            
        except ImportError:
            logger.error("❌ PRAW not installed. Run: pip install praw")
            return False
        except Exception as e:
            logger.error(f"❌ Reddit initialization failed: {str(e)}")
            return False
    
    def _is_voice_ai_related(self, text: str, min_keywords: int = 1) -> tuple[bool, List[str]]:
        """
        Check if text is related to voice AI
        
        Args:
            text: Text to analyze
            min_keywords: Minimum number of keywords required
            
        Returns:
            Tuple of (is_relevant, matched_keywords)
        """
        if not text:
            return False, []
        
        text_lower = text.lower()
        matched_keywords = []
        
        for keyword in VOICE_AI_KEYWORDS:
            if keyword in text_lower:
                matched_keywords.append(keyword)
        
        is_relevant = len(matched_keywords) >= min_keywords
        return is_relevant, matched_keywords
    
    def _calculate_relevance_score(self, post_data: Dict) -> int:
        """Calculate relevance score for ranking posts"""
        score = 0
        
        # Base score from Reddit score (upvotes - downvotes)
        score += min(post_data.get('score', 0), 100)  # Cap at 100
        
        # Bonus for number of matched keywords
        score += len(post_data.get('matched_keywords', [])) * 10
        
        # Bonus for recent posts (within last 24 hours)
        created_time = datetime.fromtimestamp(post_data.get('created_utc', 0))
        hours_old = (datetime.now() - created_time).total_seconds() / 3600
        if hours_old < 24:
            score += 20
        elif hours_old < 72:
            score += 10
        
        # Bonus for posts with engagement (comments)
        score += min(post_data.get('num_comments', 0), 50)  # Cap at 50
        
        # Bonus for certain high-value subreddits
        high_value_subreddits = ['MachineLearning', 'OpenAI', 'artificial']
        if post_data.get('subreddit') in high_value_subreddits:
            score += 15
        
        return score
    
    async def _process_subreddit(self, subreddit_name: str, limit: int = 25) -> List[Dict]:
        """Process a single subreddit for voice AI content"""
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            processed_urls = set()  # Avoid duplicates
            
            logger.info(f"🔍 Scanning r/{subreddit_name}...")
            
            # Get posts from different sorting methods
            post_sources = [
                ('hot', subreddit.hot(limit=limit)),
                ('new', subreddit.new(limit=limit//2)),
                ('top', subreddit.top(time_filter='week', limit=limit//2))
            ]
            
            for source_name, source_posts in post_sources:
                try:
                    for post in source_posts:
                        # Skip if already processed
                        if post.url in processed_urls:
                            continue
                        processed_urls.add(post.url)
                        
                        # Skip very old posts (older than 7 days)
                        post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)
                        if post_age > timedelta(days=7):
                            continue
                        
                        # Check if post is about voice AI
                        combined_text = f"{post.title} {getattr(post, 'selftext', '')}"
                        is_relevant, matched_keywords = self._is_voice_ai_related(combined_text)
                        
                        if is_relevant:
                            post_data = {
                                'platform': 'reddit',
                                'type': 'post',
                                'subreddit': subreddit_name,
                                'title': post.title,
                                'content': getattr(post, 'selftext', '')[:500],  # Limit content
                                'url': f"https://reddit.com{post.permalink}",
                                'author': str(post.author) if post.author else '[deleted]',
                                'score': post.score,
                                'created_utc': post.created_utc,
                                'num_comments': post.num_comments,
                                'matched_keywords': matched_keywords,
                                'source_type': source_name,
                                'relevance_score': 0  # Will be calculated later
                            }
                            
                            # Calculate relevance score
                            post_data['relevance_score'] = self._calculate_relevance_score(post_data)
                            
                            posts.append(post_data)
                            logger.info(f"📝 Found: {post.title[:60]}... (score: {post_data['relevance_score']})")
                            
                            # Limit posts per subreddit to avoid overwhelming results
                            if len(posts) >= 15:
                                break
                    
                    if len(posts) >= 15:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing {source_name} posts in r/{subreddit_name}: {str(e)}")
                    continue
            
            logger.info(f"✅ Found {len(posts)} relevant posts in r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error processing r/{subreddit_name}: {str(e)}")
            return []
    
    async def scrape_reddit(self, news_items: Optional[List] = None) -> List[Dict]:
        """
        Main method to scrape Reddit for voice AI content
        
        Args:
            news_items: Optional list of news items (not used, kept for compatibility)
            
        Returns:
            List of relevant Reddit posts about voice AI
        """
        if not self.reddit:
            logger.warning("Reddit not available, returning empty results")
            return []
        
        logger.info(f"🚀 Starting Reddit scraping across {len(TARGET_SUBREDDITS)} subreddits...")
        
        all_posts = []
        
        # Process subreddits in batches to respect rate limits
        batch_size = 3
        for i in range(0, len(TARGET_SUBREDDITS), batch_size):
            batch = TARGET_SUBREDDITS[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for subreddit_name in batch:
                task = asyncio.create_task(
                    asyncio.to_thread(self._process_subreddit, subreddit_name)
                )
                tasks.append(task)
            
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, list):
                        all_posts.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Batch task failed: {result}")
            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
            
            # Rate limiting: pause between batches
            if i + batch_size < len(TARGET_SUBREDDITS):
                await asyncio.sleep(2)
        
        # Sort by relevance score
        all_posts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Limit to top results
        all_posts = all_posts[:30]
        
        logger.info(f"🎯 Reddit scraping completed: {len(all_posts)} total posts found")
        
        # Log top findings
        if all_posts:
            logger.info("🏆 Top Reddit findings:")
            for i, post in enumerate(all_posts[:3]):
                logger.info(f"  {i+1}. r/{post['subreddit']}: {post['title'][:60]}... "
                          f"(score: {post['relevance_score']}, keywords: {len(post['matched_keywords'])})")
        else:
            logger.info("ℹ️  No voice AI content found in recent Reddit posts")
        
        return all_posts

# Create global instance
_reddit_scraper = RedditScraper()

# Main function for compatibility with existing code
async def scrape_reddit(news_items: Optional[List] = None) -> List[Dict]:
    """
    Scrape Reddit for voice AI discussions
    
    Args:
        news_items: Optional list of news items (not used, kept for compatibility)
        
    Returns:
        List of relevant Reddit posts
    """
    return await _reddit_scraper.scrape_reddit(news_items)

# For testing
async def main():
    """Test the Reddit scraper"""
    posts = await scrape_reddit()
    print(f"\n📊 Results: {len(posts)} posts found")
    
    if posts:
        print("\n🎯 Sample posts:")
        for i, post in enumerate(posts[:5]):
            print(f"\n{i+1}. r/{post['subreddit']} ({post['source_type']})")
            print(f"   Title: {post['title']}")
            print(f"   Score: {post['score']} | Comments: {post['num_comments']} | Relevance: {post['relevance_score']}")
            print(f"   Keywords: {', '.join(post['matched_keywords'][:3])}...")
            print(f"   URL: {post['url']}")

if __name__ == "__main__":
    asyncio.run(main())
