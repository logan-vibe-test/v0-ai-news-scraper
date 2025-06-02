"""
Quick Start Script for AI Voice News Scraper
This script helps you get started quickly with minimal setup
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    print("🔧 Checking environment setup...")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Creating .env template...")
        create_env_template()
        print("✅ .env template created. Please fill in your API keys.")
        return False
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ Environment setup looks good!")
    return True

def create_env_template():
    """Create a .env template file"""
    template = """# AI Voice News Scraper Configuration

# Required: OpenAI API for content summarization
OPENAI_API_KEY=your_openai_api_key_here

# Required: Email configuration for notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com

# Optional: MongoDB for data storage (will use file storage if not provided)
MONGODB_URI=mongodb://localhost:27017/ai_voice_news

# Optional: Reddit API for Reddit scraping
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=ai_voice_news_scraper_v1.0

# Optional: Slack notifications
SLACK_API_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#ai-voice-news

# Optional: Logging level
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(template)

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

async def run_quick_test():
    """Run a quick test of the system"""
    print("🧪 Running quick system test...")
    
    try:
        # Test imports
        from scrapers.news_scraper import scrape_news_sources
        from processors.content_processor import process_content
        print("✅ Core modules imported successfully")
        
        # Test news scraping (just a few items)
        print("📰 Testing news scraping...")
        news_items = await scrape_news_sources()
        print(f"✅ Found {len(news_items)} news articles")
        
        if news_items:
            # Test content processing on first item
            print("🔍 Testing content processing...")
            test_item = news_items[0]
            processed = await process_content(test_item)
            if processed:
                print("✅ Content processing works")
            else:
                print("⚠️ Content processing returned no results (might be normal)")
        
        print("🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

async def run_full_pipeline():
    """Run the full pipeline"""
    print("🚀 Running full AI Voice News Scraper pipeline...")
    
    try:
        from main_fixed import run_pipeline, setup_logging
        
        # Set up logging
        logger = setup_logging()
        
        # Run the pipeline
        results = await run_pipeline(logger)
        
        if "error" not in results:
            print("\n🎉 Pipeline completed successfully!")
            print(f"📊 Results:")
            print(f"   Articles found: {results['articles_found']}")
            print(f"   Articles processed: {results['articles_processed']}")
            print(f"   Reddit posts: {results['reddit_posts']}")
        else:
            print(f"❌ Pipeline failed: {results['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return False

def main():
    """Main quick start function"""
    print("🔊 AI Voice News Scraper - Quick Start")
    print("=" * 50)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Environment setup incomplete. Please fix the issues above and try again.")
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        return
    
    # Step 3: Choose what to run
    print("\n🎯 What would you like to do?")
    print("1. Run quick test (recommended for first time)")
    print("2. Run full pipeline")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🧪 Running quick test...")
        success = asyncio.run(run_quick_test())
        if success:
            print("\n✅ Quick test passed! You can now run the full pipeline.")
        else:
            print("\n❌ Quick test failed. Check the error messages above.")
    
    elif choice == "2":
        print("\n🚀 Running full pipeline...")
        success = asyncio.run(run_full_pipeline())
        if success:
            print("\n✅ Full pipeline completed! Check your email for the digest.")
        else:
            print("\n❌ Full pipeline failed. Check the error messages above.")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
