"""
Debug version that shows exactly what's happening
"""
import asyncio
import logging
import praw
import requests
import urllib3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

logger = logging.getLogger(__name__)

def debug_reddit_scraping():
    """Debug Reddit scraping step by step"""
    print("🐛 DEBUG: Reddit Scraping Step by Step")
    print("=" * 60)
    
    # Step 1: Check credentials
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    print(f"1. Credentials: {'✅' if client_id and client_secret else '❌'}")
    
    # Step 2: Initialize Reddit
    try:
        session = requests.Session()
        session.verify = False
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='debug_scraper',
            requestor_kwargs={'session': session}
        )
        print("2. Reddit initialization: ✅")
    except Exception as e:
        print(f"2. Reddit initialization: ❌ {e}")
        return
    
    # Step 3: Test subreddit access
    test_subreddits = ['artificial', 'MachineLearning', 'OpenAI']
    
    for subreddit_name in test_subreddits:
        try:
            print(f"\n3. Testing r/{subreddit_name}:")
            subreddit = reddit.subreddit(subreddit_name)
            
            # Get posts
            posts = list(subreddit.hot(limit=5))
            print(f"   Posts found: {len(posts)}")
            
            if posts:
                for i, post in enumerate(posts[:3]):
                    age_days = (datetime.now() - datetime.fromtimestamp(post.created_utc)).days
                    print(f"   {i+1}. {post.title[:50]}... (Age: {age_days} days)")
                    
                    # Test keyword matching
                    text = f"{post.title} {getattr(post, 'selftext', '')}".lower()
                    
                    # Simple keyword test
                    simple_keywords = ['ai', 'voice', 'speech', 'audio', 'openai', 'gpt']
                    matches = [kw for kw in simple_keywords if kw in text]
                    
                    if matches:
                        print(f"      Keywords: {matches}")
                    else:
                        print(f"      No basic keywords found")
            else:
                print("   ❌ No posts found")
                
        except Exception as e:
            print(f"   ❌ Error accessing r/{subreddit_name}: {e}")
    
    # Step 4: Test with very broad criteria
    print(f"\n4. Testing with ANY AI-related content:")
    try:
        subreddit = reddit.subreddit('artificial')
        posts = list(subreddit.hot(limit=10))
        
        ai_related = []
        for post in posts:
            text = f"{post.title} {getattr(post, 'selftext', '')}".lower()
            if any(word in text for word in ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'model']):
                ai_related.append(post)
        
        print(f"   AI-related posts: {len(ai_related)} out of {len(posts)}")
        
        if ai_related:
            print("   Sample AI-related posts:")
            for i, post in enumerate(ai_related[:3]):
                print(f"   {i+1}. {post.title}")
        
    except Exception as e:
        print(f"   ❌ Error in broad test: {e}")

if __name__ == "__main__":
    debug_reddit_scraping()
