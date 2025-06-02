"""
Test script for the consolidated Reddit scraper
"""
import asyncio
import logging
from ai_voice_scraper.scrapers.reddit_scraper import scrape_reddit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_reddit_scraper():
    """Test the Reddit scraper"""
    print("🧪 Testing consolidated Reddit scraper...")
    print("=" * 50)
    
    try:
        posts = await scrape_reddit()
        
        print(f"\n📊 Results: {len(posts)} voice AI posts found")
        
        if posts:
            print("\n🎯 Top 5 posts:")
            for i, post in enumerate(posts[:5]):
                print(f"\n{i+1}. r/{post['subreddit']} - Relevance Score: {post['relevance_score']}")
                print(f"   📝 {post['title']}")
                print(f"   👍 {post['score']} upvotes | 💬 {post['num_comments']} comments")
                print(f"   🏷️  Keywords: {', '.join(post['matched_keywords'][:3])}")
                print(f"   🔗 {post['url']}")
        else:
            print("\n⚠️  No voice AI posts found. This could be normal if:")
            print("   - Reddit API credentials are not configured")
            print("   - There are no recent voice AI discussions")
            print("   - The keywords need adjustment")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check your Reddit API credentials in .env file")

if __name__ == "__main__":
    asyncio.run(test_reddit_scraper())
