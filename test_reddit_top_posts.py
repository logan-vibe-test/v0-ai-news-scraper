"""
Test script for the updated Reddit scraper that gets top posts with summaries
"""
import asyncio
import logging
from scrapers.reddit_scraper import scrape_reddit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_reddit_top_posts():
    """Test the Reddit scraper for top posts with summaries"""
    print("🧪 Testing Reddit scraper for top posts with AI summaries...")
    print("=" * 60)
    
    try:
        posts = await scrape_reddit()
        
        print(f"\n📊 Results: {len(posts)} posts collected")
        
        if posts:
            # Group by subreddit for display
            current_subreddit = None
            post_count = 0
            
            for post in posts:
                if post['subreddit'] != current_subreddit:
                    current_subreddit = post['subreddit']
                    print(f"\n🔥 r/{current_subreddit}")
                    print("=" * 40)
                
                post_count += 1
                print(f"\n{post_count}. {post['title']}")
                print(f"   👍 {post['score']} upvotes | 💬 {post['num_comments']} comments")
                print(f"   📅 {post['created_date']} | 👤 u/{post['author']}")
                print(f"   📝 Summary: {post['summary']}")
                print(f"   🔗 Reddit: {post['url']}")
                if post.get('external_url'):
                    print(f"   🌐 External: {post['external_url']}")
        else:
            print("\n⚠️  No posts found. This could be due to:")
            print("   - Reddit API credentials not configured")
            print("   - Network connectivity issues")
            print("   - All target subreddits are private/restricted")
        
        print(f"\n✅ Test completed successfully!")
        
        # Show summary by subreddit
        if posts:
            print(f"\n📈 Summary by subreddit:")
            subreddit_counts = {}
            for post in posts:
                subreddit = post['subreddit']
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            for subreddit, count in subreddit_counts.items():
                print(f"   r/{subreddit}: {count} posts")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check your Reddit API credentials and OpenAI API key in .env file")

if __name__ == "__main__":
    asyncio.run(test_reddit_top_posts())
