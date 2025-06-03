"""
Cleanup script to organize the AI Voice News Scraper project
"""
import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up the project by removing debug files and organizing code"""
    print("🧹 Cleaning up AI Voice News Scraper project...")
    
    # Files to remove (all debugging and test scripts)
    files_to_remove = [
        # Test scripts
        "test_email_recipients.py",
        "test_fixed_app.py",
        "test_gmail_cc_issue.py",
        "test_main_email.py",
        "test_reddit.py",
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
        
        # Debug scripts
        "debug_email.py",
        "debug_email_fresh.py",
        "clear_env_cache.py",
        "restart_and_test.py",
        "quick_fix_test.py",
        
        # Old main files
        "main.py",
        "main_fixed.py",
        
        # Cleanup scripts
        "cleanup.py",
        "verify_cleanup.py",
        "fix_dependencies.py",
        "quick_start.py",
        "final_cleanup.py",
        
        # This cleanup script itself (will be removed at the end)
        "cleanup_project.py"
    ]
    
    # Rename main_fixed_final.py to main.py
    if os.path.exists("main_fixed_final.py"):
        print("✅ Renaming main_fixed_final.py to main.py")
        if os.path.exists("main.py"):
            os.remove("main.py")
        shutil.copy("main_fixed_final.py", "main.py")
    
    # Make sure we're using the correct email notifier
    if os.path.exists("notifiers/email_notifier_fixed_final.py"):
        print("✅ Updating email_notifier.py with the fixed version")
        if os.path.exists("notifiers/email_notifier.py"):
            os.remove("notifiers/email_notifier.py")
        shutil.copy("notifiers/email_notifier_fixed_final.py", "notifiers/email_notifier.py")
    
    # Update imports in main.py to use the standard email_notifier
    if os.path.exists("main.py"):
        with open("main.py", "r") as f:
            content = f.read()
        
        # Replace import for email_notifier_fixed_final with email_notifier
        content = content.replace(
            "from notifiers.email_notifier_fixed_final import send_email_digest",
            "from notifiers.email_notifier import send_email_digest"
        )
        
        with open("main.py", "w") as f:
            f.write(content)
        
        print("✅ Updated imports in main.py")
    
    # Remove all test and debug files
    removed_count = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
    
    # Remove old email notifier files
    for file_path in ["notifiers/email_notifier_fixed.py", "notifiers/email_notifier_fixed_final.py"]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
    
    print(f"\n🎉 Cleanup complete! Removed {removed_count} files.")
    print("\n📋 How to run the scraper:")
    print("   1. Make sure your .env file is configured")
    print("   2. Run: python main.py")

if __name__ == "__main__":
    cleanup_project()
