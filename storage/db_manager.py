"""
Database manager for AI Voice News Scraper - Fixed version with fallback
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

# Fallback to file storage if MongoDB is not available
USE_FILE_STORAGE = False

try:
    import motor.motor_asyncio
    # Initialize MongoDB client
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    # Collections
    news_collection = db['news_items']
    reactions_collection = db['reactions']
except Exception as e:
    logger.warning(f"MongoDB not available, using file storage: {str(e)}")
    USE_FILE_STORAGE = True
    # Create data directory
    Path('data').mkdir(exist_ok=True)

async def test_mongodb_connection():
    """Test if MongoDB is available"""
    if USE_FILE_STORAGE:
        return False
    
    try:
        # Test connection
        await client.admin.command('ping')
        return True
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {str(e)}")
        global USE_FILE_STORAGE
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
        
        if USE_FILE_STORAGE or not await test_mongodb_connection():
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
        
        if USE_FILE_STORAGE or not await test_mongodb_connection():
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

async def get_recent_news(days=1):
    """Get recent news items from the database or file"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if USE_FILE_STORAGE or not await test_mongodb_connection():
            # Use file storage
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
        else:
            # Use MongoDB
            cursor = news_collection.find({
                'published_date': {'$gte': cutoff_date.isoformat()}
            })
            
            news_items = await cursor.to_list(length=100)
            logger.info(f"Retrieved {len(news_items)} recent news items from MongoDB")
            return news_items
    except Exception as e:
        logger.error(f"Error retrieving recent news: {str(e)}")
        return []

async def get_reactions_for_news(news_id):
    """Get reactions for a specific news item"""
    try:
        if USE_FILE_STORAGE or not await test_mongodb_connection():
            # Use file storage
            reactions = load_file_data('reactions')
            related_reactions = [r for r in reactions if news_id in r.get('related_news', [])]
            return related_reactions
        else:
            # Use MongoDB
            cursor = reactions_collection.find({
                'related_news': news_id
            })
            reactions = await cursor.to_list(length=100)
            return reactions
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
