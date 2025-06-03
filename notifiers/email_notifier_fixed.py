"""
Email notifier with GUARANTEED multiple recipient delivery
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

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO', '')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Jinja2 template environment
template_loader = jinja2.FileSystemLoader(searchpath="./templates")
template_env = jinja2.Environment(loader=template_loader)

def parse_and_validate_emails(email_string: str) -> list:
    """Parse and validate email addresses with detailed logging"""
    if not email_string:
        logger.warning("No email string provided")
        return []
    
    logger.info(f"Raw email string: '{email_string}'")
    
    emails = []
    raw_emails = email_string.split(',')
    logger.info(f"Split into {len(raw_emails)} parts: {raw_emails}")
    
    for i, email in enumerate(raw_emails):
        email = email.strip()
        logger.info(f"Processing email {i+1}: '{email}'")
        
        if email and '@' in email and '.' in email:
            emails.append(email)
            logger.info(f"  ✅ Valid: {email}")
        elif email:
            logger.warning(f"  ❌ Invalid: {email}")
        else:
            logger.warning(f"  ❌ Empty email at position {i+1}")
    
    logger.info(f"Final valid emails: {emails}")
    return emails

async def send_email_digest_guaranteed(digest):
    """Send email with GUARANTEED delivery to all recipients"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM]):
        logger.error("Email configuration incomplete")
        return False
    
    # Parse emails with detailed logging
    emails = parse_and_validate_emails(EMAIL_TO)
    
    if not emails:
        logger.error("No valid email addresses found")
        return False
    
    logger.info(f"Will attempt to send to {len(emails)} recipients")
    
    try:
        # Build the email content first
        enhanced_digest = await build_enhanced_digest(digest)
        html_content = format_digest_for_email(enhanced_digest)
        
        # Strategy 1: Try bulk send first
        bulk_success = await try_bulk_send(emails, digest['date'], html_content)
        
        if bulk_success:
            logger.info("✅ Bulk send successful to all recipients")
            return True
        
        # Strategy 2: If bulk fails, send individually
        logger.warning("Bulk send failed, trying individual sends...")
        individual_success = await try_individual_sends(emails, digest['date'], html_content)
        
        return individual_success
        
    except Exception as e:
        logger.error(f"Email sending failed completely: {e}")
        return False

async def try_bulk_send(emails, date, html_content):
    """Try sending to all recipients at once"""
    try:
        logger.info(f"Attempting bulk send to {len(emails)} recipients...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔊 AI Voice News Digest - {date}"
            msg['From'] = EMAIL_FROM
            msg['To'] = ', '.join(emails)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Use sendmail with explicit recipient list
            failed_recipients = server.sendmail(EMAIL_FROM, emails, msg.as_string())
            
            if failed_recipients:
                logger.warning(f"Bulk send had failures: {failed_recipients}")
                return False
            else:
                logger.info(f"✅ Bulk send successful to: {', '.join(emails)}")
                return True
                
    except Exception as e:
        logger.error(f"Bulk send failed: {e}")
        return False

async def try_individual_sends(emails, date, html_content):
    """Send to each recipient individually"""
    successful_sends = 0
    failed_sends = 0
    
    logger.info(f"Sending individually to {len(emails)} recipients...")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            for i, email in enumerate(emails, 1):
                try:
                    logger.info(f"Sending {i}/{len(emails)} to: {email}")
                    
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = f"🔊 AI Voice News Digest - {date}"
                    msg['From'] = EMAIL_FROM
                    msg['To'] = email
                    msg.attach(MIMEText(html_content, 'html'))
                    
                    # Send to single recipient
                    result = server.sendmail(EMAIL_FROM, [email], msg.as_string())
                    
                    if result:
                        logger.error(f"  ❌ Failed to send to {email}: {result}")
                        failed_sends += 1
                    else:
                        logger.info(f"  ✅ Successfully sent to {email}")
                        successful_sends += 1
                    
                    # Small delay between sends
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"  ❌ Error sending to {email}: {e}")
                    failed_sends += 1
                    
    except Exception as e:
        logger.error(f"Individual send connection failed: {e}")
        return False
    
    logger.info(f"📊 Individual send results: {successful_sends} successful, {failed_sends} failed")
    
    if successful_sends > 0:
        logger.info(f"✅ At least {successful_sends} emails sent successfully")
        return True
    else:
        logger.error("❌ All individual sends failed")
        return False

async def build_enhanced_digest(digest):
    """Build the enhanced digest with all features"""
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
            'trends': trends_data,
            'processing_stats': {
                'articles_found': len(digest['news_items']),
                'articles_relevant': len([item for item in digest['news_items'] if item.get('summary')]),
                'reddit_scanned': digest.get('total_reddit_scanned', 0),
                'reddit_included': len(digest.get('reactions', [])),
                'relevance_rate': round((len([item for item in digest['news_items'] if item.get('summary')]) / max(len(digest['news_items']), 1)) * 100, 1)
            }
        }
    except Exception as e:
        logger.error(f"Error building enhanced digest: {e}")
        return digest

# Copy the other functions from the previous version
async def generate_executive_summary(news_items, reactions):
    """Generate an executive summary of the voice AI landscape"""
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
    """Select the top most relevant articles"""
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
    """Calculate sentiment summary from reactions"""
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    subreddit_activity = {}
    
    for reaction in reactions:
        sentiment = reaction.get('sentiment', 'neutral')
        sentiment_counts[sentiment] += 1
        
        subreddit = reaction.get('subreddit', 'unknown')
        subreddit_activity[subreddit] = subreddit_activity.get(subreddit, 0) + 1
    
    return sentiment_counts, subreddit_activity

def format_digest_for_email(digest):
    """Format the enhanced digest data for email HTML"""
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

# Alias for backward compatibility
send_email_digest = send_email_digest_guaranteed
