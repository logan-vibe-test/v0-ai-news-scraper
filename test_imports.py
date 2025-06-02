"""
Test script to verify all imports work correctly
"""
import sys
import os

def test_imports():
    """Test all the main imports"""
    print("🧪 Testing imports...")
    
    try:
        print("📰 Testing news scraper import...")
        from scrapers.news_scraper import scrape_news_sources
        print("✅ News scraper imported successfully")
    except ImportError as e:
        print(f"❌ News scraper import failed: {e}")
        return False
    
    try:
        print("💬 Testing Reddit scraper import...")
        from scrapers.reddit_scraper import scrape_reddit
        print("✅ Reddit scraper imported successfully")
    except ImportError as e:
        print(f"❌ Reddit scraper import failed: {e}")
        return False
    
    try:
        print("🔍 Testing content processor import...")
        from processors.content_processor import process_content
        print("✅ Content processor imported successfully")
    except ImportError as e:
        print(f"❌ Content processor import failed: {e}")
        return False
    
    try:
        print("🗄️ Testing database manager import...")
        from storage.db_manager import store_news_item, store_reaction, store_run_summary
        print("✅ Database manager imported successfully")
    except ImportError as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    try:
        print("📧 Testing email notifier import...")
        from notifiers.email_notifier import send_email_digest
        print("✅ Email notifier imported successfully")
    except ImportError as e:
        print(f"❌ Email notifier import failed: {e}")
        return False
    
    try:
        print("📊 Testing trends analyzer import...")
        from processors.trends_analyzer import analyze_current_trends
        print("✅ Trends analyzer imported successfully")
    except ImportError as e:
        print(f"❌ Trends analyzer import failed: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 Checking file structure...")
    
    required_files = [
        'scrapers/news_scraper.py',
        'scrapers/reddit_scraper.py',
        'processors/content_processor.py',
        'processors/trends_analyzer.py',
        'storage/db_manager.py',
        'notifiers/email_notifier.py',
        'notifiers/slack_notifier.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print(f"\n✅ All required files present")
        return True

if __name__ == "__main__":
    print("🔧 Import and File Structure Test")
    print("=" * 50)
    
    # Check file structure first
    files_ok = check_file_structure()
    
    if files_ok:
        # Test imports
        imports_ok = test_imports()
        
        if imports_ok:
            print("\n🎉 Everything looks good! You can run main.py now.")
        else:
            print("\n❌ Import issues found. Check the error messages above.")
    else:
        print("\n❌ Missing files. Make sure all required files are in place.")
