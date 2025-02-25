import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# YouTube API Configuration
# Get API key from environment variable
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# If not in environment variables, try to load from local_config.py
if not YOUTUBE_API_KEY:
    try:
        from local_config import YOUTUBE_API_KEY
    except ImportError:
        print("WARNING: YouTube API key not found.")
        print("Please either:")
        print("1. Set the YOUTUBE_API_KEY environment variable, or")
        print("2. Create a local_config.py file with YOUTUBE_API_KEY defined")

# Maximum number of videos to analyze per channel
MAX_VIDEOS_TO_ANALYZE = 100

# Maximum number of viral videos to download
MAX_VIDEOS_TO_DOWNLOAD = 31
