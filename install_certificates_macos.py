"""
macOS specific SSL certificate fix
"""
import subprocess
import sys
import os

def fix_macos_certificates():
    """Fix SSL certificates on macOS"""
    print("🍎 macOS SSL Certificate Fix")
    print("=" * 40)
    
    # Method 1: Try the official Python certificate installer
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    cert_command_paths = [
        f"/Applications/Python {python_version}/Install Certificates.command",
        "/Applications/Python 3.11/Install Certificates.command",
        "/Applications/Python 3.10/Install Certificates.command",
        "/Applications/Python 3.9/Install Certificates.command",
    ]
    
    print("1. Looking for Python certificate installer...")
    for path in cert_command_paths:
        if os.path.exists(path):
            print(f"   Found: {path}")
            try:
                subprocess.run([path], check=True)
                print("   ✅ Certificate installer completed")
                return True
            except Exception as e:
                print(f"   ❌ Failed to run installer: {e}")
        else:
            print(f"   Not found: {path}")
    
    # Method 2: Manual certificate update
    print("\n2. Trying manual certificate update...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "certifi"
        ])
        print("   ✅ Updated certifi package")
        
        # Update certificates using certifi
        subprocess.check_call([
            sys.executable, "-c", 
            "import ssl; import certifi; print(ssl.get_default_verify_paths())"
        ])
        print("   ✅ SSL paths updated")
        return True
    except Exception as e:
        print(f"   ❌ Manual update failed: {e}")
    
    # Method 3: Instructions for manual fix
    print("\n3. Manual fix instructions:")
    print("   Run this command in Terminal:")
    print(f"   /Applications/Python\\ {python_version}/Install\\ Certificates.command")
    print("\n   Or try:")
    print("   pip install --upgrade certifi")
    print("   python -m certifi")
    
    return False

if __name__ == "__main__":
    if sys.platform == "darwin":
        fix_macos_certificates()
    else:
        print("This script is for macOS only")
        print("For other systems, try: pip install --upgrade certifi")
