"""
Test script for trends analysis functionality
"""
import asyncio
import logging
from datetime import datetime
from processors.trends_analyzer import analyze_current_trends
from storage.db_manager import store_run_summary

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_trends_analysis():
    """Test the trends analysis functionality"""
    print("🧪 Testing trends analysis...")
    print("=" * 60)
    
    # Create some sample run data to simulate historical runs
    sample_runs = [
        {
            'articles_found': 15,
            'articles_processed': 8,
            'reddit_posts': 12,
            'sentiment_summary': {'positive': 5, 'negative': 2, 'neutral': 5},
            'subreddit_activity': {'MachineLearning': 3, 'technology': 2, 'OpenAI': 4, 'artificial': 3}
        },
        {
            'articles_found': 18,
            'articles_processed': 10,
            'reddit_posts': 14,
            'sentiment_summary': {'positive': 8, 'negative': 3, 'neutral': 3},
            'subreddit_activity': {'MachineLearning': 4, 'technology': 3, 'OpenAI': 3, 'artificial': 4}
        },
        {
            'articles_found': 12,
            'articles_processed': 6,
            'reddit_posts': 10,
            'sentiment_summary': {'positive': 6, 'negative': 1, 'neutral': 3},
            'subreddit_activity': {'MachineLearning': 2, 'technology': 2, 'OpenAI': 3, 'artificial': 3}
        }
    ]
    
    # Store sample historical runs
    print("📊 Creating sample historical data...")
    for i, run_data in enumerate(sample_runs):
        await store_run_summary(run_data)
        print(f"   Stored sample run {i+1}")
    
    # Test current run analysis
    current_run = {
        'articles_found': 20,
        'articles_processed': 12,
        'reddit_posts': 16,
        'sentiment_summary': {'positive': 10, 'negative': 2, 'neutral': 4},
        'subreddit_activity': {'MachineLearning': 5, 'technology': 3, 'OpenAI': 4, 'artificial': 4}
    }
    
    print("\n🔍 Analyzing trends for current run...")
    trends = await analyze_current_trends(current_run)
    
    if trends.get('available'):
        print("✅ Trends analysis successful!")
        print(f"\n📈 Trends Summary: {trends['summary']}")
        print(f"📅 Date Range: {trends['date_range']}")
        print(f"🔢 Runs Analyzed: {trends['runs_analyzed']}")
        
        print(f"\n🎭 Sentiment Trends:")
        sentiment = trends['sentiment']
        print(f"   Direction: {sentiment['emoji']} {sentiment['trend'].title()}")
        print(f"   Current Score: {sentiment['current_score']:.2f}")
        print(f"   Change: {sentiment['change']:+.2f}")
        
        print(f"\n💬 Activity Trends:")
        activity = trends['activity']
        print(f"   Direction: {activity['emoji']} {activity['trend'].title()}")
        print(f"   Current Posts: {activity['current_posts']}")
        print(f"   Change: {activity['change']:+d}")
        
        print(f"\n📰 News Volume Trends:")
        news = trends['news_volume']
        print(f"   Direction: {news['emoji']} {news['trend'].title()}")
        print(f"   Current Articles: {news['current_articles']}")
        print(f"   Change: {news['change']:+d}")
        
        if trends.get('insights'):
            print(f"\n💡 Key Insights:")
            for insight in trends['insights']:
                print(f"   • {insight}")
        
        if trends.get('subreddit_trends'):
            print(f"\n🏆 Top Subreddit Trends:")
            for subreddit, data in list(trends['subreddit_trends'].items())[:3]:
                print(f"   r/{subreddit}: {data['emoji']} {data['trend']} (avg: {data['avg_posts']:.1f} posts)")
        
        print(f"\n🎉 Trends analysis completed successfully!")
        
    else:
        print("❌ Trends analysis failed:")
        print(f"   Error: {trends.get('message', 'Unknown error')}")
    
    return trends.get('available', False)

async def test_email_with_trends():
    """Test email generation with trends"""
    print("\n" + "=" * 60)
    print("📧 Testing email digest with trends...")
    
    try:
        from notifiers.email_notifier import send_email_digest
        
        # Sample digest data
        sample_digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': [
                {
                    'title': 'ElevenLabs Launches New Voice API',
                    'url': 'https://example.com/elevenlabs',
                    'source': 'TechCrunch',
                    'published_date': '2024-01-15T10:00:00',
                    'summary': 'ElevenLabs announced a breakthrough in voice cloning technology.'
                }
            ],
            'reactions': [
                {
                    'platform': 'reddit',
                    'subreddit': 'MachineLearning',
                    'title': 'ElevenLabs new API is incredible',
                    'url': 'https://reddit.com/r/MachineLearning/test',
                    'score': 156,
                    'num_comments': 23,
                    'sentiment': 'positive',
                    'sentiment_emoji': '😊',
                    'summary': 'Community is excited about the new voice cloning capabilities.',
                    'created_date': '2024-01-15 10:30'
                }
            ]
        }
        
        # This will automatically include trends analysis
        result = await send_email_digest(sample_digest)
        
        if result:
            print("✅ Email with trends sent successfully!")
            print("Check your email for the new trends section")
        else:
            print("❌ Email sending failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔬 Trends Analysis Test Suite")
    print("=" * 60)
    
    # Test 1: Basic trends analysis
    trends_test = await test_trends_analysis()
    
    if trends_test:
        # Test 2: Email with trends
        email_test = await test_email_with_trends()
        
        if email_test:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Trends analysis is working correctly")
            print("✅ Email digest includes trends section")
        else:
            print("\n⚠️ Trends work but email has issues")
    else:
        print("\n❌ Trends analysis has issues")

if __name__ == "__main__":
    asyncio.run(main())
