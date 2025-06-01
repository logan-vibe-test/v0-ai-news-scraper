"""
Simple email test to verify configuration
"""
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_config():
    """Test email configuration with a simple message"""
    
    # Check if email is configured
    required_vars = ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_TO']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing email configuration: {missing_vars}")
        logger.info("Please set these in your .env file:")
        for var in missing_vars:
            logger.info(f"  {var}=your_value_here")
        return False
    
    # Test with a simple digest
    test_digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': [
            {
                'title': 'Test: OpenAI Releases New Voice Model',
                'url': 'https://example.com/test-article',
                'source': 'Test Source',
                'published_date': datetime.now().isoformat(),
                'summary': 'This is a test article to verify that your email configuration is working correctly. If you receive this email, your AI Voice News Scraper is properly configured!'
            }
        ],
        'reactions': []
    }
    
    try:
        from notifiers.email_notifier import send_email_digest
        result = await send_email_digest(test_digest)
        
        if result:
            logger.info("✅ Test email sent successfully!")
            logger.info("Check your inbox (and spam folder) for the test email.")
            return True
        else:
            logger.error("❌ Test email failed to send")
            return False
    except Exception as e:
        logger.error(f"❌ Email test error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_email_config())
