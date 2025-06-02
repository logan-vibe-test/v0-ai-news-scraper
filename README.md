# AI Voice News Scraper

A comprehensive Python-based system for monitoring AI voice technology news and developer reactions from Reddit and Twitter.

## Features

- **News Monitoring**: Scrapes trusted tech news sites and company blogs for AI voice technology updates
- **Developer Reaction Tracking**: Monitors Reddit and Twitter for community discussions about the news
- **Content Processing**: Filters for relevance, summarizes articles, and analyzes sentiment
- **Notification System**: Delivers daily digests via Slack and/or email

## Quick Start

1. **Clone and setup**:
   \`\`\`bash
   git clone <your-repo-url>
   cd ai-voice-news-scraper
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   \`\`\`

2. **Configure environment**:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your API keys
   \`\`\`

3. **Run the scraper**:
   \`\`\`bash
   # Full system (news + social media)
   python main.py
   
   # News only (no social media)
   python main_no_social.py
   \`\`\`

## Configuration

### Required Environment Variables

\`\`\`env
# OpenAI (for content summarization)
OPENAI_API_KEY=your_openai_api_key

# MongoDB (for data storage)
MONGODB_URI=mongodb://localhost:27017/ai_voice_news

# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com
\`\`\`

### Optional Environment Variables

\`\`\`env
# Reddit API (for Reddit scraping)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=ai_voice_news_scraper_v1.0

# Twitter API (for Twitter scraping)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Slack notifications
SLACK_API_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#ai-voice-news
\`\`\`

## Project Structure

\`\`\`
ai-voice-news-scraper/
├── main.py                 # Main entry point (full system)
├── main_no_social.py       # News-only version
├── test_system.py          # System tests
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── config/
│   ├── __init__.py
│   └── keywords.py        # Voice AI keywords configuration
├── scrapers/
│   ├── __init__.py
│   ├── news_scraper.py    # News sources scraper
│   ├── reddit_scraper.py  # Reddit scraper
│   └── twitter_scraper.py # Twitter scraper
├── processors/
│   ├── __init__.py
│   ├── content_processor.py    # Content filtering & summarization
│   └── sentiment_analyzer.py  # Sentiment analysis
├── storage/
│   ├── __init__.py
│   └── db_manager.py      # Database operations
├── notifiers/
│   ├── __init__.py
│   ├── email_notifier.py  # Email notifications
│   └── slack_notifier.py  # Slack notifications
└── templates/
    └── email_digest.html  # Email template
\`\`\`

## Usage

### Running the System

\`\`\`bash
# Test the system first
python test_system.py

# Run once (for testing)
python main.py

# For production: uncomment the scheduling code in main.py
# to run daily automatically
\`\`\`

### Customization

- **Keywords**: Edit `config/keywords.py` to customize voice AI detection
- **News Sources**: Edit `scrapers/news_scraper.py` to add/modify sources
- **Email Template**: Edit `templates/email_digest.html` for custom formatting

## API Setup Guides

### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Note the client ID and secret

### Twitter API Setup
1. Apply for Twitter Developer account
2. Create a new app
3. Generate Bearer Token

### OpenAI API Setup
1. Sign up at https://platform.openai.com
2. Generate an API key
3. Add billing information

## Deployment

### Local Scheduling
Add to your crontab for daily runs:
\`\`\`bash
0 9 * * * cd /path/to/ai-voice-news-scraper && python main.py
\`\`\`

### Docker Deployment
\`\`\`dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
\`\`\`

## License

MIT License - see LICENSE file for details
\`\`\`

Now let's create a clean environment template:
