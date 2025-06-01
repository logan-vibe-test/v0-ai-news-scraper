"""
Guide for creating a Reddit app
"""

def print_reddit_setup_guide():
    """Print step-by-step guide for setting up Reddit API"""
    
    print("🔧 Reddit API Setup Guide")
    print("=" * 50)
    
    print("\n1. Go to Reddit Apps page:")
    print("   https://www.reddit.com/prefs/apps")
    
    print("\n2. Click 'Create App' or 'Create Another App'")
    
    print("\n3. Fill in the form:")
    print("   Name: AI Voice News Scraper")
    print("   App type: Select 'script'")
    print("   Description: Scrapes Reddit for AI voice discussions")
    print("   About URL: (leave blank)")
    print("   Redirect URI: http://localhost:8080")
    
    print("\n4. Click 'Create app'")
    
    print("\n5. After creation, you'll see:")
    print("   - App name at the top")
    print("   - Client ID: (string under the app name)")
    print("   - Client Secret: (longer string labeled 'secret')")
    
    print("\n6. Add to your .env file:")
    print("   REDDIT_CLIENT_ID=your_client_id_here")
    print("   REDDIT_CLIENT_SECRET=your_client_secret_here")
    print("   REDDIT_USER_AGENT=ai_voice_news_scraper_v1.0_by_yourusername")
    
    print("\n7. Optional (for better rate limits):")
    print("   REDDIT_USERNAME=your_reddit_username")
    print("   REDDIT_PASSWORD=your_reddit_password")
    
    print("\n8. Test with:")
    print("   python simple_reddit_test.py")
    
    print("\n" + "=" * 50)
    print("📝 Common Issues:")
    print("- Make sure to select 'script' not 'web app'")
    print("- Client ID is the short string under the app name")
    print("- Client Secret is the longer string labeled 'secret'")
    print("- Don't include quotes in your .env file")
    print("- Make sure there are no spaces around the = sign")

if __name__ == "__main__":
    print_reddit_setup_guide()
