"""
Super simple test to verify RSS feeds can be fetched
"""
import feedparser
import ssl

# Create unverified SSL context for problematic feeds
ssl._create_default_https_context = ssl._create_unverified_context

def test_rss_feed(url, name):
    print(f"Testing {name} feed: {url}")
    feed = feedparser.parse(url)
    
    if hasattr(feed, 'status') and feed.status == 200:
        print(f"✅ Success! Status: {feed.status}")
    else:
        print(f"❌ Error! No status code available")
    
    if hasattr(feed, 'entries') and feed.entries:
        print(f"✅ Found {len(feed.entries)} entries")
        if len(feed.entries) > 0:
            print(f"First entry title: {feed.entries[0].title}")
    else:
        print(f"❌ No entries found")
    
    print("-" * 50)

if __name__ == "__main__":
    print("Testing basic RSS feed functionality...\n")
    
    # Test a few common RSS feeds
    test_rss_feed("https://news.ycombinator.com/rss", "Hacker News")
    test_rss_feed("https://feeds.arstechnica.com/arstechnica/index", "Ars Technica")
    test_rss_feed("https://www.theverge.com/rss/index.xml", "The Verge")
    test_rss_feed("https://artificialintelligence-news.com/feed/", "AI News")
