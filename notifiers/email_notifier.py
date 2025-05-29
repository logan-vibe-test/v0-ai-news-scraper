"""
Email notifier for AI Voice News Scraper
"""
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import jinja2

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

# Jinja2 template environment
template_loader = jinja2.FileSystemLoader(searchpath="./templates")
template_env = jinja2.Environment(loader=template_loader)

async def send_email_digest(digest):
    """Send a digest via email"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]):
        logger.error("Email configuration not complete")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"AI Voice News Digest - {digest['date']}"
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        # Create HTML content
        html_content = format_digest_for_email(digest)
        
        # Attach parts
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Sent email digest to {EMAIL_TO}")
        return True
    except Exception as e:
        logger.error(f"Error sending email digest: {str(e)}")
        return False

def format_digest_for_email(digest):
    """Format the digest data for email HTML"""
    try:
        # Try to load the template
        template = template_env.get_template('email_digest.html')
    except jinja2.exceptions.TemplateNotFound:
        # If template doesn't exist, use a simple inline template
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                .news-item { margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
                .news-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
                .news-meta { font-size: 14px; color: #7f8c8d; margin-bottom: 10px; }
                .news-summary { font-size: 16px; }
                .reaction { margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }
                .reaction-meta { font-size: 14px; color: #7f8c8d; margin-bottom: 5px; }
                .reaction-content { font-size: 15px; }
            </style>
        </head>
        <body>
            <h1>🔊 AI Voice News Digest - {{ date }}</h1>
            
            <h2>📰 Latest News</h2>
            {% if news_items %}
                {% for item in news_items %}
                <div class="news-item">
                    <div class="news-title"><a href="{{ item.url }}">{{ item.title }}</a></div>
                    <div class="news-meta">{{ item.source }} • {{ item.published_date[:10] }}</div>
                    <div class="news-summary">{{ item.summary[:300] }}...</div>
                </div>
                {% endfor %}
            {% else %}
                <p>No new AI voice news today</p>
            {% endif %}
            
            <h2>💬 Community Reactions</h2>
            {% if reactions %}
                {% for platform, platform_reactions in reactions_by_platform.items() %}
                <h3>{{ platform|capitalize }}</h3>
                {% for reaction in platform_reactions[:3] %}
                <div class="reaction">
                    {% if reaction.platform == 'reddit' %}
                    <div class="reaction-meta">
                        <a href="{{ reaction.url }}">r/{{ reaction.subreddit }}</a> • {{ reaction.score }} points
                    </div>
                    {% else %}
                    <div class="reaction-meta">
                        <a href="{{ reaction.url }}">Tweet</a> • {{ reaction.like_count }} likes
                    </div>
                    {% endif %}
                    <div class="reaction-content">{{ reaction.content[:150] }}...</div>
                </div>
                {% endfor %}
                {% endfor %}
            {% else %}
                <p>No community reactions today</p>
            {% endif %}
        </body>
        </html>
        """
        template = jinja2.Template(template_str)
    
    # Group reactions by platform
    reactions_by_platform = {}
    for reaction in digest['reactions']:
        platform = reaction['platform']
        if platform not in reactions_by_platform:
            reactions_by_platform[platform] = []
        reactions_by_platform[platform].append(reaction)
    
    # Render the template
    return template.render(
        date=digest['date'],
        news_items=digest['news_items'],
        reactions=digest['reactions'],
        reactions_by_platform=reactions_by_platform
    )
