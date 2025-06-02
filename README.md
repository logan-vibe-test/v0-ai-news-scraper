# AI Voice News Scraper

A comprehensive Python-based system for monitoring AI voice technology news and developer reactions from Reddit.

## Features

- **News Monitoring**: Scrapes trusted tech news sites and company blogs for AI voice technology updates
- **Developer Reaction Tracking**: Monitors Reddit for community discussions about voice AI
- **Content Processing**: Filters for relevance, summarizes articles using OpenAI
- **Notification System**: Delivers daily digests via Slack and/or email
- **Executive Summary**: Provides AI-generated insights on the voice AI landscape

## Quick Start

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/yourusername/ai-voice-news-scraper
cd ai-voice-news-scraper

# Install the package
pip install -e .

# Create and configure your .env file
cp .env.example .env
# Edit .env with your API keys
\`\`\`

### Running the Scraper

\`\`\`bash
# Run with default settings
ai-voice-scraper

# Set custom log level
ai-voice-scraper --log-level DEBUG
\`\`\`

### Docker Installation

\`\`\`bash
# Build the Docker image
docker build -t ai-voice-scraper .

# Run the Docker container
docker run --env-file .env ai-voice-scraper
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

# Slack notifications
SLACK_API_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#ai-voice-news

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
\`\`\`

## Project Structure

\`\`\`
ai-voice-scraper/
├── ai_voice_scraper/           # Main package
│   ├── __init__.py
│   ├── main.py                 # Main entry point
│   ├── config/                 # Configuration
│   │   ├── __init__.py
│   │   └── keywords.py         # Voice AI keywords
│   ├── scrapers/               # Data sources
│   │   ├── __init__.py
│   │   ├── news_scraper.py     # News sites
│   │   └── reddit_scraper.py   # Reddit
│   ├── processors/             # Processing
│   │   ├── __init__.py
│   │   └── content_processor.py # Content filtering & summarization
│   ├── storage/                # Data storage
│   │   ├── __init__.py
│   │   └── db_manager.py       # Database operations
│   ├── notifiers/              # Notifications
│   │   ├── __init__.py
│   │   ├── email_notifier.py   # Email
│   │   └── slack_notifier.py   # Slack
│   └── templates/              # HTML templates
│       └── email_digest.html   # Email template
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_system.py          # System tests
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
├── README.md                   # Documentation
└── Dockerfile                  # Docker configuration
\`\`\`

## Customization

- **Keywords**: Edit `ai_voice_scraper/config/keywords.py` to customize voice AI detection
- **News Sources**: Edit `ai_voice_scraper/scrapers/news_scraper.py` to add/modify sources
- **Email Template**: Edit `ai_voice_scraper/templates/email_digest.html` for custom formatting

## API Setup Guides

### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Note the client ID and secret

### OpenAI API Setup
1. Sign up at https://platform.openai.com
2. Generate an API key
3. Add billing information

## Scheduling

### Local Scheduling with cron

Add to your crontab for daily runs:
\`\`\`bash
0 9 * * * cd /path/to/ai-voice-news-scraper && ai-voice-scraper
\`\`\`

### Scheduling with Systemd

Create a service file at `/etc/systemd/system/ai-voice-scraper.service`:

\`\`\`ini
[Unit]
Description=AI Voice News Scraper
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/ai-voice-news-scraper
ExecStart=/path/to/python -m ai_voice_scraper.main
User=youruser
Environment=PYTHONPATH=/path/to/ai-voice-news-scraper

[Install]
WantedBy=multi-user.target
\`\`\`

Create a timer file at `/etc/systemd/system/ai-voice-scraper.timer`:

\`\`\`ini
[Unit]
Description=Run AI Voice News Scraper daily

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
\`\`\`

Enable and start the timer:

\`\`\`bash
sudo systemctl enable ai-voice-scraper.timer
sudo systemctl start ai-voice-scraper.timer
\`\`\`

## License

MIT License - see LICENSE file for details
