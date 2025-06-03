# 🎙️ AI Voice News Scraper

**Stay up-to-date with AI voice technology news automatically.**

Get a daily email digest of the latest AI voice news, curated and summarized by AI. No more manually checking dozens of sources.

## What you get

- **Daily email digest** with the latest AI voice news
- **AI-powered summaries** of articles and discussions  
- **Reddit sentiment tracking** from AI communities
- **Trend analysis** to spot emerging topics

## Quick Setup

### 1. Clone and install
\`\`\`bash
git clone https://github.com/yourusername/ai-voice-news-scraper.git
cd ai-voice-news-scraper
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### 2. Set up your .env file
\`\`\`bash
cp .env.example .env
\`\`\`

Edit `.env` with your credentials:
\`\`\`bash
# Required
OPENAI_API_KEY=sk-your-key-here
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
EMAIL_TO=your-email@gmail.com

# Optional (for Reddit data)
REDDIT_CLIENT_ID=your-reddit-id
REDDIT_CLIENT_SECRET=your-reddit-secret
\`\`\`

### 3. Run it
\`\`\`bash
python main.py
\`\`\`

## Getting API Keys

**OpenAI**: Visit [platform.openai.com](https://platform.openai.com/api-keys) (~$2-5/month)

**Gmail**: Enable 2FA, then create an [App Password](https://myaccount.google.com/apppasswords)

**Reddit** (optional): Create an app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)

---

That's it! You'll get your first digest email within a few minutes.
