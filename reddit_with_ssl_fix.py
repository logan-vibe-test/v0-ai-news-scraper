"""
Reddit scraper with SSL certificate fix
"""
import ssl
import certifi
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_ssl_context():
    """Create SSL context with proper certificates"""
    try:
        # Create SSL context with certificates
        context = ssl.create_default_context(cafile=certifi.where())
        return context
    except Exception as e:
        print(f"Warning: Could not create SSL context: {e}")
        return None

def test_reddit_with_ssl_fix():
    """Test Reddit with SSL fix"""
    print("🔧 Testing Reddit with SSL fix...")
    
    try:
        import praw
        import prawcore
        import requests
        
        # Configure requests to use proper certificates
        session = requests.Session()
        session.verify = certifi.where()
        
        # Create Reddit instance with custom session
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="ai_voice_news_scraper_v1.0",
            requestor_kwargs={'session': session}
        )
        
        print("✓ Reddit instance created with SSL fix")
        
        # Test connection
        subreddit = reddit.subreddit('python')
        print("✓ Subreddit object created")
        
        # Get one post
        for post in subreddit.hot(limit=1):
            print(f"✅ Successfully got post: {post.title}")
            return True
            
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False

def test_alternative_method():
    """Test with SSL verification disabled (not recommended for production)"""
    print("\n🔧 Testing with SSL verification disabled (temporary fix)...")
    
    try:
        import praw
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        import urllib3
        
        # Disable SSL warnings (not recommended for production)
        urllib3.disable_warnings(InsecureRequestWarning)
        
        # Create session with SSL verification disabled
        session = requests.Session()
        session.verify = False
        
        # Create Reddit instance
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="ai_voice_news_scraper_v1.0",
            requestor_kwargs={'session': session}
        )
        
        print("✓ Reddit instance created (SSL disabled)")
        
        # Test connection
        subreddit = reddit.subreddit('python')
        for post in subreddit.hot(limit=1):
            print(f"✅ Successfully got post: {post.title}")
            print("\n⚠️ WARNING: This method disables SSL verification")
            print("   Only use this temporarily while fixing SSL certificates")
            return True
            
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False

if __name__ == "__main__":
    # Try SSL fix first
    if not test_reddit_with_ssl_fix():
        # If that fails, try alternative method
        test_alternative_method()
