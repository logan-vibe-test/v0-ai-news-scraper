"""
Test script for Reddit scraper with sentiment analysis
"""
import asyncio
import logging
from scrapers.reddit_scraper import scrape_reddit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_reddit_sentiment():
    """Test the Reddit scraper with sentiment analysis"""
    print("🧪 Testing Reddit scraper with sentiment analysis...")
    print("=" * 60)
    
    try:
        posts = await scrape_reddit()
        
        print(f"\n📊 Results: {len(posts)} posts collected")
        
        if posts:
            # Calculate sentiment statistics
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            # Group by subreddit for display
            current_subreddit = None
            post_count = 0
            
            for post in posts:
                sentiment_counts[post['sentiment']] += 1
                
                if post['subreddit'] != current_subreddit:
                    current_subreddit = post['subreddit']
                    print(f"\n🔥 r/{current_subreddit}")
                    print("=" * 40)
                
                post_count += 1
                print(f"\n{post_count}. {post['title']}")
                print(f"   👍 {post['score']} upvotes | 💬 {post['num_comments']} comments")
                print(f"   📅 {post['created_date']} | 👤 u/{post['author']}")
                print(f"   🎭 Sentiment: {post['sentiment'].title()} {post['sentiment_emoji']}")
                print(f"   📝 Summary: {post['summary']}")
                print(f"   🔗 Reddit: {post['url']}")
                if post.get('external_url'):
                    print(f"   🌐 External: {post['external_url']}")
            
            # Show overall sentiment analysis
            print(f"\n📈 Overall Sentiment Analysis:")
            print(f"   😊 Positive: {sentiment_counts['positive']} posts ({sentiment_counts['positive']/len(posts)*100:.1f}%)")
            print(f"   😟 Negative: {sentiment_counts['negative']} posts ({sentiment_counts['negative']/len(posts)*100:.1f}%)")
            print(f"   😐 Neutral: {sentiment_counts['neutral']} posts ({sentiment_counts['neutral']/len(posts)*100:.1f}%)")
            
            # Show sentiment by subreddit
            print(f"\n📊 Sentiment by subreddit:")
            subreddit_sentiments = {}
            for post in posts:
                subreddit = post['subreddit']
                if subreddit not in subreddit_sentiments:
                    subreddit_sentiments[subreddit] = {'positive': 0, 'negative': 0, 'neutral': 0}
                subreddit_sentiments[subreddit][post['sentiment']] += 1
            
            for subreddit, sentiments in subreddit_sentiments.items():
                total = sum(sentiments.values())
                print(f"   r/{subreddit}: 😊{sentiments['positive']} 😟{sentiments['negative']} 😐{sentiments['neutral']} (total: {total})")
                
        else:
            print("\n⚠️  No posts found. This could be due to:")
            print("   - Reddit API credentials not configured")
            print("   - Network connectivity issues")
            print("   - All target subreddits are private/restricted")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check your Reddit API credentials and OpenAI API key in .env file")

if __name__ == "__main__":
    asyncio.run(test_reddit_sentiment())
