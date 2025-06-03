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
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from processors.trends_analyzer import analyze_current_trends
from storage.db_manager import store_run_summary
import time

# Load environment variables with override
load_dotenv(override=True)

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_CC = os.getenv('EMAIL_CC', '')
EMAIL_BCC = os.getenv('EMAIL_BCC', '')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Jinja2 template environment
template_loader = jinja2.FileSystemLoader(searchpath="./templates")
template_env = jinja2.Environment(loader=template_loader)

def parse_email_list(email_string: str) -> list:
    """Parse and validate email addresses"""
    if not email_string:
        return []
    
    emails = []
    for email in email_string.split(','):
        email = email.strip()
        if email and '@' in email and '.' in email:
            emails.append(email)
    
    return emails

def get_all_recipients():
    """Get all email recipients - treats all as TO recipients"""
    # Force reload environment variables
    load_dotenv(override=True)
    
    to_emails = parse_email_list(os.getenv('EMAIL_TO', ''))
    cc_emails = parse_email_list(os.getenv('EMAIL_CC', ''))
    bcc_emails = parse_email_list(os.getenv('EMAIL_BCC', ''))
    
    # Treat ALL emails as TO recipients to avoid Gmail CC issues
    all_recipients = to_emails + cc_emails + bcc_emails
    
    logger.info(f"📧 Email recipients (treating all as TO):")
    logger.info(f"  Original TO: {to_emails}")
    logger.info(f"  Original CC: {cc_emails}")
    logger.info(f"  Original BCC: {bcc_emails}")
    logger.info(f"  FINAL TO LIST: {all_recipients}")
    
    return all_recipients

async def send_email_digest(digest):
    """Send email digest with guaranteed delivery"""
    logger.info("🚀 Starting email digest send...")
    
    # Force reload environment variables
    load_dotenv(override=True)
    
    # Get fresh email configuration
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM')
    
    if not all([smtp_server, smtp_username, smtp_password, email_from]):
        logger.error("❌ Email configuration incomplete")
        return False
    
    # Get all recipients (treating all as TO to avoid CC issues)
    all_recipients = get_all_recipients()
    
    if not all_recipients:
        logger.error("❌ No valid email recipients found")
        return False
    
    logger.info(f"📧 Will send to {len(all_recipients)} recipients (all as TO)")
    
    try:
        # Build enhanced digest
        enhanced_digest = await build_enhanced_digest(digest)
        html_content = format_digest_for_email(enhanced_digest)
        
        # Strategy 1: Send to all as TO recipients (avoids Gmail CC issues)
        success = await send_all_as_to_recipients(
            smtp_server, smtp_port, smtp_username, smtp_password, email_from,
            all_recipients, digest['date'], html_content
        )
        
        if success:
            logger.info(f"✅ Email sent successfully to all {len(all_recipients)} recipients!")
            return True
        
        # Strategy 2: If that fails, send individually
        logger.warning("Bulk send failed, trying individual sends...")
        success = await send_individually(
            smtp_server, smtp_port, smtp_username, smtp_password, email_from,
            all_recipients, digest['date'], html_content
        )
        
        return success
            
    except Exception as e:
        logger.error(f"❌ Email digest failed: {e}")
        return False

async def send_all_as_to_recipients(smtp_server, smtp_port, smtp_username, smtp_password, 
                                  email_from, all_recipients, date, html_content):
    """Send to all recipients as TO (avoids Gmail CC delivery issues)"""
    
    logger.info(f"📧 Sending to all {len(all_recipients)} as TO recipients...")
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔊 AI Voice News Digest - {date}"
            msg['From'] = email_from
            msg['To'] = ', '.join(all_recipients)  # All as TO recipients
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send to all recipients
            failed = server.sendmail(email_from, all_recipients, msg.as_string())
            
            if not failed:
                logger.info(f"✅ Successfully sent to all {len(all_recipients)} recipients as TO!")
                return True
            else:
                logger.warning(f"⚠️ Some recipients failed: {failed}")
                return False
    
    except Exception as e:
        logger.error(f"❌ Bulk TO send failed: {e}")
        return False

async def send_individually(smtp_server, smtp_port, smtp_username, smtp_password, 
                          email_from, all_recipients, date, html_content):
    """Send individually to each recipient as fallback"""
    
    logger.info(f"📧 Sending individually to {len(all_recipients)} recipients...")
    successful_sends = 0
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            
            for i, email in enumerate(all_recipients, 1):
                try:
                    logger.info(f"  Sending {i}/{len(all_recipients)} to: {email}")
                    
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = f"🔊 AI Voice News Digest - {date}"
                    msg['From'] = email_from
                    msg['To'] = email
                    msg.attach(MIMEText(html_content, 'html'))
                    
                    result = server.sendmail(email_from, [email], msg.as_string())
                    
                    if not result:
                        logger.info(f"    ✅ Success: {email}")
                        successful_sends += 1
                    else:
                        logger.error(f"    ❌ Failed: {email} - {result}")
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"    ❌ Error sending to {email}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Individual send connection failed: {e}")
        return False
    
    logger.info(f"📊 Individual send results: {successful_sends}/{len(all_recipients)} successful")
    return successful_sends > 0

async def build_enhanced_digest(digest):
    """Build enhanced digest with all features"""
    try:
        # Calculate sentiment summary
        sentiment_summary, subreddit_activity = calculate_sentiment_summary(digest.get('reactions', []))
        
        # Prepare run data
        current_run_data = {
            'articles_found': len(digest.get('news_items', [])),
            'articles_processed': len(digest.get('news_items', [])),
            'reddit_posts': len(digest.get('reactions', [])),
            'sentiment_summary': sentiment_summary,
            'subreddit_activity': subreddit_activity
        }
        
        # Analyze trends
        trends_data = await analyze_current_trends(current_run_data)
        await store_run_summary(current_run_data)
        
        # Generate executive summary
        executive_summary = await generate_executive_summary(
            digest['news_items'], 
            digest.get('reactions', [])
        )
        
        # Select top articles
        top_articles = select_top_articles(digest['news_items'], limit=5)
        
        return {
            **digest,
            'executive_summary': executive_summary,
            'top_articles': top_articles,
            'total_articles_found': len(digest['news_items']),
            'total_articles_relevant': len([item for item in digest['news_items'] if item.get('summary')]),
            'total_reddit_posts_scanned': digest.get('total_reddit_scanned', 0),
            'total_reddit_posts_included': len(digest.get('reactions', [])),
            'trends': trends_data
        }
    except Exception as e:
        logger.error(f"Error building enhanced digest: {e}")
        return digest

async def generate_executive_summary(news_items, reactions):
    """Generate executive summary"""
    if not OPENAI_API_KEY:
        return "Executive summary not available (OpenAI API key not configured)"
    
    try:
        news_content = []
        for item in news_items[:10]:
            news_content.append(f"• {item['title']} ({item['source']}): {item.get('summary', '')[:200]}")
        
        reddit_content = []
        for reaction in reactions[:10]:
            reddit_content.append(f"• r/{reaction.get('subreddit', 'unknown')}: {reaction.get('title', reaction.get('content', ''))[:150]}")
        
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
        
        llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo")
        
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
    """Select top articles"""
    if not news_items:
        return []
    
    def relevance_score(item):
        score = 0
        title_lower = item.get('title', '').lower()
        summary_lower = item.get('summary', '').lower()
        
        high_value_keywords = [
            'elevenlabs', 'openai voice', 'breakthrough', 'launch', 'release',
            'funding', 'acquisition', 'partnership', 'new model', 'api'
        ]
        
        for keyword in high_value_keywords:
            if keyword in title_lower or keyword in summary_lower:
                score += 10
        
        medium_value_keywords = [
            'voice ai', 'text-to-speech', 'speech synthesis', 'voice cloning',
            'ai voice', 'neural voice', 'voice generation'
        ]
        
        for keyword in medium_value_keywords:
            if keyword in title_lower:
                score += 5
            elif keyword in summary_lower:
                score += 3
        
        if 'today' in summary_lower or 'announced' in summary_lower:
            score += 5
        
        return score
    
    sorted_items = sorted(news_items, key=relevance_score, reverse=True)
    return sorted_items[:limit]

def calculate_sentiment_summary(reactions):
    """Calculate sentiment summary"""
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    subreddit_activity = {}
    
    for reaction in reactions:
        sentiment = reaction.get('sentiment', 'neutral')
        sentiment_counts[sentiment] += 1
        
        subreddit = reaction.get('subreddit', 'unknown')
        subreddit_activity[subreddit] = subreddit_activity.get(subreddit, 0) + 1
    
    return sentiment_counts, subreddit_activity

def format_digest_for_email(digest):
    """Format digest for email"""
    try:
        template = template_env.get_template('email_digest.html')
        
        reactions_by_platform = {}
        for reaction in digest.get('reactions', []):
            platform = reaction['platform']
            if platform not in reactions_by_platform:
                reactions_by_platform[platform] = []
            reactions_by_platform[platform].append(reaction)
        
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
        
    except jinja2.exceptions.TemplateNotFound:
        logger.warning("Email template not found, using fallback")
        return f"""
        <html>
        <body>
        <h1>AI Voice News Digest - {digest['date']}</h1>
        <p>Found {len(digest.get('news_items', []))} articles and {len(digest.get('reactions', []))} Reddit discussions.</p>
        </body>
        </html>
        """
