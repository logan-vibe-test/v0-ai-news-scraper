"""
Debug script with forced fresh environment loading
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

def test_with_fresh_env():
    """Test email with completely fresh environment loading"""
    
    # Clear any cached environment variables
    env_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 
                'EMAIL_FROM', 'EMAIL_TO', 'EMAIL_CC', 'EMAIL_BCC']
    
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    
    # Force reload with override
    print("🔄 Force reloading .env file...")
    load_dotenv(override=True, verbose=True)
    
    # Get fresh values
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    EMAIL_CC = os.getenv('EMAIL_CC', '')
    EMAIL_BCC = os.getenv('EMAIL_BCC', '')
    
    print("🔧 Fresh Email Configuration:")
    print(f"SMTP_SERVER: {SMTP_SERVER}")
    print(f"SMTP_PORT: {SMTP_PORT}")
    print(f"EMAIL_FROM: {EMAIL_FROM}")
    print(f"EMAIL_TO: '{EMAIL_TO}'")
    print(f"EMAIL_CC: '{EMAIL_CC}'")
    print(f"EMAIL_BCC: '{EMAIL_BCC}'")
    
    # Parse ALL email addresses
    all_emails = []
    
    # Parse TO emails
    if EMAIL_TO:
        for email in EMAIL_TO.split(','):
            email = email.strip()
            if email and '@' in email:
                all_emails.append(('TO', email))
    
    # Parse CC emails
    if EMAIL_CC:
        for email in EMAIL_CC.split(','):
            email = email.strip()
            if email and '@' in email:
                all_emails.append(('CC', email))
    
    # Parse BCC emails
    if EMAIL_BCC:
        for email in EMAIL_BCC.split(','):
            email = email.strip()
            if email and '@' in email:
                all_emails.append(('BCC', email))
    
    print(f"\n📧 Found {len(all_emails)} total email addresses:")
    for i, (type_label, email) in enumerate(all_emails, 1):
        print(f"  {i}. {email} ({type_label})")
    
    if len(all_emails) < 3:
        print(f"⚠️  Warning: Only {len(all_emails)} emails found, expected 3+")
        return
    
    # Test sending to all emails
    print(f"\n🧪 Testing email send to all {len(all_emails)} recipients...")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Prepare recipient lists
            to_list = [email for type_label, email in all_emails if type_label == 'TO']
            cc_list = [email for type_label, email in all_emails if type_label == 'CC']
            bcc_list = [email for type_label, email in all_emails if type_label == 'BCC']
            all_recipients = [email for _, email in all_emails]
            
            print(f"TO: {to_list}")
            print(f"CC: {cc_list}")
            print(f"BCC: {bcc_list}")
            print(f"All recipients: {all_recipients}")
            
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = "Test Email - Fresh Environment Variables"
            msg['From'] = EMAIL_FROM
            
            if to_list:
                msg['To'] = ', '.join(to_list)
            if cc_list:
                msg['Cc'] = ', '.join(cc_list)
            # BCC is not added to headers
            
            body = f"""
            <html>
            <body>
            <h2>Fresh Environment Test</h2>
            <p>This email was sent to <strong>{len(all_emails)} recipients</strong> using fresh environment variables:</p>
            <ul>
            """
            
            for type_label, email in all_emails:
                body += f"<li>{email} ({type_label})</li>"
            
            body += """
            </ul>
            <p>If you receive this, the environment variables are working correctly!</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send to all recipients
            result = server.sendmail(EMAIL_FROM, all_recipients, msg.as_string())
            
            if result:
                print(f"⚠️  Some emails failed: {result}")
            else:
                print(f"✅ Email sent successfully to all {len(all_emails)} recipients!")
                
    except Exception as e:
        print(f"❌ Email test failed: {e}")

if __name__ == "__main__":
    test_with_fresh_env()
