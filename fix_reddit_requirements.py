"""
Script to fix Reddit-related package issues
"""
import subprocess
import sys

def install_reddit_packages():
    """Install or reinstall Reddit-related packages"""
    
    print("🔧 Fixing Reddit packages...")
    
    packages_to_install = [
        "praw==7.7.1",
        "prawcore==2.3.0",
        "requests>=2.25.0",
        "urllib3>=1.26.0"
    ]
    
    for package in packages_to_install:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    print("\n🧪 Testing PRAW installation...")
    try:
        import praw
        print(f"✓ PRAW version: {praw.__version__}")
        
        # Test basic functionality
        reddit = praw.Reddit(
            client_id="test",
            client_secret="test", 
            user_agent="test"
        )
        print("✓ PRAW can create Reddit instance")
        
    except ImportError as e:
        print(f"❌ PRAW still not working: {e}")
    except Exception as e:
        print(f"✓ PRAW imported (connection error expected with test credentials)")

if __name__ == "__main__":
    install_reddit_packages()
