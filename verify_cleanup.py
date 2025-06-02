"""
Verify that we only have one Reddit scraper after cleanup
"""
import os
import glob

def check_reddit_scrapers():
    """Check for Reddit scraper files"""
    print("🔍 Checking for Reddit scraper files...")
    
    # Look for any files with 'reddit' in the name
    reddit_files = []
    
    # Check current directory
    for pattern in ['*reddit*.py', 'scrapers/*reddit*.py', 'ai_voice_scraper/scrapers/*reddit*.py']:
        reddit_files.extend(glob.glob(pattern))
    
    # Filter out non-scraper files
    scraper_files = [f for f in reddit_files if 'scraper' in f and not f.endswith('test_reddit.py')]
    
    print(f"\n📊 Found {len(scraper_files)} Reddit scraper files:")
    for file in scraper_files:
        print(f"  📄 {file}")
    
    if len(scraper_files) == 1:
        print(f"\n✅ Perfect! Only one Reddit scraper found: {scraper_files[0]}")
        return True
    elif len(scraper_files) > 1:
        print(f"\n❌ Found {len(scraper_files)} Reddit scrapers. Should only have 1!")
        print("Run the cleanup script to remove duplicates.")
        return False
    else:
        print("\n⚠️  No Reddit scrapers found!")
        return False

def check_project_structure():
    """Check the overall project structure"""
    print("\n🏗️  Checking project structure...")
    
    expected_files = [
        'scrapers/reddit_scraper.py',
        'scrapers/news_scraper.py',
        'processors/content_processor.py',
        'storage/db_manager.py',
        'notifiers/email_notifier.py',
        'notifiers/slack_notifier.py',
        'main.py'
    ]
    
    missing_files = []
    found_files = []
    
    for file in expected_files:
        if os.path.exists(file):
            found_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"✅ Found {len(found_files)} expected files")
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} files:")
        for file in missing_files:
            print(f"  📄 {file}")
    
    return len(missing_files) == 0

if __name__ == "__main__":
    print("🧹 Verifying cleanup results...")
    print("=" * 50)
    
    reddit_ok = check_reddit_scrapers()
    structure_ok = check_project_structure()
    
    print("\n" + "=" * 50)
    if reddit_ok and structure_ok:
        print("🎉 Cleanup verification PASSED!")
        print("✅ Project structure is clean and organized")
    else:
        print("❌ Cleanup verification FAILED!")
        print("Run cleanup.py to fix the issues")
