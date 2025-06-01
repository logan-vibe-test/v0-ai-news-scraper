"""
Simple email test script
"""
import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_email_simple():
    """Test email with simple configuration"""
    
    # Get email settings
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM')
    email_to = os.getenv('EMAIL_TO')
    
    logger.info(f"SMTP Server: {smtp_server}")
    logger.info(f"SMTP Port: {smtp_port}")
    logger.info(f"Username: {smtp_username}")
    logger.info(f"From: {email_from}")
    logger.info(f"To: {email_to}")
    
    if not all([smtp_server, smtp_username, smtp_password, email_from, email_to]):
        logger.error("Missing email configuration")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['Subject'] = "Test Email from AI Voice News Scraper"
        msg['From'] = email_from
        msg['To'] = email_to
        
        # Add body
        body = """
        <html>
        <body>
        <h1>Test Email</h1>
        <p>This is a test email from the AI Voice News Scraper.</p>
        <p>If you receive this, your email configuration is working!</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        logger.info("Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            logger.info("Starting TLS...")
            server.starttls()
            logger.info("Logging in...")
            server.login(smtp_username, smtp_password)
            logger.info("Sending email...")
            server.send_message(msg)
        
        logger.info("✓ Email sent successfully!")
        return True
    except Exception as e:
        logger.error(f"✗ Email failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_email_simple())
