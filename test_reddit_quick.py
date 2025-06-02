"""
Quick Reddit test
"""
import asyncio
import logging
from scrapers.reddit_scraper_simple import scrape_reddit_simple

logging.basicConfig(level=logging.INFO)

async def test():
    print("🔴 Testing Reddit scraper...")
    posts = await scrape_reddit_simple()
    
    print(f"\n📊 Found {len(posts)} voice AI posts")
    
    for i, post in enumerate(posts[:5]):
        print(f"\n{i+1}. r/{post['subreddit']}")
        print(f"   Title: {post['title']}")
        print(f"   Score: {post['score']}")
        print(f"   URL: {post['url']}")

if __name__ == "__main__":
    asyncio.run(test())
