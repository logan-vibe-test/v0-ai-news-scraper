"""
Fix missing dependencies for AI Voice News Scraper
"""
import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def download_spacy_model():
    """Download the spacy English model"""
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return True
    except subprocess.CalledProcessError:
        return False

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        return True
    except Exception:
        return False

def main():
    """Fix all dependency issues"""
    print("🔧 Fixing AI Voice News Scraper Dependencies")
    print("=" * 50)
    
    # Install missing packages
    missing_packages = ['spacy>=3.4.0', 'nltk>=3.8.0']
    
    for package in missing_packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            return False
    
    # Download spacy model
    print("📥 Downloading spacy English model...")
    if download_spacy_model():
        print("✅ Spacy model downloaded successfully")
    else:
        print("❌ Failed to download spacy model")
        return False
    
    # Download NLTK data
    print("📥 Downloading NLTK data...")
    if download_nltk_data():
        print("✅ NLTK data downloaded successfully")
    else:
        print("❌ Failed to download NLTK data")
        return False
    
    print("\n🎉 All dependencies fixed!")
    print("You can now run: python main_fixed.py")
    return True

if __name__ == "__main__":
    main()
