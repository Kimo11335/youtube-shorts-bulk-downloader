import os
from dotenv import load_dotenv
import requests
import sys

def test_api_key():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.environ.get("YOUTUBE_API_KEY")
    
    if not api_key:
        print("ERROR: YouTube API key not found in environment variables.")
        print("Make sure you've set up your API key using set_api_key_env.py")
        sys.exit(1)
    
    print(f"Found API key: {api_key[:5]}...{api_key[-3:]} (hidden for security)")
    
    # Make a simple API request to test the key
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&maxResults=1&key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            video = data['items'][0]
            print("\nAPI key is working correctly!")
            print(f"Successfully retrieved data for video: {video['snippet']['title']}")
            return True
        else:
            print("\nAPI request succeeded but returned no items.")
            return False
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("\nERROR: API key is invalid or has insufficient permissions.")
            print("Make sure your API key is correct and has YouTube Data API v3 enabled.")
        elif e.response.status_code == 400:
            print("\nERROR: Bad request. Check your API parameters.")
        else:
            print(f"\nHTTP Error: {e}")
        return False
    except Exception as e:
        print(f"\nError testing API key: {e}")
        return False

if __name__ == "__main__":
    test_api_key()