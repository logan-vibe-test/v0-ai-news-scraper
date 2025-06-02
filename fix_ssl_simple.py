"""
Simple SSL certificate fix
"""
import ssl
import certifi
import subprocess
import sys

def fix_ssl():
    """Fix SSL certificates"""
    print("🔧 Fixing SSL certificates...")
    
    try:
        # Update certifi
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "certifi"])
        print("✅ Updated certifi")
        
        # Check certificate path
        cert_path = certifi.where()
        print(f"✅ Certificates at: {cert_path}")
        
        # Test SSL
        import requests
        response = requests.get('https://www.reddit.com', timeout=10)
        print(f"✅ SSL test successful: {response.status_code}")
        
    except Exception as e:
        print(f"❌ SSL fix failed: {e}")
        print("Try running: /Applications/Python*/Install\\ Certificates.command")

if __name__ == "__main__":
    fix_ssl()
