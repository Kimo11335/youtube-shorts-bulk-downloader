## API Key Setup

This application requires a YouTube Data API key. For security reasons, you should never commit your API key to the repository.

### Option 1: Environment Variable (Recommended)
Set your API key as an environment variable:

**Linux/Mac:**
```bash
export YOUTUBE_API_KEY=your_api_key_here
```

**Windows:**
```bash
set YOUTUBE_API_KEY=your_api_key_here
```

### Option 2: Local Configuration File
1. Copy `local_config.template.py` to `local_config.py`
2. Edit `local_config.py` and add your API key
3. Make sure `local_config.py` is in your `.gitignore` file

### Getting a YouTube API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (API key)
5. Consider restricting the API key to only the YouTube Data API
