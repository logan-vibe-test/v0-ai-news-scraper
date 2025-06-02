"""
Standalone Reddit scraper test
"""
import asyncio
import logging
import sys
from scrapers.reddit_scraper_improved import scrape_reddit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def test_reddit():
    """Test Reddit scraping standalone"""
    print("🔴 Testing Reddit Scraper...")
    print("=" * 50)
    
    reactions = await scrape_reddit()
    
    print(f"\n📊 Results: {len(reactions)} reactions found")
    
    if reactions:
        print("\n🎯 Top findings:")
        for i, reaction in enumerate(reactions[:5]):
            print(f"\n{i+1}. r/{reaction['subreddit']} ({reaction['type']})")
            print(f"   Score: {reaction.get('relevance_score', 0)}")
            print(f"   Title: {reaction.get('title', 'N/A')}")
            print(f"   Content: {reaction.get('content', '')[:100]}...")
            print(f"   URL: {reaction['url']}")
    else:
        print("\n⚠️ No reactions found. This could mean:")
        print("   - Reddit API credentials not configured")
        print("   - No recent voice AI discussions")
        print("   - Relevance threshold too high")
    
    return len(reactions)

if __name__ == "__main__":
    asyncio.run(test_reddit())
