import os
import keyring

def get_api_key():
    # Try environment variable first
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if api_key:
        return api_key
    
    # Try system keyring
    try:
        api_key = keyring.get_password("youtube_api", "api_key")
        if api_key:
            return api_key
    except Exception:
        pass
    
    # Fall back to local config
    try:
        from local_config import YOUTUBE_API_KEY
        return YOUTUBE_API_KEY
    except ImportError:
        print("WARNING: YouTube API key not found.")
        print("Please set up your API key using one of the following methods:")
        print("1. Environment variable: YOUTUBE_API_KEY")
        print("2. System keyring (run set_api_key.py)")
        print("3. Local config file (local_config.py)")
        return ""