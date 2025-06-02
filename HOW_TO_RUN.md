# How to Run AI Voice News Scraper

## 🚀 Quick Start (Recommended)

### Option 1: Use the Quick Start Script
\`\`\`bash
python quick_start.py
\`\`\`
This interactive script will:
- ✅ Check your environment setup
- ✅ Install dependencies
- ✅ Guide you through first-time setup
- ✅ Run tests or the full pipeline

### Option 2: Manual Setup

1. **Set up environment variables:**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your API keys
   \`\`\`

2. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Run the application:**
   \`\`\`bash
   python main_fixed.py
   \`\`\`

## 📋 Prerequisites

### Required API Keys
- **OpenAI API Key** (for content summarization)
  - Get it from: https://platform.openai.com/api-keys
  - Add to .env as: `OPENAI_API_KEY=your_key_here`

### Optional API Keys
- **Reddit API** (for Reddit scraping)
  - Get it from: https://www.reddit.com/prefs/apps
  - Add to .env as: `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`

- **Email SMTP** (for email notifications)
  - Use Gmail, Outlook, or any SMTP server
  - Add credentials to .env

## 🎯 Different Ways to Run

### 1. Full Pipeline (Default)
\`\`\`bash
python main_fixed.py
\`\`\`
Runs the complete pipeline:
- 📰 Scrapes news sources
- 🔍 Processes and filters content
- 💬 Scrapes Reddit discussions
- 📊 Analyzes trends
- 📧 Sends email digest

### 2. Test Mode
\`\`\`bash
python test_imports.py        # Test imports
python test_system.py         # Test all components
python test_reddit_ssl_fix.py # Test Reddit specifically
\`\`\`

### 3. Individual Components
\`\`\`bash
# Test just news scraping
python -c "
import asyncio
from scrapers.news_scraper import scrape_news_sources
print(asyncio.run(scrape_news_sources()))
"

# Test just Reddit scraping
python test_reddit_single_post.py
\`\`\`

### 4. With Custom Settings
\`\`\`bash
python main_fixed.py --log-level DEBUG  # Verbose logging
\`\`\`

## 🔧 Troubleshooting

### Common Issues

**Import Errors:**
\`\`\`bash
python test_imports.py  # Diagnose import issues
\`\`\`

**SSL Issues with Reddit:**
\`\`\`bash
python test_reddit_ssl_fix.py  # Test Reddit SSL fixes
\`\`\`

**Missing Dependencies:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Environment Variables:**
\`\`\`bash
# Check if .env is loaded
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OpenAI Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
"
\`\`\`

## 📅 Scheduling (Optional)

### Run Daily with Cron
\`\`\`bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/your/project && python main_fixed.py
\`\`\`

### Run with systemd (Linux)
\`\`\`bash
# Create service file
sudo nano /etc/systemd/system/ai-voice-scraper.service

# Enable and start
sudo systemctl enable ai-voice-scraper.service
sudo systemctl start ai-voice-scraper.service
\`\`\`

## 📊 What Happens When You Run It

1. **News Scraping** (30-60 seconds)
   - Fetches articles from RSS feeds and websites
   - Filters for voice AI relevance

2. **Content Processing** (1-2 minutes)
   - Summarizes articles using OpenAI
   - Analyzes relevance to voice AI

3. **Reddit Scraping** (30-60 seconds)
   - Gets top post from each target subreddit
   - Analyzes sentiment

4. **Trends Analysis** (10-20 seconds)
   - Compares with previous runs
   - Identifies sentiment and activity trends

5. **Notifications** (10-30 seconds)
   - Sends email digest with trends
   - Optional Slack notification

**Total Runtime:** ~3-5 minutes

## 📧 Output

You'll receive an email digest containing:
- 📊 **Trends Analysis** (sentiment changes over time)
- 📰 **Top 5 Voice AI Articles** (with summaries)
- 💬 **Reddit Discussions** (with sentiment analysis)
- 📈 **Executive Summary** (AI-generated insights)

## 🆘 Getting Help

If you encounter issues:

1. **Run diagnostics:**
   \`\`\`bash
   python quick_start.py  # Choose option 1 for quick test
   \`\`\`

2. **Check logs:**
   \`\`\`bash
   tail -f ai_voice_scraper.log
   \`\`\`

3. **Test individual components:**
   \`\`\`bash
   python test_system.py
   \`\`\`

The quick start script is the easiest way to get everything working!
