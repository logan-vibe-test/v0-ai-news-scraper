"""
Cleanup script to organize and streamline the AI Voice News Scraper codebase
"""
import os
import shutil
from pathlib import Path
import re

def remove_file_if_exists(filepath):
    """Remove a file if it exists"""
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"✅ Removed: {filepath}")
    else:
        print(f"⚠️  Not found: {filepath}")

def ensure_directory(directory):
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"📁 Ensured directory: {directory}")

def cleanup_codebase():
    """Clean up and organize the codebase"""
    print("🧹 Cleaning up and organizing the AI Voice News Scraper codebase...")
    
    # Create proper package structure
    ensure_directory("ai_voice_scraper")
    ensure_directory("ai_voice_scraper/config")
    ensure_directory("ai_voice_scraper/scrapers")
    ensure_directory("ai_voice_scraper/processors")
    ensure_directory("ai_voice_scraper/storage")
    ensure_directory("ai_voice_scraper/notifiers")
    ensure_directory("ai_voice_scraper/templates")
    ensure_directory("tests")
    
    # Files to remove
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
        "test_reddit_fix.py",
        "test_enhanced_digest.py",
        
        # Reddit debug files
        "reddit_scraper_debug.py",
        "reddit_scraper_working.py", 
        "reddit_with_ssl_fix.py",
        "scrapers/reddit_scraper_ssl_fixed.py",
        "scrapers/reddit_scraper_simple.py",
        
        # Twitter files (not working anyway)
        "scrapers/twitter_scraper.py",
        "scrapers/twitter_scraper_improved.py",
    ]
    
    for file in files_to_remove:
        remove_file_if_exists(file)
    
    # Identify and organize proper package structure
    source_files = {
        # Main app files
        "main.py": "ai_voice_scraper/main.py",
        
        # Config files
        "config/__init__.py": "ai_voice_scraper/config/__init__.py",
        "config/keywords.py": "ai_voice_scraper/config/keywords.py",
        
        # Scrapers
        "scrapers/__init__.py": "ai_voice_scraper/scrapers/__init__.py",
        "scrapers/news_scraper.py": "ai_voice_scraper/scrapers/news_scraper.py",
        "scrapers/reddit_scraper.py": "ai_voice_scraper/scrapers/reddit_scraper.py",
        "scrapers/reddit_scraper_fixed.py": "ai_voice_scraper/scrapers/reddit_scraper_impl.py",
        
        # Processors
        "processors/__init__.py": "ai_voice_scraper/processors/__init__.py",
        "processors/content_processor.py": "ai_voice_scraper/processors/content_processor.py",
        
        # Storage
        "storage/__init__.py": "ai_voice_scraper/storage/__init__.py",
        "storage/db_manager.py": "ai_voice_scraper/storage/db_manager.py",
        
        # Notifiers
        "notifiers/__init__.py": "ai_voice_scraper/notifiers/__init__.py",
        "notifiers/email_notifier.py": "ai_voice_scraper/notifiers/email_notifier.py",
        "notifiers/slack_notifier.py": "ai_voice_scraper/notifiers/slack_notifier.py",
        
        # Templates
        "templates/email_digest.html": "ai_voice_scraper/templates/email_digest.html",
        
        # Tests 
        "test_system.py": "tests/test_system.py"
    }
    
    for source, destination in source_files.items():
        if os.path.exists(source):
            # Create destination directory if needed
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Copy file to new location
            shutil.copy2(source, destination)
            print(f"📋 Copied: {source} → {destination}")
            
            # Update imports in the copied file
            update_imports(destination)
    
    # Create __init__.py files for proper package structure
    for directory in ["ai_voice_scraper", "tests"]:
        init_file = f"{directory}/__init__.py"
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""\n{directory.replace("_", " ").title()} package for AI Voice News Scraper\n"""\n')
            print(f"✏️  Created: {init_file}")
    
    # Create setup.py file
    create_setup_file()
    
    print("\n✅ Cleanup complete! Codebase has been organized into a proper package structure.")
    print("\nTo install the package in development mode:")
    print("pip install -e .")

def update_imports(file_path):
    """Update imports in Python files to use the new package structure"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update imports for the ai_voice_scraper package
    # from config import X -> from ai_voice_scraper.config import X
    # from scrapers import X -> from ai_voice_scraper.scrapers import X
    # etc.
    modules = ["config", "scrapers", "processors", "storage", "notifiers"]
    
    for module in modules:
        # Match both 'import module.x' and 'from module import x'
        content = re.sub(
            rf'from {module}(\.[\w]+)? import', 
            f'from ai_voice_scraper.{module}\\1 import', 
            content
        )
        content = re.sub(
            rf'import {module}(\.[\w]+)?', 
            f'import ai_voice_scraper.{module}\\1', 
            content
        )
    
    # Update relative imports like "from .module import X"
    # Only needed if we're reorganizing internal references
    
    # Write updated content back to file
    with open(file_path, 'w') as f:
        f.write(content)

def create_setup_file():
    """Create setup.py file for the package"""
    setup_content = """
from setuptools import setup, find_packages

setup(
    name="ai-voice-scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.11.0",
        "python-dotenv>=1.0.0",
        "feedparser>=6.0.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.2",
        "openai>=1.6.1,<2.0.0",
        "motor>=3.3.0",
        "pymongo>=4.6.0",
        "praw>=7.7.0",
        "certifi>=2023.0.0",
        "slack-sdk>=3.26.0",
        "jinja2>=3.1.0",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "ai_voice_scraper": ["templates/*.html"],
    },
    entry_points={
        "console_scripts": [
            "ai-voice-scraper=ai_voice_scraper.main:main_cli",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive scraper for AI voice technology news and discussions",
    keywords="ai, voice, news, scraper",
    url="https://github.com/yourusername/ai-voice-news-scraper",
)
"""
    with open("setup.py", 'w') as f:
        f.write(setup_content)
    print("✏️  Created: setup.py")

if __name__ == "__main__":
    cleanup_codebase()
