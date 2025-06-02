"""
Cleanup script to remove unnecessary files
"""
import os
import shutil
from pathlib import Path

def remove_file_if_exists(filepath):
    """Remove a file if it exists"""
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"✅ Removed: {filepath}")
    else:
        print(f"⚠️  Not found: {filepath}")

def remove_files():
    """Remove all unnecessary files"""
    print("🧹 Cleaning up unnecessary files...")
    
    # Debug and test files to remove
    files_to_remove = [
        # Debug files
        "better_news_sources.py",
        "config.py", 
        "create_reddit_app_guide.py",
        "debug_reddit.py",
        "debug_reddit_keywords.py", 
        "debug_scraper.py",
        "fix_reddit_requirements.py",
        "fix_selectors.py",
        "fix_ssl_reddit.py",
        "fix_ssl_simple.py",
        "install_certificates_macos.py",
        
        # Alternative main files
        "main_no_social.py",
        "main_with_working_reddit.py", 
        "main_news_only.py",
        "optimized_main.py",
        "simple_main.py",
        
        # Test files
        "simple_reddit_test.py",
        "simple_scraper.py",
        "test_email.py",
        "test_email_simple.py", 
        "test_keywords.py",
        "test_selectors.py",
        "test_social_scrapers.py",
        "test_reddit_standalone.py",
        "test_reddit_simple.py",
        "test_reddit_quick.py",
        
        # Reddit debug files
        "reddit_scraper_debug.py",
        "reddit_scraper_working.py", 
        "reddit_with_ssl_fix.py",
        "scrapers/reddit_scraper_ssl_fixed.py",
        
        # Twitter files (not working anyway)
        "scrapers/twitter_scraper.py",
        "scrapers/twitter_scraper_improved.py",
        
        # Other unused files
        "processors/sentiment_analyzer.py",
        "setup.py",
        "setup_news_only.py", 
        "requirements-flexible.txt"
    ]
    
    for file in files_to_remove:
        remove_file_if_exists(file)
    
    print(f"\n✅ Cleanup complete! Removed {len([f for f in files_to_remove if os.path.exists(f)])} files")

def show_remaining_files():
    """Show the clean project structure"""
    print("\n📁 Clean project structure:")
    print("├── main.py                    # Main entry point")
    print("├── test_system.py             # System tests") 
    print("├── requirements.txt           # Dependencies")
    print("├── .env.example              # Environment template")
    print("├── README.md                 # Documentation")
    print("├── config/")
    print("│   └── keywords.py           # Voice AI keywords")
    print("├── scrapers/")
    print("│   ├── news_scraper.py       # News sources")
    print("│   ├── reddit_scraper.py     # Reddit API")
    print("│   └── reddit_scraper_simple.py")
    print("├── processors/")
    print("│   └── content_processor.py  # Content processing")
    print("├── storage/")
    print("│   └── db_manager.py         # Database/file storage")
    print("├── notifiers/")
    print("│   ├── email_notifier.py     # Email notifications")
    print("│   └── slack_notifier.py     # Slack notifications")
    print("└── templates/")
    print("    └── email_digest.html     # Email template")

if __name__ == "__main__":
    remove_files()
    show_remaining_files()
