"""
Debug script to test keyword matching on real Reddit posts
"""
import asyncio
import logging
import praw
import requests
import urllib3
from datetime import datetime
import os
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

logger = logging.getLogger(__name__)

def create_reddit_session():
    session = requests.Session()
    session.verify = False
    return session

def test_keyword_matching():
    """Test keyword matching on real Reddit posts"""
    print("🔍 Testing keyword matching on real Reddit posts")
    print("=" * 60)
    
    try:
        session = create_reddit_session()
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='test_keywords',
            requestor_kwargs={'session': session}
        )
        
        # Test with r/artificial (usually has AI content)
        subreddit = reddit.subreddit('artificial')
        posts = list(subreddit.hot(limit=10))
        
        print(f"Analyzing {len(posts)} posts from r/artificial:")
        print("-" * 60)
        
        keywords_to_test = [
            'ai', 'artificial intelligence', 'voice', 'speech', 'audio',
            'openai', 'gpt', 'chatgpt', 'llm', 'model', 'training'
        ]
        
        for i, post in enumerate(posts):
            title = post.title
            content = getattr(post, 'selftext', '')
            combined = f"{title} {content}".lower()
            
            print(f"\n{i+1}. {title}")
            print(f"   Posted: {datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M')}")
            print(f"   Score: {post.score} | Comments: {post.num_comments}")
            
            # Check which keywords match
            matches = [kw for kw in keywords_to_test if kw in combined]
            if matches:
                print(f"   ✅ Keywords found: {', '.join(matches)}")
            else:
                print(f"   ❌ No keywords found")
            
            # Show first 100 chars of content
            if content:
                print(f"   Content: {content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_keyword_matching()
