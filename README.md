# AI Voice News Scraper

A Python application that monitors AI voice technology news and community discussions, delivering daily digests with trend analysis.

## 🚀 Quick Start

1. **Setup environment:**
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

   Or use the run script:
   \`\`\`bash
   ./run.sh
   \`\`\`

## 📋 Required Configuration

### Essential API Keys (.env file)
\`\`\`env
# Required: OpenAI for content summarization
OPENAI_API_KEY=your_openai_api_key

# Required: Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com
\`\`\`

### Optional API Keys
\`\`\`env
# Optional: Reddit API (for Reddit discussions)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Optional: MongoDB (uses file storage if not provided)
MONGODB_URI=mongodb://localhost:27017/ai_voice_news

# Optional: Slack notifications
SLACK_API_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#ai-voice-news
\`\`\`

## 🎯 What It Does

1. **📰 Scrapes News** - Monitors tech news sites for voice AI articles
2. **🔍 Filters Content** - Uses AI to identify relevant voice AI news
3. **💬 Monitors Reddit** - Tracks discussions in relevant subreddits
4. **📊 Analyzes Trends** - Compares sentiment and activity over time
5. **📧 Sends Digest** - Delivers comprehensive email with insights

## 📁 Project Structure

\`\`\`
ai-voice-news-scraper/
├── main_fixed.py              # Main application
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── config/keywords.py        # Voice AI keywords
├── scrapers/                 # Data collection
├── processors/               # Content processing & trends
├── storage/                  # Database operations
├── notifiers/                # Email & Slack notifications
└── templates/                # Email template
\`\`\`

## 🔧 API Setup

### OpenAI API
1. Visit https://platform.openai.com/api-keys
2. Create an API key
3. Add to .env as `OPENAI_API_KEY`

### Reddit API (Optional)
1. Visit https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Add client ID and secret to .env

### Gmail SMTP (Recommended)
1. Enable 2-factor authentication
2. Generate an app password
3. Use app password in .env (not your regular password)

## 📧 Output

You'll receive a daily email digest containing:
- **📊 Trends Analysis** - Sentiment changes over recent runs
- **📰 Top Voice AI Articles** - Curated and summarized
- **💬 Reddit Discussions** - Community sentiment analysis
- **🎯 Executive Summary** - AI-generated insights

## 📅 Scheduling

### Daily Cron Job
\`\`\`bash
# Run daily at 9 AM
0 9 * * * cd /path/to/project && python main_fixed.py
\`\`\`

### Manual Run
\`\`\`bash
python main_fixed.py
\`\`\`

## 🆘 Troubleshooting

**Import Errors:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Missing .env:**
\`\`\`bash
cp .env.example .env
# Edit with your API keys
\`\`\`

**Reddit SSL Issues:**
The Reddit scraper includes automatic SSL fixes.

**No Email Received:**
- Check spam folder
- Verify SMTP credentials
- Test with Gmail app password

## 📊 Runtime

- **Duration:** ~3-5 minutes
- **Articles Found:** 10-30 per run
- **Reddit Posts:** 5-15 per run
- **Memory Usage:** ~100MB
- **Network:** Moderate (RSS feeds + API calls)

## 🎉 Success Indicators

When working correctly, you should see:
\`\`\`
🚀 Starting AI Voice News Scraper
📰 Found 15 articles
🔍 Processed 8 relevant articles
💬 Found 6 Reddit posts about AI voice
📊 Stored run summary for trends analysis
✅ Email sent
✅ Pipeline complete
\`\`\`

## 📝 License

MIT License - Feel free to modify and use for your projects.
\`\`\`

```plaintext file="requirements.txt"
# Core dependencies
aiohttp>=3.8.0
beautifulsoup4>=4.11.0
python-dotenv>=1.0.0
feedparser>=6.0.0

# AI/ML processing
langchain>=0.1.0
langchain-community>=0.0.10
langchain-openai>=0.0.2
openai>=1.6.1,&lt;2.0.0

# Database (optional)
motor>=3.3.0
pymongo>=4.6.0

# Reddit API
praw>=7.7.0
prawcore>=2.3.0
requests>=2.28.0
urllib3>=1.26.0
certifi>=2023.0.0

# Notifications
slack-sdk>=3.26.0
jinja2>=3.1.0
