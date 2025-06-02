"""
Reddit scraper for AI Voice News Scraper
Gets top posts from target subreddits and provides AI summaries
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

class RedditScraper:
    """Reddit scraper that gets top posts and provides summaries"""
    
    def __init__(self):
        self.reddit = None
        self.openai_client = None
        self._initialize_reddit()
        self._initialize_openai()
    
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
                read_only=True
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
    
    def _initialize_openai(self) -> bool:
        """Initialize OpenAI client for summarization"""
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured - summaries will be basic")
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
    
    async def _generate_summary(self, title: str, content: str, url: str) -> str:
        """Generate an AI summary of the Reddit post"""
        if not self.openai_client:
            # Fallback to basic summary if OpenAI not available
            return self._create_basic_summary(title, content)
        
        try:
            # Prepare content for summarization
            post_text = f"Title: {title}\n\nContent: {content[:1000]}"  # Limit content length
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise, informative summaries of Reddit posts. Focus on the key points and main discussion topics. Keep summaries to 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this Reddit post:\n\n{post_text}"
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.warning(f"Error generating AI summary: {str(e)}")
            return self._create_basic_summary(title, content)
    
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
    
    async def _get_top_posts_from_subreddit(self, subreddit_name: str, limit: int = 5) -> List[Dict]:
        """Get top posts from a specific subreddit"""
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            logger.info(f"🔍 Getting top {limit} posts from r/{subreddit_name}...")
            
            # Get hot posts (most active/trending)
            for post in subreddit.hot(limit=limit * 2):  # Get more to filter out stickied posts
                # Skip stickied posts (announcements, rules, etc.)
                if post.stickied:
                    continue
                
                # Skip very old posts (older than 7 days)
                post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)
                if post_age > timedelta(days=7):
                    continue
                
                # Get post content
                content = getattr(post, 'selftext', '') or ''
                
                # If it's a link post, note that
                if not content and post.url != f"https://reddit.com{post.permalink}":
                    content = f"Link post: {post.url}"
                
                post_data = {
                    'platform': 'reddit',
                    'type': 'post',
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'content': content[:500],  # Limit content length
                    'full_content': content,  # Keep full content for summarization
                    'url': f"https://reddit.com{post.permalink}",
                    'external_url': post.url if post.url != f"https://reddit.com{post.permalink}" else None,
                    'author': str(post.author) if post.author else '[deleted]',
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments,
                    'created_date': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M'),
                    'summary': ''  # Will be filled by AI
                }
                
                # Generate summary
                post_data['summary'] = await self._generate_summary(
                    post_data['title'], 
                    post_data['full_content'], 
                    post_data['url']
                )
                
                posts.append(post_data)
                logger.info(f"📝 Added: {post.title[:60]}... (score: {post.score})")
                
                # Stop when we have enough posts
                if len(posts) >= limit:
                    break
            
            logger.info(f"✅ Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error getting posts from r/{subreddit_name}: {str(e)}")
            return []
    
    async def scrape_reddit(self, news_items: Optional[List] = None) -> List[Dict]:
        """
        Get top 5 posts from each target subreddit with AI summaries
        
        Args:
            news_items: Optional list of news items (not used, kept for compatibility)
            
        Returns:
            List of top Reddit posts with summaries
        """
        if not self.reddit:
            logger.warning("Reddit not available, returning empty results")
            return []
        
        logger.info(f"🚀 Getting top 5 posts from {len(TARGET_SUBREDDITS)} subreddits...")
        
        all_posts = []
        
        # Process subreddits in batches to respect rate limits
        batch_size = 3
        for i in range(0, len(TARGET_SUBREDDITS), batch_size):
            batch = TARGET_SUBREDDITS[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for subreddit_name in batch:
                task = asyncio.create_task(
                    self._get_top_posts_from_subreddit(subreddit_name, limit=5)
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
        
        # Log summary by subreddit
        if organized_posts:
            logger.info("📊 Posts collected by subreddit:")
            for subreddit in TARGET_SUBREDDITS:
                count = len([p for p in organized_posts if p['subreddit'] == subreddit])
                if count > 0:
                    logger.info(f"  r/{subreddit}: {count} posts")
        
        return organized_posts

# Create global instance
_reddit_scraper = RedditScraper()

# Main function for compatibility with existing code
async def scrape_reddit(news_items: Optional[List] = None) -> List[Dict]:
    """
    Scrape Reddit for top posts with summaries
    
    Args:
        news_items: Optional list of news items (not used, kept for compatibility)
        
    Returns:
        List of top Reddit posts with AI-generated summaries
    """
    return await _reddit_scraper.scrape_reddit(news_items)

# For testing
async def main():
    """Test the Reddit scraper"""
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
            print(f"   📝 Summary: {post['summary']}")
            print(f"   🔗 Reddit: {post['url']}")
            if post.get('external_url'):
                print(f"   🌐 External: {post['external_url']}")

if __name__ == "__main__":
    asyncio.run(main())
