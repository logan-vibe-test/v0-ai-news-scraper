"""
Debug script to test email sending step by step
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def test_basic_email_sending():
    """Test basic email sending with detailed debugging"""
    
    # Get configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    
    print("🔧 Email Configuration:")
    print(f"SMTP_SERVER: {SMTP_SERVER}")
    print(f"SMTP_PORT: {SMTP_PORT}")
    print(f"EMAIL_FROM: {EMAIL_FROM}")
    print(f"EMAIL_TO: '{EMAIL_TO}'")
    
    # Parse emails manually
    if not EMAIL_TO:
        print("❌ No EMAIL_TO configured")
        return
    
    # Split and clean emails
    emails = []
    for email in EMAIL_TO.split(','):
        email = email.strip()
        if email and '@' in email:
            emails.append(email)
    
    print(f"\n📧 Parsed {len(emails)} email addresses:")
    for i, email in enumerate(emails, 1):
        print(f"  {i}. {email}")
    
    if len(emails) < 3:
        print(f"⚠️  Warning: Only {len(emails)} emails found, expected 3+")
    
    # Test each email individually first
    print(f"\n🧪 Testing individual email sends...")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            for i, email in enumerate(emails, 1):
                try:
                    msg = MIMEMultipart()
                    msg['Subject'] = f"Test Email {i}/3 - Individual Send"
                    msg['From'] = EMAIL_FROM
                    msg['To'] = email
                    
                    body = f"""
                    <html>
                    <body>
                    <h2>Test Email {i} of {len(emails)}</h2>
                    <p>This is test email #{i} sent individually to: <strong>{email}</strong></p>
                    <p>If you receive this, individual sending works for your email.</p>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(body, 'html'))
                    
                    # Send to single recipient
                    server.sendmail(EMAIL_FROM, [email], msg.as_string())
                    print(f"  ✅ Sent individual email to: {email}")
                    
                except Exception as e:
                    print(f"  ❌ Failed to send to {email}: {e}")
        
        print(f"\n✅ Individual email test completed")
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return
    
    # Now test bulk sending
    print(f"\n🧪 Testing bulk email send to all {len(emails)} recipients...")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            msg = MIMEMultipart()
            msg['Subject'] = "Test Email - Bulk Send to All Recipients"
            msg['From'] = EMAIL_FROM
            msg['To'] = ', '.join(emails)  # Show all in TO field
            
            body = f"""
            <html>
            <body>
            <h2>Bulk Email Test</h2>
            <p>This email was sent to <strong>{len(emails)} recipients</strong> in a single send:</p>
            <ul>
            """
            
            for email in emails:
                body += f"<li>{email}</li>"
            
            body += """
            </ul>
            <p>If you receive this, bulk sending is working.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send to all recipients at once
            result = server.sendmail(EMAIL_FROM, emails, msg.as_string())
            
            if result:
                print(f"⚠️  Some emails failed: {result}")
            else:
                print(f"✅ Bulk email sent successfully to all {len(emails)} recipients")
                
    except Exception as e:
        print(f"❌ Bulk email failed: {e}")

if __name__ == "__main__":
    test_basic_email_sending()
