"""
Email notifier for AI Voice News Scraper - Enhanced with trends analysis
"""
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import jinja2
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from processors.trends_analyzer import analyze_current_trends
from storage.db_manager import store_run_summary

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Jinja2 template environment
template_loader = jinja2.FileSystemLoader(searchpath="./templates")
template_env = jinja2.Environment(loader=template_loader)

async def generate_executive_summary(news_items, reactions):
    """Generate an executive summary of the voice AI landscape"""
    if not OPENAI_API_KEY:
        return "Executive summary not available (OpenAI API key not configured)"
    
    try:
        # Prepare content for summarization
        news_content = []
        for item in news_items[:10]:  # Use top 10 for summary
            news_content.append(f"• {item['title']} ({item['source']}): {item.get('summary', '')[:200]}")
        
        reddit_content = []
        for reaction in reactions[:10]:  # Use top 10 for summary
            reddit_content.append(f"• r/{reaction.get('subreddit', 'unknown')}: {reaction.get('title', reaction.get('content', ''))[:150]}")
        
        # Create the prompt
        prompt_template = """
        You are an AI analyst specializing in voice AI technology trends. Based on the following news articles and community discussions, write a concise executive summary (2-3 paragraphs) that highlights:

        1. Key developments and trends in voice AI technology
        2. Notable company announcements or product launches
        3. Emerging themes or concerns in the voice AI space
        4. Market implications and future outlook

        NEWS ARTICLES:
        {news_content}

        COMMUNITY DISCUSSIONS:
        {reddit_content}

        Write an executive summary that provides strategic insights for someone tracking the voice AI industry. Focus on the most significant developments and their implications.

        EXECUTIVE SUMMARY:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["news_content", "reddit_content"]
        )
        
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo")
        
        # Generate the summary
        formatted_prompt = prompt.format(
            news_content="\n".join(news_content) if news_content else "No news articles found",
            reddit_content="\n".join(reddit_content) if reddit_content else "No community discussions found"
        )
        
        summary = llm.invoke(formatted_prompt)
        return summary.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {str(e)}")
        return "Error generating executive summary. Please check the logs for details."

def select_top_articles(news_items, limit=5):
    """Select the top most relevant articles"""
    if not news_items:
        return []
    
    # Sort by relevance (you can customize this scoring)
    def relevance_score(item):
        score = 0
        title_lower = item.get('title', '').lower()
        summary_lower = item.get('summary', '').lower()
        
        # High-value keywords get higher scores
        high_value_keywords = [
            'elevenlabs', 'openai voice', 'breakthrough', 'launch', 'release',
            'funding', 'acquisition', 'partnership', 'new model', 'api'
        ]
        
        for keyword in high_value_keywords:
            if keyword in title_lower or keyword in summary_lower:
                score += 10
        
        # Medium-value keywords
        medium_value_keywords = [
            'voice ai', 'text-to-speech', 'speech synthesis', 'voice cloning',
            'ai voice', 'neural voice', 'voice generation'
        ]
        
        for keyword in medium_value_keywords:
            if keyword in title_lower:
                score += 5
            elif keyword in summary_lower:
                score += 3
        
        # Prefer recent articles (simple heuristic)
        if 'today' in summary_lower or 'announced' in summary_lower:
            score += 5
        
        return score
    
    # Sort by relevance score
    sorted_items = sorted(news_items, key=relevance_score, reverse=True)
    
    # Return top articles
    return sorted_items[:limit]

def calculate_sentiment_summary(reactions):
    """Calculate sentiment summary from reactions"""
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    subreddit_activity = {}
    
    for reaction in reactions:
        sentiment = reaction.get('sentiment', 'neutral')
        sentiment_counts[sentiment] += 1
        
        subreddit = reaction.get('subreddit', 'unknown')
        subreddit_activity[subreddit] = subreddit_activity.get(subreddit, 0) + 1
    
    return sentiment_counts, subreddit_activity

async def send_email_digest(digest):
    """Send a digest via email with executive summary and trends analysis"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]):
        logger.error("Email configuration not complete")
        return False
    
    try:
        # Calculate sentiment summary for trends
        sentiment_summary, subreddit_activity = calculate_sentiment_summary(digest.get('reactions', []))
        
        # Prepare run data for trends analysis
        current_run_data = {
            'articles_found': len(digest.get('news_items', [])),
            'articles_processed': len(digest.get('news_items', [])),
            'reddit_posts': len(digest.get('reactions', [])),
            'sentiment_summary': sentiment_summary,
            'subreddit_activity': subreddit_activity
        }
        
        # Analyze trends
        logger.info("Analyzing trends from recent runs...")
        trends_data = await analyze_current_trends(current_run_data)
        
        # Store this run's summary for future trend analysis
        await store_run_summary(current_run_data)
        
        # Generate executive summary
        logger.info("Generating executive summary...")
        executive_summary = await generate_executive_summary(
            digest['news_items'], 
            digest.get('reactions', [])
        )
        
        # Select top 5 articles
        top_articles = select_top_articles(digest['news_items'], limit=5)
        
        # Create enhanced digest with detailed statistics
        enhanced_digest = {
            **digest,
            'executive_summary': executive_summary,
            'top_articles': top_articles,
            'total_articles_found': len(digest['news_items']),
            'total_articles_relevant': len([item for item in digest['news_items'] if item.get('summary')]),
            'total_reddit_posts_scanned': digest.get('total_reddit_scanned', 0),
            'total_reddit_posts_included': len(digest.get('reactions', [])),
            'trends': trends_data,
            'processing_stats': {
                'articles_found': len(digest['news_items']),
                'articles_relevant': len([item for item in digest['news_items'] if item.get('summary')]),
                'reddit_scanned': digest.get('total_reddit_scanned', 0),
                'reddit_included': len(digest.get('reactions', [])),
                'relevance_rate': round((len([item for item in digest['news_items'] if item.get('summary')]) / max(len(digest['news_items']), 1)) * 100, 1)
            }
        }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔊 AI Voice News Digest - {digest['date']}"
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        # Create HTML content
        html_content = format_digest_for_email(enhanced_digest)
        
        # Attach parts
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Sent enhanced email digest with trends to {EMAIL_TO}")
        return True
    except Exception as e:
        logger.error(f"Error sending email digest: {str(e)}")
        return False

def format_digest_for_email(digest):
    """Format the enhanced digest data for email HTML"""
    try:
        # Try to load the template
        template = template_env.get_template('email_digest.html')
    except jinja2.exceptions.TemplateNotFound:
        # If template doesn't exist, use an enhanced inline template with trends
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Voice News Digest</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }
                .container {
                    background-color: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                }
                h2 {
                    color: #3498db;
                    margin-top: 30px;
                    margin-bottom: 20px;
                }
                h3 {
                    color: #e74c3c;
                    margin-top: 25px;
                    margin-bottom: 15px;
                    border-left: 4px solid #e74c3c;
                    padding-left: 15px;
                }
                .executive-summary {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                .executive-summary h2 {
                    color: white;
                    margin-top: 0;
                    margin-bottom: 15px;
                }
                .trends-section {
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                .trends-section h2 {
                    color: white;
                    margin-top: 0;
                    margin-bottom: 15px;
                }
                .trend-item {
                    background-color: rgba(255,255,255,0.15);
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .trend-label {
                    font-weight: bold;
                }
                .trend-value {
                    font-size: 18px;
                }
                .insights-list {
                    list-style: none;
                    padding: 0;
                }
                .insights-list li {
                    background-color: rgba(255,255,255,0.1);
                    padding: 10px;
                    margin-bottom: 8px;
                    border-radius: 5px;
                }
                .stats {
                    background-color: #ecf0f1;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    text-align: center;
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                }
                .stat-item {
                    margin: 10px;
                    min-width: 120px;
                }
                .stat-number {
                    font-size: 28px;
                    font-weight: bold;
                    color: #3498db;
                    display: block;
                }
                .stat-label {
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }
                .news-item {
                    margin-bottom: 30px;
                    border-left: 4px solid #3498db;
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 8px 8px 0;
                    transition: transform 0.2s ease;
                }
                .news-item:hover {
                    transform: translateX(5px);
                }
                .news-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }
                .news-title a {
                    color: #2c3e50;
                    text-decoration: none;
                }
                .news-title a:hover {
                    color: #3498db;
                }
                .news-meta {
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-bottom: 12px;
                    font-weight: 500;
                }
                .news-summary {
                    font-size: 16px;
                    line-height: 1.6;
                }
                .reddit-section {
                    background: linear-gradient(135deg, #ff4500 0%, #ff6b35 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px;
                    margin-top: 30px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                .reddit-section h2 {
                    color: white;
                    margin-top: 0;
                    margin-bottom: 20px;
                }
                .reddit-subreddit {
                    margin-bottom: 25px;
                }
                .reddit-subreddit h3 {
                    color: white;
                    border-left: 4px solid rgba(255,255,255,0.5);
                    margin-bottom: 15px;
                    font-size: 18px;
                }
                .reddit-post {
                    background-color: rgba(255,255,255,0.15);
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border-left: 3px solid rgba(255,255,255,0.3);
                }
                .reddit-post:last-child {
                    margin-bottom: 0;
                }
                .reddit-post.positive {
                    border-left-color: #2ecc71;
                    background-color: rgba(46, 204, 113, 0.1);
                }
                .reddit-post.negative {
                    border-left-color: #e74c3c;
                    background-color: rgba(231, 76, 60, 0.1);
                }
                .reddit-post.neutral {
                    border-left-color: #95a5a6;
                    background-color: rgba(149, 165, 166, 0.1);
                }
                .reddit-meta {
                    font-size: 14px;
                    opacity: 0.9;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .sentiment-indicator {
                    font-size: 16px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 12px;
                    background-color: rgba(255,255,255,0.2);
                }
                .reddit-title {
                    font-weight: 500;
                    margin-bottom: 8px;
                }
                .reddit-title a {
                    color: white;
                    text-decoration: none;
                }
                .reddit-title a:hover {
                    text-decoration: underline;
                }
                .reddit-summary {
                    font-size: 14px;
                    opacity: 0.9;
                    font-style: italic;
                    margin-bottom: 8px;
                }
                .reddit-links {
                    font-size: 12px;
                    opacity: 0.8;
                }
                .reddit-links a {
                    color: white;
                    margin-right: 10px;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ecf0f1;
                    font-size: 14px;
                    color: #7f8c8d;
                    text-align: center;
                }
                .emoji {
                    font-size: 24px;
                    margin-right: 10px;
                }
                .highlight {
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #ffc107;
                    margin-bottom: 20px;
                }
                .sentiment-summary {
                    background-color: rgba(255,255,255,0.2);
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    font-size: 14px;
                }
                .processing-summary {
                    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                .processing-summary h3 {
                    color: white;
                    margin-top: 0;
                    margin-bottom: 15px;
                    border-left: 4px solid rgba(255,255,255,0.5);
                    padding-left: 15px;
                }
                .summary-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                }
                .summary-item {
                    background-color: rgba(255,255,255,0.15);
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 3px solid rgba(255,255,255,0.5);
                }
                .summary-item strong {
                    color: #fff;
                    font-size: 18px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1><span class="emoji">🔊</span>AI Voice News Digest - {{ date }}</h1>
                
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-number">{{ total_articles_found or processing_stats.articles_found or news_items|length }}</span>
                        <div class="stat-label">Articles Found</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{{ total_articles_relevant or processing_stats.articles_relevant or top_articles|length }}</span>
                        <div class="stat-label">Relevant Articles</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{{ total_reddit_posts_scanned or processing_stats.reddit_scanned or 0 }}</span>
                        <div class="stat-label">Reddit Posts Scanned</div>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{{ total_reddit_posts_included or processing_stats.reddit_included or reactions|length }}</span>
                        <div class="stat-label">Reddit Posts Included</div>
                    </div>
                    {% if processing_stats and processing_stats.relevance_rate %}
                    <div class="stat-item">
                        <span class="stat-number">{{ processing_stats.relevance_rate }}%</span>
                        <div class="stat-label">Relevance Rate</div>
                    </div>
                    {% endif %}
                </div>

                {% if processing_stats %}
                <div class="processing-summary">
                    <h3>📊 Processing Summary</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <strong>{{ processing_stats.articles_found }}</strong> articles discovered from news sources
                        </div>
                        <div class="summary-item">
                            <strong>{{ processing_stats.articles_relevant }}</strong> articles relevant to voice AI ({{ processing_stats.relevance_rate }}% relevance rate)
                        </div>
                        <div class="summary-item">
                            <strong>{{ processing_stats.reddit_scanned }}</strong> Reddit posts scanned across target subreddits
                        </div>
                        <div class="summary-item">
                            <strong>{{ processing_stats.reddit_included }}</strong> Reddit posts included (voice AI related)
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if trends and trends.available %}
                <div class="trends-section">
                    <h2>📊 Trends Analysis (Last {{ trends.runs_analyzed }} Runs)</h2>
                    <p><strong>Period:</strong> {{ trends.date_range }}</p>
                    
                    <div class="trend-item">
                        <span class="trend-label">Community Sentiment</span>
                        <span class="trend-value">{{ trends.sentiment.emoji }} {{ trends.sentiment.trend.title() }}</span>
                    </div>
                    
                    <div class="trend-item">
                        <span class="trend-label">Discussion Activity</span>
                        <span class="trend-value">{{ trends.activity.emoji }} {{ trends.activity.trend.title() }}</span>
                    </div>
                    
                    <div class="trend-item">
                        <span class="trend-label">News Volume</span>
                        <span class="trend-value">{{ trends.news_volume.emoji }} {{ trends.news_volume.trend.title() }}</span>
                    </div>
                    
                    {% if trends.insights %}
                    <h3 style="color: white; border-left-color: white;">Key Insights</h3>
                    <ul class="insights-list">
                        {% for insight in trends.insights %}
                        <li>{{ insight }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </div>
                {% endif %}
                
                {% if executive_summary %}
                <div class="executive-summary">
                    <h2>📊 Executive Summary</h2>
                    {% for paragraph in executive_summary.split('\n\n') %}
                        {% if paragraph.strip() %}
                        <p>{{ paragraph.strip() }}</p>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if top_articles or news_items %}
                    <h2>🏆 Top {{ (top_articles or news_items)|length }} Voice AI Articles</h2>
                    {% for item in (top_articles or news_items) %}
                    <div class="news-item">
                        <div class="news-title">
                            <a href="{{ item.url }}" target="_blank">{{ item.title }}</a>
                        </div>
                        <div class="news-meta">
                            <strong>{{ item.source }}</strong> • {{ item.published_date[:10] }}
                        </div>
                        <div class="news-summary">
                            {{ item.summary }}
                        </div>
                    </div>
                    {% endfor %}
                    
                    {% if total_articles_found and total_articles_found > (top_articles or news_items)|length %}
                    <div class="highlight">
                        <strong>📈 Additional Coverage:</strong> Found {{ total_articles_found }} total articles today. 
                        Showing the top {{ (top_articles or news_items)|length }} most relevant to voice AI technology.
                    </div>
                    {% endif %}
                {% else %}
                    <div class="news-item">
                        <p>No voice AI news found today. The scraper will continue monitoring for updates.</p>
                    </div>
                {% endif %}
                
                {% if reactions %}
                <div class="reddit-section">
                    <h2>💬 Top Reddit Discussions with Sentiment Analysis</h2>
                    
                    {% set sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0} %}
                    {% for reaction in reactions %}
                        {% if sentiment_counts.update({reaction.sentiment: sentiment_counts[reaction.sentiment] + 1}) %}{% endif %}
                    {% endfor %}
                    
                    <div class="sentiment-summary">
                        <strong>Overall Community Sentiment:</strong> 
                        😊 {{ sentiment_counts.positive }} Positive | 
                        😟 {{ sentiment_counts.negative }} Negative | 
                        😐 {{ sentiment_counts.neutral }} Neutral
                    </div>
                    
                    {% set current_subreddit = '' %}
                    {% for reaction in reactions %}
                        {% if reaction.subreddit != current_subreddit %}
                            {% if current_subreddit != '' %}</div>{% endif %}
                            {% set current_subreddit = reaction.subreddit %}
                            <div class="reddit-subreddit">
                                <h3>r/{{ reaction.subreddit }}</h3>
                        {% endif %}
                        
                        <div class="reddit-post {{ reaction.sentiment }}">
                            <div class="reddit-meta">
                                <span>
                                    <strong>{{ reaction.score }} upvotes</strong> • {{ reaction.num_comments }} comments • {{ reaction.created_date }}
                                </span>
                                <span class="sentiment-indicator">
                                    {{ reaction.sentiment_emoji }} {{ reaction.sentiment.title() }}
                                </span>
                            </div>
                            <div class="reddit-title">
                                <a href="{{ reaction.url }}" target="_blank">{{ reaction.title }}</a>
                            </div>
                            <div class="reddit-summary">
                                "{{ reaction.summary }}"
                            </div>
                            <div class="reddit-links">
                                <a href="{{ reaction.url }}" target="_blank">💬 Discussion</a>
                                {% if reaction.external_url %}
                                <a href="{{ reaction.external_url }}" target="_blank">🌐 External Link</a>
                                {% endif %}
                            </div>
                        </div>
                        
                        {% if loop.last %}</div>{% endif %}
                    {% endfor %}
                </div>
                {% endif %}
                
                <div class="footer">
                    <p><strong>Generated by AI Voice News Scraper</strong> on {{ date }}</p>
                    <p>This digest includes trend analysis, top discussions from Reddit communities with AI-powered sentiment analysis.</p>
                    {% if trends and trends.available %}
                    <p><em>Trends based on analysis of the last {{ trends.runs_analyzed }} runs.</em></p>
                    {% endif %}
                </div>
            </div>
        </body>
        </html>
        """
        template = jinja2.Template(template_str)
    
    # Group reactions by platform for the template
    reactions_by_platform = {}
    for reaction in digest.get('reactions', []):
        platform = reaction['platform']
        if platform not in reactions_by_platform:
            reactions_by_platform[platform] = []
        reactions_by_platform[platform].append(reaction)
    
    # Render the template
    return template.render(
        date=digest['date'],
        news_items=digest.get('news_items', []),
        top_articles=digest.get('top_articles', []),
        reactions=digest.get('reactions', []),
        reactions_by_platform=reactions_by_platform,
        executive_summary=digest.get('executive_summary', ''),
        total_articles_found=digest.get('total_articles_found', 0),
        total_reddit_posts=digest.get('total_reddit_posts', 0),
        trends=digest.get('trends', {}),
        processing_stats=digest.get('processing_stats', {})
    )
