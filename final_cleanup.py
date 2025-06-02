"""
Final cleanup script - Remove all unnecessary files and keep only what's needed
"""
import os
import shutil
from pathlib import Path

def remove_file_if_exists(filepath):
    """Remove a file if it exists"""
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"🗑️  Removed: {filepath}")
        return True
    return False

def remove_directory_if_exists(dirpath):
    """Remove a directory if it exists"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
        print(f"🗑️  Removed directory: {dirpath}")
        return True
    return False

def final_cleanup():
    """Remove all unnecessary files and keep only essentials"""
    print("🧹 Final Cleanup - Removing unnecessary files...")
    print("=" * 60)
    
    # Files to remove (duplicates, tests, old versions)
    files_to_remove = [
        # Test files
        "test_system.py",
        "test_reddit_fix.py",
        "test_reddit_simple.py",
        "test_reddit_ssl_fix.py",
        "test_reddit_single_post.py",
        "test_reddit_sentiment.py",
        "test_reddit_top_posts.py",
        "test_reddit_bulletproof.py",
        "test_enhanced_digest.py",
        "test_trends_analysis.py",
        "test_imports.py",
        
        # Cleanup and setup files
        "cleanup.py",
        "verify_cleanup.py",
        "fix_dependencies.py",
        "quick_start.py",
        
        # Old main files
        "main.py",
        
        # Duplicate Reddit scrapers
        "scrapers/reddit_scraper_simple.py",
        "scrapers/reddit_scraper_fixed.py",
        "scrapers/reddit_scraper_improved.py",
        "scrapers/reddit_scraper_ssl_fixed.py",
        
        # Package structure files (we'll keep it simple)
        "ai_voice_scraper/__init__.py",
        "setup.py",
        "Dockerfile",
        "CHANGELOG.md",
        
        # Run scripts
        "run_app.sh",
        "HOW_TO_RUN.md",
        
        # Any remaining test or debug files
        "debug_*.py",
        "simple_*.py",
    ]
    
    # Directories to remove
    directories_to_remove = [
        "ai_voice_scraper",  # We'll keep the flat structure
        "tests",
        "__pycache__",
        ".pytest_cache",
        "data",  # Will be recreated if needed
    ]
    
    removed_files = 0
    removed_dirs = 0
    
    # Remove files
    for file_path in files_to_remove:
        if remove_file_if_exists(file_path):
            removed_files += 1
    
    # Remove directories
    for dir_path in directories_to_remove:
        if remove_directory_if_exists(dir_path):
            removed_dirs += 1
    
    # Remove any __pycache__ directories recursively
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                if remove_directory_if_exists(dir_path):
                    removed_dirs += 1
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   🗑️  Files removed: {removed_files}")
    print(f"   📁 Directories removed: {removed_dirs}")
    
    # Show what's left
    print(f"\n✅ Essential files remaining:")
    essential_files = [
        "main_fixed.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "config/keywords.py",
        "scrapers/news_scraper.py",
        "scrapers/reddit_scraper.py",
        "processors/content_processor.py",
        "processors/trends_analyzer.py",
        "storage/db_manager.py",
        "notifiers/email_notifier.py",
        "notifiers/slack_notifier.py",
        "templates/email_digest.html"
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} - MISSING!")
    
    if missing_files:
        print(f"\n⚠️  Warning: {len(missing_files)} essential files are missing!")
        print("You may need to restore them from the code blocks above.")
    else:
        print(f"\n🎉 Perfect! All {len(existing_files)} essential files are present.")
    
    print(f"\n📋 Your clean project structure:")
    print_project_structure()

def print_project_structure():
    """Print the final project structure"""
    structure = """
ai-voice-news-scraper/
├── main_fixed.py              # 🚀 Main application entry point
├── requirements.txt           # 📦 Dependencies
├── .env.example              # 🔧 Environment template
├── README.md                 # 📖 Documentation
├── config/
│   ├── __init__.py
│   └── keywords.py           # 🏷️  Voice AI keywords
├── scrapers/
│   ├── __init__.py
│   ├── news_scraper.py       # 📰 News scraping
│   └── reddit_scraper.py     # 💬 Reddit scraping (bulletproof)
├── processors/
│   ├── __init__.py
│   ├── content_processor.py  # 🔍 Content filtering & summarization
│   └── trends_analyzer.py    # 📊 Trend analysis
├── storage/
│   ├── __init__.py
│   └── db_manager.py         # 🗄️  Database operations
├── notifiers/
│   ├── __init__.py
│   ├── email_notifier.py     # 📧 Email notifications
│   └── slack_notifier.py     # 💬 Slack notifications
└── templates/
    └── email_digest.html     # 📧 Email template
"""
    print(structure)

def create_simple_run_script():
    """Create a simple run script"""
    run_script = """#!/bin/bash
# Simple run script for AI Voice News Scraper

echo "🔊 AI Voice News Scraper"
echo "======================="

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Copy .env.example to .env and add your API keys"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "🚀 Starting scraper..."
python main_fixed.py
"""
    
    with open("run.sh", "w") as f:
        f.write(run_script)
    
    # Make it executable on Unix systems
    try:
        os.chmod("run.sh", 0o755)
    except:
        pass
    
    print("✅ Created simple run.sh script")

if __name__ == "__main__":
    final_cleanup()
    create_simple_run_script()
    
    print("\n🎉 CLEANUP COMPLETE!")
    print("\n🚀 To run your app:")
    print("   1. Copy .env.example to .env")
    print("   2. Add your API keys to .env")
    print("   3. Run: python main_fixed.py")
    print("   4. Or run: ./run.sh")
