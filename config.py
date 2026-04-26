import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration using environment variables"""

    # Flask session secret key - MUST be set via environment variable
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError(
            "ERROR: SECRET_KEY environment variable not set. "
            "Please create a .env file with SECRET_KEY=<your_secret_key>"
        )

    # MongoDB connection URI - MUST be set via environment variable
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError(
            "ERROR: MONGO_URI environment variable not set. "
            "Please create a .env file with MONGO_URI=<your_mongodb_connection_string>"
        )