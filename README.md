# AI Voice News Scraper

A comprehensive Python-based system for monitoring AI voice technology news and developer reactions.

## Features

- **News Monitoring**: Scrapes trusted tech news sites and company blogs for AI voice technology updates
- **Developer Reaction Tracking**: Monitors Reddit and Twitter for community discussions about the news
- **Content Processing**: Filters for relevance, summarizes articles, and analyzes sentiment
- **Notification System**: Delivers daily digests via Slack and/or email

## Setup

1. Clone the repository:
   \`\`\`
   git clone https://github.com/yourusername/ai-voice-news-scraper.git
   cd ai-voice-news-scraper
   \`\`\`

2. Create a virtual environment and install dependencies:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   \`\`\`

3. Copy the example environment file and fill in your API keys:
   \`\`\`
   cp .env.example .env
   # Edit .env with your API keys and configuration
   \`\`\`

4. Run the scraper:
   \`\`\`
   python main.py
   \`\`\`

## Configuration

Edit the `.env` file to configure:

- API keys for OpenAI, Reddit, and Twitter
- MongoDB connection details
- Notification settings (Slack and email)
- Scraping intervals and other preferences

## Architecture

The system consists of several components:

1. **Scrapers**: Modules for fetching content from news sites, Reddit, and Twitter
2. **Processors**: Content filtering, summarization, and sentiment analysis
3. **Storage**: MongoDB database for storing news and reactions
4. **Notifiers**: Slack and email notification systems

## License

MIT
