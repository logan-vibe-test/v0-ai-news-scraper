"""
Fix SSL certificate issues for Reddit API
"""
import ssl
import certifi
import os
import sys
import subprocess

def fix_ssl_certificates():
    """Fix SSL certificate issues"""
    print("🔧 Fixing SSL Certificate Issues...")
    
    # Method 1: Install/update certificates
    print("\n1. Installing/updating certificates...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "certifi"])
        print("✓ Updated certifi package")
    except Exception as e:
        print(f"⚠️ Could not update certifi: {e}")
    
    # Method 2: Check certificate location
    print("\n2. Checking certificate location...")
    try:
        import certifi
        cert_path = certifi.where()
        print(f"✓ Certificates located at: {cert_path}")
        
        if os.path.exists(cert_path):
            print("✓ Certificate file exists")
        else:
            print("❌ Certificate file missing")
    except Exception as e:
        print(f"❌ Error checking certificates: {e}")
    
    # Method 3: macOS specific fix
    if sys.platform == "darwin":  # macOS
        print("\n3. Applying macOS SSL fix...")
        try:
            # Try to run the macOS certificate update
            subprocess.run([
                "/Applications/Python 3.11/Install Certificates.command"
            ], check=False)
            print("✓ Attempted macOS certificate update")
        except:
            print("⚠️ Could not run macOS certificate update")
            print("   Try running this manually:")
            print("   /Applications/Python 3.11/Install Certificates.command")

def test_ssl_fix():
    """Test if SSL fix worked"""
    print("\n🧪 Testing SSL fix...")
    
    try:
        import requests
        import certifi
        
        # Test with explicit certificate verification
        response = requests.get(
            'https://www.reddit.com',
            verify=certifi.where(),
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SSL connection to Reddit successful!")
            return True
        else:
            print(f"⚠️ Got response code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SSL test failed: {e}")
        return False

if __name__ == "__main__":
    fix_ssl_certificates()
    test_ssl_fix()
