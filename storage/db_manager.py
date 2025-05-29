"""
Database manager for AI Voice News Scraper
"""
import logging
import os
import motor.motor_asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB connection string
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'ai_voice_news')

# Initialize MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
news_collection = db['news_items']
reactions_collection = db['reactions']

async def store_news_item(news_item):
    """Store a news item in the database"""
    try:
        # Add unique ID and timestamp
        if '_id' not in news_item:
            news_item['_id'] = str(uuid.uuid4())
        
        news_item['stored_at'] = datetime.now().isoformat()
        
        # Check if the item already exists (by URL)
        existing = await news_collection.find_one({'url': news_item['url']})
        if existing:
            # Update existing item
            await news_collection.update_one(
                {'_id': existing['_id']},
                {'$set': news_item}
            )
            logger.info(f"Updated existing news item: {news_item['title']}")
            return existing['_id']
        else:
            # Insert new item
            result = await news_collection.insert_one(news_item)
            logger.info(f"Stored new news item: {news_item['title']}")
            return result.inserted_id
    except Exception as e:
        logger.error(f"Error storing news item: {str(e)}")
        return None

async def store_reaction(reaction):
    """Store a reaction in the database"""
    try:
        # Add unique ID and timestamp
        if '_id' not in reaction:
            reaction['_id'] = str(uuid.uuid4())
        
        reaction['stored_at'] = datetime.now().isoformat()
        
        # Check if the reaction already exists (by URL or content hash)
        if 'url' in reaction:
            existing = await reactions_collection.find_one({'url': reaction['url']})
        else:
            # For reactions without URLs, use content as a unique identifier
            existing = await reactions_collection.find_one({'content': reaction['content']})
        
        if existing:
            # Update existing reaction
            await reactions_collection.update_one(
                {'_id': existing['_id']},
                {'$set': reaction}
            )
            logger.info(f"Updated existing reaction")
            return existing['_id']
        else:
            # Insert new reaction
            result = await reactions_collection.insert_one(reaction)
            logger.info(f"Stored new reaction")
            return result.inserted_id
    except Exception as e:
        logger.error(f"Error storing reaction: {str(e)}")
        return None

async def get_recent_news(days=1):
    """Get recent news items from the database"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor = news_collection.find({
            'published_date': {'$gte': cutoff_date.isoformat()}
        })
        
        news_items = await cursor.to_list(length=100)
        logger.info(f"Retrieved {len(news_items)} recent news items")
        return news_items
    except Exception as e:
        logger.error(f"Error retrieving recent news: {str(e)}")
        return []

async def get_reactions_for_news(news_id):
    """Get reactions for a specific news item"""
    try:
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
        cutoff_date = datetime.now() - timedelta(days=1)
        news_cursor = news_collection.find({
            'published_date': {'$gte': cutoff_date.isoformat()}
        })
        
        news_items = await news_cursor.to_list(length=100)
        
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
