"""
Slack notifier for AI Voice News Scraper
"""
import logging
import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Slack API token
SLACK_API_TOKEN = os.getenv('SLACK_API_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '#ai-voice-news')

async def send_slack_digest(digest):
    """Send a digest to Slack"""
    if not SLACK_API_TOKEN:
        logger.error("Slack API token not configured")
        return False
    
    try:
        client = WebClient(token=SLACK_API_TOKEN)
        
        # Format the digest for Slack
        blocks = format_digest_for_slack(digest)
        
        # Send the message
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=f"AI Voice News Digest - {digest['date']}",
            blocks=blocks
        )
        
        logger.info(f"Sent Slack digest: {response['ts']}")
        return True
    except SlackApiError as e:
        logger.error(f"Error sending Slack digest: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Error sending Slack digest: {str(e)}")
        return False

def format_digest_for_slack(digest):
    """Format the digest data for Slack blocks API"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔊 AI Voice News Digest - {digest['date']}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add news items
    if digest['news_items']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📰 Latest News*"
            }
        })
        
        for item in digest['news_items']:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{item['url']}|{item['title']}>*\n{item['source']} • {item['published_date'][:10]}\n{item['summary'][:300]}..."
                }
            })
            blocks.append({
                "type": "divider"
            })
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*No new AI voice news today*"
            }
        })
    
    # Add reactions
    if digest['reactions']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💬 Community Reactions*"
            }
        })
        
        # Group reactions by platform
        platforms = {}
        for reaction in digest['reactions']:
            platform = reaction['platform']
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(reaction)
        
        # Add each platform's reactions
        for platform, reactions in platforms.items():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{platform.capitalize()}*"
                }
            })
            
            # Add top reactions (limit to 3 per platform)
            for reaction in reactions[:3]:
                if reaction['platform'] == 'reddit':
                    text = f"<{reaction['url']}|r/{reaction['subreddit']}> • {reaction['score']} points\n{reaction['content'][:150]}..."
                else:  # Twitter
                    text = f"<{reaction['url']}|Tweet> • {reaction['like_count']} likes\n{reaction['content'][:150]}..."
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                })
            
            blocks.append({
                "type": "divider"
            })
    
    return blocks
