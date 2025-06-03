# 🎙️ AI Voice News Scraper

> **Intelligent monitoring and analysis of AI voice technology news and community discussions**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An automated intelligence platform that monitors the rapidly evolving AI voice technology landscape, delivering curated insights through daily email digests with trend analysis and sentiment tracking.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (required)
- Email SMTP access (Gmail recommended)
- Reddit API credentials (optional but recommended)

### Installation

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/yourusername/ai-voice-news-scraper.git
   cd ai-voice-news-scraper
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Configure environment**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your API keys
   \`\`\`

4. **Run the scraper**
   \`\`\`bash
   python main.py
   \`\`\`

## ⚙️ Configuration

Create a `.env` file with the following settings:

\`\`\`
# OpenAI API (Required for content processing and summaries)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email Configuration (Required)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Multiple Recipients Support
EMAIL_TO=recipient1@gmail.com,recipient2@company.com,recipient3@example.com
EMAIL_CC=optional-cc@company.com,another-cc@example.com
EMAIL_BCC=optional-bcc@company.com

# Reddit API (Highly Recommended)
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# Database (Optional - uses file storage if not provided)
MONGODB_URI=mongodb://localhost:27017/ai_voice_news

# Slack Notifications (Optional)
SLACK_API_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#ai-voice-news

# Logging Level (Optional)
LOG_LEVEL=INFO
\`\`\`

### API Setup Guides

<details>
<summary><strong>🔑 OpenAI API Setup</strong></summary>

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add billing information (required for API access)
4. Copy the key to your `.env` file
5. **Cost estimate**: ~$2-5/month for daily runs

</details>

<details>
<summary><strong>📧 Gmail SMTP Setup</strong></summary>

1. Enable 2-factor authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use this app password (not your regular password) in `.env`
5. **Security**: App passwords are safer than regular passwords

</details>

<details>
<summary><strong>🔴 Reddit API Setup</strong></summary>

1. Visit [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Copy the client ID and secret to your `.env` file
5. **Rate limits**: 60 requests per minute (automatically handled)

</details>

---

## 📊 What You'll Receive

### Daily Email Digest Contains:

- **Executive Summary**: AI-generated overview of key developments
- **Curated News Articles**: Most relevant voice AI articles with summaries
- **Community Insights**: Top Reddit discussions about voice AI
- **Trend Analysis**: Sentiment changes and emerging topics

---

## 🔧 Project Structure

\`\`\`
ai-voice-news-scraper/
├── main.py                  # Main application entry point
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── README.md                # Documentation
├── config/                  # Configuration files
├── scrapers/                # News and Reddit scrapers
├── processors/              # Content processing and analysis
├── storage/                 # Database operations
├── notifiers/               # Email and Slack notifications
└── templates/               # Email templates
\`\`\`

## 📄 License

This project is licensed under the MIT License.
