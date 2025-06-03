"""
Script to clear environment variable cache and test fresh loading
"""
import os
import sys
from dotenv import load_dotenv

def clear_and_reload_env():
    """Clear environment cache and reload .env file"""
    print("🧹 Clearing environment variable cache...")
    
    # Clear specific variables from os.environ
    env_vars_to_clear = [
        'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD',
        'EMAIL_FROM', 'EMAIL_TO', 'EMAIL_CC', 'EMAIL_BCC'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
            print(f"  Cleared: {var}")
    
    # Force reload the .env file
    print("\n🔄 Reloading .env file...")
    load_dotenv(override=True)  # override=True forces reload
    
    # Display current values
    print("\n📋 Current environment variables:")
    for var in env_vars_to_clear:
        value = os.getenv(var, 'NOT SET')
        if var in ['SMTP_PASSWORD']:
            # Mask password
            display_value = value[:4] + '*' * (len(value) - 4) if value != 'NOT SET' else 'NOT SET'
        else:
            display_value = value
        print(f"  {var}: {display_value}")
    
    # Test email parsing
    print("\n🧪 Testing email parsing with fresh values...")
    email_to = os.getenv('EMAIL_TO', '')
    email_cc = os.getenv('EMAIL_CC', '')
    
    print(f"Raw EMAIL_TO: '{email_to}'")
    print(f"Raw EMAIL_CC: '{email_cc}'")
    
    # Parse emails
    to_emails = []
    if email_to:
        for email in email_to.split(','):
            email = email.strip()
            if email and '@' in email:
                to_emails.append(email)
    
    cc_emails = []
    if email_cc:
        for email in email_cc.split(','):
            email = email.strip()
            if email and '@' in email:
                cc_emails.append(email)
    
    print(f"\nParsed TO emails ({len(to_emails)}): {to_emails}")
    print(f"Parsed CC emails ({len(cc_emails)}): {cc_emails}")
    print(f"Total recipients: {len(to_emails) + len(cc_emails)}")
    
    return to_emails + cc_emails

if __name__ == "__main__":
    emails = clear_and_reload_env()
    print(f"\n✅ Found {len(emails)} total email addresses")
    for i, email in enumerate(emails, 1):
        print(f"  {i}. {email}")
