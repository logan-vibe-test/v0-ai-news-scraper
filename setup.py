#!/usr/bin/env python3
"""
Setup script for AI Voice News Scraper
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def install_dependencies():
    """Install dependencies with fallback options"""
    print("📦 Installing dependencies...")
    
    # Try the main requirements first
    if run_command("pip install -r requirements.txt", "Installing main requirements"):
        return True
    
    print("⚠️  Main requirements failed, trying flexible versions...")
    
    # Try flexible requirements
    if run_command("pip install -r requirements-flexible.txt", "Installing flexible requirements"):
        return True
    
    print("⚠️  Flexible requirements failed, trying individual packages...")
    
    # Try installing packages individually
    packages = [
        "aiohttp",
        "beautifulsoup4", 
        "python-dotenv",
        "feedparser",
        "langchain",
        "langchain-community",
        "langchain-openai",
        "openai>=1.6.1,<2.0.0",
        "motor",
        "pymongo",
        "praw",
        "tweepy",
        "slack-sdk",
        "jinja2"
    ]
    
    failed_packages = []
    for package in packages:
        if not run_command(f"pip install '{package}'", f"Installing {package}"):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        print("💡 Try installing these manually or check for version conflicts")
        return False
    
    return True

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            run_command("cp .env.example .env", "Creating .env file from example")
            print("📝 Please edit .env file with your API keys and configuration")
        else:
            print("⚠️  No .env.example found. Please create .env file manually")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Voice News Scraper...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed due to dependency issues")
        print("💡 Try running: pip install --upgrade pip")
        print("💡 Or create a virtual environment: python -m venv venv && source venv/bin/activate")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python test_system.py")
    print("3. Run: python main.py")
    print("\n💡 For news-only mode: python main_no_social.py")

if __name__ == "__main__":
    main()
