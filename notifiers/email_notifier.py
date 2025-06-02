"""
Email notifier for AI Voice News Scraper - Enhanced with executive summary
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

async def send_email_digest(digest):
    """Send a digest via email with executive summary"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]):
        logger.error("Email configuration not complete")
        return False
    
    try:
        # Generate executive summary
        logger.info("Generating executive summary...")
        executive_summary = await generate_executive_summary(
            digest['news_items'], 
            digest.get('reactions', [])
        )
        
        # Select top 5 articles
        top_articles = select_top_articles(digest['news_items'], limit=5)
        
        # Create enhanced digest
        enhanced_digest = {
            **digest,
            'executive_summary': executive_summary,
            'top_articles': top_articles,
            'total_articles_found': len(digest['news_items']),
            'total_reddit_posts': len(digest.get('reactions', []))
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
        
        logger.info(f"Sent enhanced email digest to {EMAIL_TO}")
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
        # If template doesn't exist, use an enhanced inline template
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
                }
                h2 {
                    color: #3498db;
                    margin-top: 30px;
                    margin-bottom: 20px;
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
                .stats {
                    background-color: #ecf0f1;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                }
                .stat-item {
                    margin: 5px;
                }
                .stat-number {
                    font-size: 24px;
                    font-weight: bold;
                    color: #3498db;
                }
                .news-item {
                    margin-bottom: 30px;
                    border-left: 4px solid #3498db;
                    padding-left: 20px;
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 8px 8px 0;
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
                }
                .news-summary {
                    font-size: 16px;
                    line-height: 1.6;
                }
                .reddit-section {
                    background-color: #ff4500;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 30px;
                }
                .reddit-section h2 {
                    color: white;
                    margin-top: 0;
                }
                .reddit-post {
                    background-color: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1><span class="emoji">🔊</span>AI Voice News Digest - {{ date }}</h1>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">{{ total_articles_found }}</div>
                        <div>Articles Found</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ top_articles|length }}</div>
                        <div>Top Articles</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ total_reddit_posts }}</div>
                        <div>Reddit Posts</div>
                    </div>
                </div>
                
                {% if executive_summary %}
                <div class="executive-summary">
                    <h2>📊 Executive Summary</h2>
                    <p>{{ executive_summary|replace('\n', '</p><p>')|safe }}</p>
                </div>
                {% endif %}
                
                {% if top_articles %}
                    <h2>🏆 Top 5 Voice AI Articles</h2>
                    {% for item in top_articles %}
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
                {% else %}
                    <div class="news-item">
                        <p>No voice AI news found today. The scraper will continue monitoring for updates.</p>
                    </div>
                {% endif %}
                
                {% if reactions %}
                <div class="reddit-section">
                    <h2>💬 Community Discussions (Top 5)</h2>
                    {% for reaction in reactions[:5] %}
                    <div class="reddit-post">
                        <strong>r/{{ reaction.subreddit }}</strong> • {{ reaction.score }} points<br>
                        <a href="{{ reaction.url }}" target="_blank" style="color: white;">
                            {{ reaction.title or reaction.content[:100] }}...
                        </a>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                <div class="footer">
                    <p>Generated by AI Voice News Scraper on {{ date }}</p>
                    <p>This digest focuses specifically on voice AI technology news and community insights.</p>
                    {% if total_articles_found > 5 %}
                    <p><em>Showing top 5 of {{ total_articles_found }} articles found today.</em></p>
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
        total_reddit_posts=digest.get('total_reddit_posts', 0)
    )
