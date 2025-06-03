"""
Email notifier for AI Voice News Scraper - Fixed multiple recipients
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

# Email configuration with multiple recipient support
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')

# Support multiple recipients
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_CC = os.getenv('EMAIL_CC', '')  # Optional CC recipients
EMAIL_BCC = os.getenv('EMAIL_BCC', '')  # Optional BCC recipients

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Jinja2 template environment
template_loader = jinja2.FileSystemLoader(searchpath="./templates")
template_env = jinja2.Environment(loader=template_loader)

def parse_email_list(email_string: str) -> list:
    """Parse comma-separated email addresses with better validation"""
    if not email_string:
        return []
    
    emails = []
    # Split by comma and clean up each email
    for email in email_string.split(','):
        email = email.strip()
        # Basic email validation
        if email and '@' in email and '.' in email.split('@')[1]:
            emails.append(email)
            logger.debug(f"Added email: {email}")
        elif email:
            logger.warning(f"Invalid email format skipped: {email}")
    
    return emails

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
    """Send a digest via email with FIXED multiple recipient support"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM]):
        logger.error("Email configuration not complete")
        return False
    
    # Parse recipient lists with detailed logging
    logger.info(f"Raw EMAIL_TO: '{EMAIL_TO}'")
    logger.info(f"Raw EMAIL_CC: '{EMAIL_CC}'")
    logger.info(f"Raw EMAIL_BCC: '{EMAIL_BCC}'")
    
    to_emails = parse_email_list(EMAIL_TO)
    cc_emails = parse_email_list(EMAIL_CC)
    bcc_emails = parse_email_list(EMAIL_BCC)
    
    logger.info(f"Parsed TO emails: {to_emails}")
    logger.info(f"Parsed CC emails: {cc_emails}")
    logger.info(f"Parsed BCC emails: {bcc_emails}")
    
    if not to_emails:
        logger.error("No valid TO email addresses configured")
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
        
        # Create HTML content
        html_content = format_digest_for_email(enhanced_digest)
        
        # Combine all recipients for actual sending
        all_recipients = to_emails + cc_emails + bcc_emails
        logger.info(f"Total recipients for sending: {len(all_recipients)}")
        logger.info(f"All recipients: {all_recipients}")
        
        # Send email using SMTP with proper recipient handling
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Create message for each batch to ensure proper delivery
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔊 AI Voice News Digest - {digest['date']}"
            msg['From'] = EMAIL_FROM
            
            # Set headers properly
            if to_emails:
                msg['To'] = ', '.join(to_emails)
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            # Note: BCC recipients are not added to headers (that's the point of BCC)
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send to ALL recipients (TO + CC + BCC)
            logger.info(f"Sending email to {len(all_recipients)} recipients...")
            
            # Use sendmail with explicit recipient list
            text = msg.as_string()
            server.sendmail(EMAIL_FROM, all_recipients, text)
            
            logger.info("✅ Email sent successfully!")
        
        # Log detailed recipient information
        logger.info(f"📧 Email delivery summary:")
        logger.info(f"   TO recipients ({len(to_emails)}): {', '.join(to_emails)}")
        if cc_emails:
            logger.info(f"   CC recipients ({len(cc_emails)}): {', '.join(cc_emails)}")
        if bcc_emails:
            logger.info(f"   BCC recipients ({len(bcc_emails)}): {', '.join(bcc_emails)}")
        logger.info(f"   Total sent to: {len(all_recipients)} recipients")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email digest: {str(e)}")
        logger.error(f"Failed recipients: {all_recipients if 'all_recipients' in locals() else 'Unknown'}")
        return False

def format_digest_for_email(digest):
    """Format the enhanced digest data for email HTML"""
    try:
        # Try to load the template
        template = template_env.get_template('email_digest.html')
        
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
        
    except jinja2.exceptions.TemplateNotFound:
        logger.warning("Email template not found, using fallback")
        return f"""
        <html>
        <body>
        <h1>AI Voice News Digest - {digest['date']}</h1>
        <p>Found {len(digest.get('news_items', []))} articles and {len(digest.get('reactions', []))} Reddit discussions.</p>
        <p>Template file missing - please check templates/email_digest.html</p>
        </body>
        </html>
        """
