"""
Test the fixed Reddit scraper that focuses solely on AI voice topics
"""
import asyncio
import logging
from scrapers.reddit_scraper_fixed import scrape_reddit_fixed

logging.basicConfig(level=logging.INFO)

async def test():
    print("🧪 Testing AI Voice Reddit scraper...")
    posts = await scrape_reddit_fixed()
    
    print(f"\n📊 Results: {len(posts)} voice AI posts found")
    
    if posts:
        print("\n🎯 Sample posts:")
        for i, post in enumerate(posts[:5]):
            print(f"\n{i+1}. r/{post['subreddit']} ({post['source_type']})")
            print(f"   Title: {post['title']}")
            print(f"   Score: {post['score']} | Comments: {post['num_comments']}")
            print(f"   Keywords: {', '.join(post['matched_keywords'])}")
            print(f"   URL: {post['url']}")
    else:
        print("\n⚠️ No voice AI posts found (this might be normal)")
        print("   - Check your Reddit API credentials")
        print("   - There might not be recent voice AI discussions")
        print("   - Try expanding the VOICE_KEYWORDS list")

if __name__ == "__main__":
    asyncio.run(test())
