"""
Database manager for AI Voice News Scraper
"""
import logging
import os
import json
from datetime import datetime, timedelta
import uuid
from pathlib import Path

from ai_voice_scraper.config import MONGODB_URI, DB_NAME

logger = logging.getLogger(__name__)

# Global variable for file storage fallback
USE_FILE_STORAGE = False

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
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
    return []

def save_file_data(filename, data):
    """Save data to JSON file"""
    filepath = Path('data') / f"{filename}.json"
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
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
        
        # Check if we should use file storage
        use_files = USE_FILE_STORAGE or not await test_mongodb_connection()
        
        if use_files:
            # Use file storage
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
        else:
            # Use MongoDB
            existing = await news_collection.find_one({'url': news_item['url']})
            if existing:
                await news_collection.update_one(
                    {'_id': existing['_id']},
                    {'$set': news_item}
                )
                logger.info(f"Updated existing news item: {news_item['title']}")
                return existing['_id']
            else:
                result = await news_collection.insert_one(news_item)
                logger.info(f"Stored new news item: {news_item['title']}")
                return result.inserted_id
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
        
        # Check if we should use file storage
        use_files = USE_FILE_STORAGE or not await test_mongodb_connection()
        
        if use_files:
            # Use file storage
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
        else:
            # Use MongoDB
            if 'url' in reaction:
                existing = await reactions_collection.find_one({'url': reaction['url']})
            else:
                existing = await reactions_collection.find_one({'content': reaction['content']})
            
            if existing:
                await reactions_collection.update_one(
                    {'_id': existing['_id']},
                    {'$set': reaction}
                )
                logger.info(f"Updated existing reaction")
                return existing['_id']
            else:
                result = await reactions_collection.insert_one(reaction)
                logger.info(f"Stored new reaction")
                return result.inserted_id
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
        
        # Check if we should use file storage
        use_files = USE_FILE_STORAGE or not await test_mongodb_connection()
        
        if use_files:
            # Use file storage
            runs = load_file_data('runs')
            runs.append(run_summary)
            
            # Keep only last 10 runs
            runs = runs[-10:]
            save_file_data('runs', runs)
            logger.info(f"Stored run summary for {run_summary['date']}")
            return run_summary['_id']
        else:
            # Use MongoDB
            result = await runs_collection.insert_one(run_summary)
            
            # Clean up old runs (keep last 10)
            old_runs = await runs_collection.find().sort('timestamp', -1).skip(10).to_list(None)
            if old_runs:
                old_ids = [run['_id'] for run in old_runs]
                await runs_collection.delete_many({'_id': {'$in': old_ids}})
            
            logger.info(f"Stored run summary for {run_summary['date']}")
            return result.inserted_id
    except Exception as e:
        logger.error(f"Error storing run summary: {str(e)}")
        return None

async def get_recent_runs(limit=3):
    """Get the last N runs for trend analysis"""
    try:
        # Check if we should use file storage
        use_files = USE_FILE_STORAGE or not await test_mongodb_connection()
        
        if use_files:
            # Use file storage
            runs = load_file_data('runs')
            # Sort by timestamp descending and take the last N
            runs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            recent_runs = runs[:limit]
            logger.info(f"Retrieved {len(recent_runs)} recent runs from file")
            return recent_runs
        else:
            # Use MongoDB
            cursor = runs_collection.find().sort('timestamp', -1).limit(limit)
            runs = await cursor.to_list(length=limit)
            logger.info(f"Retrieved {len(runs)} recent runs from MongoDB")
            return runs
    except Exception as e:
        logger.error(f"Error retrieving recent runs: {str(e)}")
        return []

async def get_recent_news(days=1):
    """Get recent news items from the database or file"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Check if we should use file storage
        use_files = USE_FILE_STORAGE or not await test_mongodb_connection()
        
        if use_files:
            # Use file storage
            news_items = load_file_data('news_items')
            recent_items = []
            
            for item in news_items:
                try:
                    item_date = datetime.fromisoformat(item.
