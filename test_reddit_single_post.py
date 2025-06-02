"""
Test script to verify we get exactly 1 post per subreddit
"""
import asyncio
import logging
from scrapers.reddit_scraper import scrape_reddit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_single_post_per_subreddit():
    """Test that we get exactly 1 post per subreddit"""
    print("🧪 Testing Reddit scraper for 1 post per subreddit...")
    print("=" * 60)
    
    try:
        posts = await scrape_reddit()
        
        print(f"\n📊 Results: {len(posts)} posts collected")
        
        if posts:
            # Count posts per subreddit
            subreddit_counts = {}
            for post in posts:
                subreddit = post['subreddit']
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            print(f"\n📈 Posts per subreddit:")
            all_single = True
            for subreddit, count in subreddit_counts.items():
                status = "✅" if count == 1 else "❌"
                print(f"   {status} r/{subreddit}: {count} post(s)")
                if count != 1:
                    all_single = False
            
            if all_single:
                print(f"\n🎉 SUCCESS! Exactly 1 post per subreddit as expected")
            else:
                print(f"\n⚠️ Some subreddits have more than 1 post")
            
            print(f"\n🔥 Top posts by subreddit:")
            for post in posts:
                print(f"\nr/{post['subreddit']}:")
                print(f"   📝 {post['title']}")
                print(f"   👍 {post['score']} upvotes | 💬 {post['num_comments']} comments")
                print(f"   🎭 Sentiment: {post['sentiment'].title()} {post['sentiment_emoji']}")
                print(f"   📄 Summary: {post['summary']}")
                print(f"   🔗 {post['url']}")
                
        else:
            print("\n⚠️ No posts found. This could be due to:")
            print("   - Reddit API credentials not configured")
            print("   - Network connectivity issues")
            print("   - All target subreddits are private/restricted")
        
        print(f"\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check your Reddit API credentials and network connection")

if __name__ == "__main__":
    asyncio.run(test_single_post_per_subreddit())
