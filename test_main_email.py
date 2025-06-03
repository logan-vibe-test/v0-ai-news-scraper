"""
Test script to verify the main script email functionality
"""
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_main_email_function():
    """Test the main script's email functionality"""
    
    # Force reload environment
    load_dotenv(override=True)
    
    print("🧪 Testing main script email functionality...")
    
    try:
        # Import the email function from the main script's path
        from notifiers.email_notifier import send_email_digest, get_all_recipients
        
        # Test recipient parsing first
        print("\n📧 Testing recipient parsing...")
        to_emails, cc_emails, bcc_emails, all_recipients = get_all_recipients()
        
        print(f"Found {len(all_recipients)} total recipients:")
        for i, email in enumerate(all_recipients, 1):
            print(f"  {i}. {email}")
        
        if len(all_recipients) < 3:
            print(f"⚠️ Warning: Expected 3+ recipients, found {len(all_recipients)}")
            return False
        
        # Create test digest
        test_digest = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'news_items': [{
                'title': 'Test Voice AI News - Main Script Test',
                'url': 'https://example.com/test-main',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'summary': 'This is a test from the main script email function to verify all recipients receive the email.'
            }],
            'reactions': [{
                'platform': 'reddit',
                'subreddit': 'test',
                'title': 'Test Reddit Discussion - Main Script',
                'content': 'Test content from main script',
                'url': 'https://reddit.com/test-main',
                'sentiment': 'positive',
                'sentiment_emoji': '😊',
                'summary': 'Test Reddit discussion from main script',
                'score': 100,
                'num_comments': 10,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }],
            'total_reddit_scanned': 50
        }
        
        print(f"\n📧 Sending test email via main script function...")
        result = await send_email_digest(test_digest)
        
        if result:
            print("✅ Main script email function works!")
            print(f"📧 Email sent to all {len(all_recipients)} recipients")
            print("Check all inboxes to verify delivery.")
            return True
        else:
            print("❌ Main script email function failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing main script email: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_main_email_function())
