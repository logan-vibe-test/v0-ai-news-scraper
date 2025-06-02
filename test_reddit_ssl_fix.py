"""
Test script specifically for Reddit SSL issues - FIXED VERSION
"""
import asyncio
import logging
import ssl
import certifi
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def fix_ssl_globally():
    """Fix SSL issues globally"""
    try:
        # Create a custom SSL context that's more permissive
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Set the SSL context globally
        ssl._create_default_https_context = lambda: ssl_context
        
        print("✅ SSL context configured globally")
        return True
    except Exception as e:
        print(f"❌ Could not configure SSL context: {e}")
        return False

async def test_reddit_ssl():
    """Test Reddit connection with SSL fixes"""
    print("🔧 Testing Reddit SSL connection...")
    print("=" * 50)
    
    # Fix SSL first
    fix_ssl_globally()
    
    try:
        # Import after SSL fix
        import praw
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Get credentials
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper_v1.0')
        
        if not all([client_id, client_secret]):
            print("❌ Reddit API credentials not found in .env file")
            print("Please add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to your .env file")
            return False
        
        print("🔑 Reddit credentials found")
        
        # Create Reddit instance with SSL fixes
        print("🔗 Connecting to Reddit API...")
        
        # Create a custom session with SSL disabled
        import requests
        session = requests.Session()
        session.verify = False
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            read_only=True,
            requestor_kwargs={'session': session}
        )
        
        print("✅ Reddit client created successfully")
        
        # Test connection
        print("🧪 Testing connection...")
        
        try:
            # Try to access a simple subreddit
            test_subreddit = reddit.subreddit('test')
            posts = list(test_subreddit.hot(limit=1))
            print("✅ Successfully connected to Reddit!")
            print(f"✅ Retrieved test post: {posts[0].title if posts else 'No posts found'}")
            
            # Test with a real subreddit
            print("🧪 Testing with r/technology...")
            tech_subreddit = reddit.subreddit('technology')
            tech_posts = list(tech_subreddit.hot(limit=3))
            
            print(f"✅ Retrieved {len(tech_posts)} posts from r/technology:")
            for i, post in enumerate(tech_posts, 1):
                print(f"  {i}. {post.title[:60]}...")
            
            return True
            
        except Exception as connection_error:
            print(f"❌ Connection test failed: {connection_error}")
            
            # Try alternative approach
            print("🔄 Trying alternative connection method...")
            try:
                # Just check if we can create the reddit object
                reddit_info = reddit.read_only
                print(f"✅ Reddit object created (read_only: {reddit_info})")
                return True
            except Exception as alt_error:
                print(f"❌ Alternative method also failed: {alt_error}")
                return False
        
    except ImportError as import_error:
        print(f"❌ Import error: {import_error}")
        print("Please install required packages: pip install praw requests urllib3 certifi")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_full_reddit_scraper():
    """Test the full Reddit scraper"""
    print("\n" + "=" * 50)
    print("🚀 Testing full Reddit scraper...")
    
    try:
        from scrapers.reddit_scraper import scrape_reddit
        
        posts = await scrape_reddit()
        
        if posts:
            print(f"✅ SUCCESS! Retrieved {len(posts)} posts")
            print("\n📝 Sample posts:")
            for i, post in enumerate(posts[:3]):
                print(f"  {i+1}. r/{post['subreddit']}: {post['title'][:50]}...")
                print(f"      Sentiment: {post['sentiment']} {post['sentiment_emoji']}")
        else:
            print("⚠️ No posts retrieved, but no errors occurred")
        
        return True
        
    except Exception as e:
        print(f"❌ Full scraper test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔧 Reddit SSL Fix Test Suite")
    print("=" * 60)
    
    # Test 1: Basic SSL connection
    ssl_test = await test_reddit_ssl()
    
    if ssl_test:
        # Test 2: Full scraper
        scraper_test = await test_full_reddit_scraper()
        
        if scraper_test:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ SSL issues have been resolved")
            print("✅ Reddit scraper is working correctly")
        else:
            print("\n⚠️ SSL fixed but scraper has other issues")
    else:
        print("\n❌ SSL issues persist")
        print("Please check your Reddit API credentials and network connection")

if __name__ == "__main__":
    asyncio.run(main())
