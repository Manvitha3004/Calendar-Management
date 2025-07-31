from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get MongoDB configuration from environment
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "calendar_management_app")

# Validate required environment variables
if not MONGO_URI:
    logger.error("MONGO_URI environment variable is required")
    # Use default for development
    MONGO_URI = "mongodb://localhost:27017"
    logger.warning(f"Using default MongoDB URI: {MONGO_URI}")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    logger.info(f"MongoDB client initialized for database: {DATABASE_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise e

# Collections
events_collection = db.events

async def connect_to_mongo():
    try:
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Create indexes for better performance
        await db.events.create_index("start")
        await db.events.create_index("agendaOrder")
        await db.emails.create_index("message_id")
        await db.emails.create_index("recipient")
        await db.email_drafts.create_index("user_id")
        await db.email_reminders.create_index("user_id")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    try:
        client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
