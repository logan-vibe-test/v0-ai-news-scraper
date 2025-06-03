"""
Test script to diagnose Gmail CC delivery issues
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import time

load_dotenv(override=True)

def test_gmail_cc_delivery():
    """Test different email delivery strategies with Gmail"""
    
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    
    to_emails = ['youngberglogan@gmail.com', 'lwyoungberg@gmail.com']
    cc_emails = ['logan.youngberg@workday.com']
    all_recipients = to_emails + cc_emails
    
    print("🧪 Testing Gmail CC Delivery Issues")
    print("=" * 50)
    print(f"TO emails: {to_emails}")
    print(f"CC emails: {cc_emails}")
    print(f"All recipients: {all_recipients}")
    
    # Test 1: Send with proper TO/CC headers
    print("\n📧 Test 1: Proper TO/CC structure")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            msg = MIMEMultipart()
            msg['Subject'] = "Test 1: TO/CC Structure"
            msg['From'] = EMAIL_FROM
            msg['To'] = ', '.join(to_emails)
            msg['Cc'] = ', '.join(cc_emails)
            
            body = """
            <html><body>
            <h2>Test 1: TO/CC Structure</h2>
            <p>This email uses proper TO/CC headers.</p>
            <p>TO: youngberglogan@gmail.com, lwyoungberg@gmail.com</p>
            <p>CC: logan.youngberg@workday.com</p>
            </body></html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            result = server.sendmail(EMAIL_FROM, all_recipients, msg.as_string())
            print(f"  Result: {result if result else 'Success'}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)
    
    # Test 2: Send to all recipients as TO (no CC)
    print("\n📧 Test 2: All recipients as TO")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            msg = MIMEMultipart()
            msg['Subject'] = "Test 2: All as TO Recipients"
            msg['From'] = EMAIL_FROM
            msg['To'] = ', '.join(all_recipients)  # All as TO
            
            body = """
            <html><body>
            <h2>Test 2: All as TO Recipients</h2>
            <p>This email sends to all 3 addresses as TO recipients.</p>
            <p>All recipients: youngberglogan@gmail.com, lwyoungberg@gmail.com, logan.youngberg@workday.com</p>
            </body></html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            result = server.sendmail(EMAIL_FROM, all_recipients, msg.as_string())
            print(f"  Result: {result if result else 'Success'}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)
    
    # Test 3: Send individually to each recipient
    print("\n📧 Test 3: Individual sends")
    for i, email in enumerate(all_recipients, 1):
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                
                msg = MIMEMultipart()
                msg['Subject'] = f"Test 3: Individual Send {i}/3"
                msg['From'] = EMAIL_FROM
                msg['To'] = email
                
                body = f"""
                <html><body>
                <h2>Test 3: Individual Send {i}/3</h2>
                <p>This email was sent individually to: <strong>{email}</strong></p>
                <p>If you receive this, individual sending works for your email.</p>
                </body></html>
                """
                msg.attach(MIMEText(body, 'html'))
                
                result = server.sendmail(EMAIL_FROM, [email], msg.as_string())
                print(f"  {i}. {email}: {result if result else 'Success'}")
                
        except Exception as e:
            print(f"  {i}. {email}: Error - {e}")
        
        time.sleep(1)
    
    print("\n✅ All tests completed!")
    print("Check all 3 inboxes to see which method works best.")
    print("\nExpected results:")
    print("- Test 1: Might only deliver to TO recipients (Gmail CC issue)")
    print("- Test 2: Should deliver to all 3 recipients")
    print("- Test 3: Should definitely deliver to all 3 recipients")

if __name__ == "__main__":
    test_gmail_cc_delivery()
