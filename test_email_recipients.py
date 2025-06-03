"""
Test script to verify multiple email recipients work correctly
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_parsing():
    """Test email parsing function"""
    from notifiers.email_notifier import parse_email_list
    
    # Test cases
    test_cases = [
        "email1@gmail.com,email2@company.com,email3@example.com",
        "email1@gmail.com, email2@company.com, email3@example.com",  # with spaces
        "email1@gmail.com,email2@company.com,email3@example.com,",  # trailing comma
        "email1@gmail.com",  # single email
        "",  # empty string
        "invalid-email,valid@email.com,another-invalid",  # mixed valid/invalid
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: '{test_case}'")
        result = parse_email_list(test_case)
        print(f"Result: {result}")
        print(f"Count: {len(result)}")

async def test_email_sending():
    """Test sending email to multiple recipients"""
    from notifiers.email_notifier import send_email_digest
    from datetime import datetime
    
    # Check environment variables
    email_to = os.getenv('EMAIL_TO', '')
    email_cc = os.getenv('EMAIL_CC', '')
    email_bcc = os.getenv('EMAIL_BCC', '')
    
    print(f"EMAIL_TO: '{email_to}'")
    print(f"EMAIL_CC: '{email_cc}'")
    print(f"EMAIL_BCC: '{email_bcc}'")
    
    if not email_to:
        print("❌ No EMAIL_TO configured in .env file")
        return
    
    # Create test digest
    test_digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': [{
            'title': 'Test Voice AI News Article',
            'url': 'https://example.com/test',
            'source': 'Test Source',
            'published_date': datetime.now().isoformat(),
            'summary': 'This is a test article to verify multiple email recipients are working correctly.'
        }],
        'reactions': [{
            'platform': 'reddit',
            'subreddit': 'test',
            'title': 'Test Reddit Discussion',
            'content': 'Test content',
            'url': 'https://reddit.com/test',
            'sentiment': 'positive',
            'sentiment_emoji': '😊',
            'summary': 'Test Reddit discussion for email testing',
            'score': 100,
            'num_comments': 10,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }],
        'total_reddit_scanned': 50
    }
    
    print("\n🧪 Sending test email...")
    result = await send_email_digest(test_digest)
    
    if result:
        print("✅ Test email sent successfully!")
        print("Check all recipient inboxes to verify delivery.")
    else:
        print("❌ Test email failed to send.")

async def main():
    """Main test function"""
    print("🧪 Testing Email Recipients Configuration")
    print("=" * 50)
    
    print("\n1. Testing email parsing...")
    test_email_parsing()
    
    print("\n2. Testing actual email sending...")
    await test_email_sending()

if __name__ == "__main__":
    asyncio.run(main())
