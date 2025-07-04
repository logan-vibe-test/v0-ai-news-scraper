"""
Database manager for AI Voice News Scraper - Enhanced with trends tracking
"""
import logging
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid
from pathlib import Path

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB connection string
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'ai_voice_news')

# Global variable for file storage fallback
USE_FILE_STORAGE = True  # Default to file storage

try:
    import motor.motor_asyncio
    # Initialize MongoDB client
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    # Collections
    news_collection = db['news_items']
    reactions_collection = db['reactions']
    runs_collection = db['runs']  # New collection for tracking runs
    logger.info("MongoDB client initialized")
    USE_FILE_STORAGE = False  # Use MongoDB if available
except Exception as e:
    logger.warning(f"MongoDB not available, using file storage: {str(e)}")
    USE_FILE_STORAGE = True
    client = None
    db = None
    news_collection = None
    reactions_collection = None
    runs_collection = None

# Create data directory for file storage
Path('data').mkdir(exist_ok=True)

async def test_mongodb_connection():
    """Test if MongoDB is available"""
    global USE_FILE_STORAGE
    
    if USE_FILE_STORAGE or client is None:
        return False
    
    try:
        # Test connection
        await client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return True
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {str(e)}")
        USE_FILE_STORAGE = True
        return False

def load_file_data(filename):
    """Load data from JSON file"""
    filepath = Path('data') / f"{filename}.json"
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
    return []

def save_file_data(filename, data):
    """Save data to JSON file"""
    filepath = Path('data') / f"{filename}.json"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {str(e)}")
        return False

async def store_news_item(news_item):
    """Store a news item in the database or file"""
    try:
        # Add unique ID and timestamp
        if '_id' not in news_item:
            news_item['_id'] = str(uuid.uuid4())
        
        news_item['stored_at'] = datetime.now().isoformat()
        
        # Always use file storage for now (more reliable)
        news_items = load_file_data('news_items')
        
        # Check if item exists
        existing_index = None
        for i, item in enumerate(news_items):
            if item.get('url') == news_item['url']:
                existing_index = i
                break
        
        if existing_index is not None:
            news_items[existing_index] = news_item
            logger.info(f"Updated existing news item: {news_item['title']}")
        else:
            news_items.append(news_item)
            logger.info(f"Stored new news item: {news_item['title']}")
        
        save_file_data('news_items', news_items)
        return news_item['_id']
        
    except Exception as e:
        logger.error(f"Error storing news item: {str(e)}")
        return None

async def store_reaction(reaction):
    """Store a reaction in the database or file"""
    try:
        # Add unique ID and timestamp
        if '_id' not in reaction:
            reaction['_id'] = str(uuid.uuid4())
        
        reaction['stored_at'] = datetime.now().isoformat()
        
        # Always use file storage for now
        reactions = load_file_data('reactions')
        
        # Check if reaction exists
        existing_index = None
        for i, item in enumerate(reactions):
            if item.get('url') == reaction.get('url') or item.get('content') == reaction.get('content'):
                existing_index = i
                break
        
        if existing_index is not None:
            reactions[existing_index] = reaction
            logger.info(f"Updated existing reaction")
        else:
            reactions.append(reaction)
            logger.info(f"Stored new reaction")
        
        save_file_data('reactions', reactions)
        return reaction['_id']
        
    except Exception as e:
        logger.error(f"Error storing reaction: {str(e)}")
        return None

async def store_run_summary(run_data):
    """Store a summary of this run for trend analysis"""
    try:
        run_summary = {
            '_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'articles_found': run_data.get('articles_found', 0),
            'articles_processed': run_data.get('articles_processed', 0),
            'reddit_posts': run_data.get('reddit_posts', 0),
            'sentiment_summary': run_data.get('sentiment_summary', {}),
            'top_keywords': run_data.get('top_keywords', []),
            'subreddit_activity': run_data.get('subreddit_activity', {})
        }
        
        # Always use file storage for now
        runs = load_file_data('runs')
        runs.append(run_summary)
        
        # Keep only last 10 runs
        runs = runs[-10:]
        save_file_data('runs', runs)
        logger.info(f"Stored run summary for {run_summary['date']}")
        return run_summary['_id']
        
    except Exception as e:
        logger.error(f"Error storing run summary: {str(e)}")
        return None

async def get_recent_runs(limit=3):
    """Get the last N runs for trend analysis"""
    try:
        runs = load_file_data('runs')
        # Sort by timestamp descending and take the last N
        runs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        recent_runs = runs[:limit]
        logger.info(f"Retrieved {len(recent_runs)} recent runs from file")
        return recent_runs
    except Exception as e:
        logger.error(f"Error retrieving recent runs: {str(e)}")
        return []

async def get_recent_news(days=1):
    """Get recent news items from the database or file"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        news_items = load_file_data('news_items')
        recent_items = []
        
        for item in news_items:
            try:
                item_date = datetime.fromisoformat(item.get('published_date', ''))
                if item_date >= cutoff_date:
                    recent_items.append(item)
            except:
                # If date parsing fails, include the item
                recent_items.append(item)
        
        logger.info(f"Retrieved {len(recent_items)} recent news items from file")
        return recent_items
    except Exception as e:
        logger.error(f"Error retrieving recent news: {str(e)}")
        return []

async def get_reactions_for_news(news_id):
    """Get reactions for a specific news item"""
    try:
        reactions = load_file_data('reactions')
        related_reactions = [r for r in reactions if news_id in r.get('related_news', [])]
        return related_reactions
    except Exception as e:
        logger.error(f"Error retrieving reactions: {str(e)}")
        return []

async def get_daily_digest():
    """Get data for daily digest"""
    try:
        # Get news from the last 24 hours
        news_items = await get_recent_news(days=1)
        
        # Get reactions for these news items
        digest_data = []
        for news in news_items:
            reactions = await get_reactions_for_news(news['_id'])
            digest_data.append({
                'news': news,
                'reactions': reactions
            })
        
        return digest_data
    except Exception as e:
        logger.error(f"Error creating digest: {str(e)}")
        return []
