"""
Debug script to identify Reddit API issues
"""
import logging
import os
import sys
from dotenv import load_dotenv

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_reddit_credentials():
    """Check if Reddit credentials are properly configured"""
    logger.info("=== Checking Reddit Credentials ===")
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('REDDIT_PASSWORD')
    
    print(f"REDDIT_CLIENT_ID: {'✓ Set' if client_id else '✗ Missing'}")
    print(f"REDDIT_CLIENT_SECRET: {'✓ Set' if client_secret else '✗ Missing'}")
    print(f"REDDIT_USER_AGENT: {user_agent or 'Using default'}")
    print(f"REDDIT_USERNAME: {'✓ Set' if username else '✗ Missing (optional)'}")
    print(f"REDDIT_PASSWORD: {'✓ Set' if password else '✗ Missing (optional)'}")
    
    if not client_id or not client_secret:
        print("\n❌ Missing required Reddit credentials!")
        print("Please add these to your .env file:")
        print("REDDIT_CLIENT_ID=your_client_id_here")
        print("REDDIT_CLIENT_SECRET=your_client_secret_here")
        print("\nTo get these credentials:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'Create App' or 'Create Another App'")
        print("3. Choose 'script' as the app type")
        print("4. Use http://localhost:8080 as redirect URI")
        return False
    
    return True

def test_praw_installation():
    """Test if PRAW is properly installed"""
    logger.info("=== Testing PRAW Installation ===")
    
    try:
        import praw
        print(f"✓ PRAW version: {praw.__version__}")
        return True
    except ImportError as e:
        print(f"❌ PRAW not installed: {e}")
        print("Install with: pip install praw")
        return False
    except Exception as e:
        print(f"❌ PRAW import error: {e}")
        return False

def test_reddit_connection():
    """Test basic Reddit connection"""
    logger.info("=== Testing Reddit Connection ===")
    
    try:
        import praw
        
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')
        username = os.getenv('REDDIT_USERNAME')
        password = os.getenv('REDDIT_PASSWORD')
        
        # Try with username/password if available
        if username and password:
            print("Attempting connection with username/password...")
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=username,
                password=password
            )
        else:
            print("Attempting read-only connection...")
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
        
        # Test the connection by accessing a simple endpoint
        print("Testing connection by accessing r/test...")
        test_subreddit = reddit.subreddit('test')
        
        # Try to get just one post
        posts = list(test_subreddit.hot(limit=1))
        
        if posts:
            post = posts[0]
            print(f"✓ Successfully connected to Reddit!")
            print(f"✓ Test post title: {post.title}")
            print(f"✓ Reddit user: {reddit.user.me() if hasattr(reddit.user, 'me') and reddit.user.me() else 'Read-only mode'}")
            return True
        else:
            print("⚠️ Connected but no posts found in r/test")
            return True
            
    except praw.exceptions.InvalidUserPass:
        print("❌ Invalid username/password")
        print("Try without username/password (read-only mode)")
        return False
    except praw.exceptions.ResponseException as e:
        print(f"❌ Reddit API error: {e}")
        print("Check your client_id and client_secret")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subreddit_access():
    """Test accessing specific subreddits"""
    logger.info("=== Testing Subreddit Access ===")
    
    try:
        import praw
        
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'ai_voice_news_scraper v1.0')
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test subreddits we want to monitor
        test_subreddits = ['MachineLearning', 'artificial', 'OpenAI']
        
        for subreddit_name in test_subreddits:
            try:
                print(f"Testing r/{subreddit_name}...")
                subreddit = reddit.subreddit(subreddit_name)
                
                # Get just one post
                posts = list(subreddit.hot(limit=1))
                
                if posts:
                    post = posts[0]
                    print(f"  ✓ Found post: {post.title[:50]}...")
                else:
                    print(f"  ⚠️ No posts found")
                    
            except Exception as e:
                print(f"  ❌ Error accessing r/{subreddit_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Subreddit test failed: {e}")
        return False

def main():
    """Run all Reddit debugging tests"""
    print("🔍 Reddit API Debugging Tool")
    print("=" * 50)
    
    # Step 1: Check credentials
    if not check_reddit_credentials():
        return
    
    print("\n" + "=" * 50)
    
    # Step 2: Test PRAW installation
    if not test_praw_installation():
        return
    
    print("\n" + "=" * 50)
    
    # Step 3: Test connection
    if not test_reddit_connection():
        return
    
    print("\n" + "=" * 50)
    
    # Step 4: Test subreddit access
    test_subreddit_access()
    
    print("\n" + "=" * 50)
    print("✅ Reddit debugging complete!")
    print("\nIf all tests passed, try running the Reddit scraper again.")
    print("If tests failed, check the error messages above for solutions.")

if __name__ == "__main__":
    main()
