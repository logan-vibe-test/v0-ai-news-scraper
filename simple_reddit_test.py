"""
Very simple Reddit test to isolate the issue
"""
import os
from dotenv import load_dotenv

load_dotenv()

def simple_reddit_test():
    """Minimal Reddit test"""
    print("Testing Reddit with minimal setup...")
    
    try:
        import praw
        print("✓ PRAW imported successfully")
    except ImportError:
        print("❌ PRAW not installed. Run: pip install praw")
        return
    
    # Get credentials
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET")
        print("Add these to your .env file:")
        print("REDDIT_CLIENT_ID=your_id_here")
        print("REDDIT_CLIENT_SECRET=your_secret_here")
        return
    
    try:
        # Create Reddit instance
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="test_script_v1.0"
        )
        
        print("✓ Reddit instance created")
        
        # Test with a simple subreddit
        subreddit = reddit.subreddit('python')  # Use a popular, stable subreddit
        print("✓ Subreddit object created")
        
        # Get one post
        for post in subreddit.hot(limit=1):
            print(f"✓ Successfully got post: {post.title}")
            break
        
        print("🎉 Reddit is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Common error solutions
        if "401" in str(e) or "Unauthorized" in str(e):
            print("\n💡 Solution: Check your client_id and client_secret")
            print("Make sure they're correct in your .env file")
        elif "403" in str(e) or "Forbidden" in str(e):
            print("\n💡 Solution: Your app might be suspended or rate limited")
            print("Try creating a new Reddit app")
        elif "429" in str(e) or "rate" in str(e).lower():
            print("\n💡 Solution: Rate limited. Wait a few minutes and try again")
        else:
            print("\n💡 Try creating a new Reddit app at https://www.reddit.com/prefs/apps")

if __name__ == "__main__":
    simple_reddit_test()
