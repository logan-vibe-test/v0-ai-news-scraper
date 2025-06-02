"""
Test the fixed Reddit scraper
"""
import asyncio
import logging
from scrapers.reddit_scraper_fixed import scrape_reddit_fixed

logging.basicConfig(level=logging.INFO)

async def test():
    print("🧪 Testing fixed Reddit scraper...")
    posts = await scrape_reddit_fixed()
    
    print(f"\n📊 Results: {len(posts)} voice AI posts found")
    
    if posts:
        print("\n🎯 Sample posts:")
        for i, post in enumerate(posts[:3]):
            print(f"\n{i+1}. r/{post['subreddit']}")
            print(f"   Title: {post['title']}")
            print(f"   Score: {post['score']}")
            print(f"   URL: {post['url']}")
    else:
        print("\n⚠️ No voice AI posts found (this might be normal)")
        print("   - Check your Reddit API credentials")
        print("   - There might not be recent voice AI discussions")

if __name__ == "__main__":
    asyncio.run(test())
