
# YouTube Shorts Viral Analysis Tool

A tool for downloading and analyzing YouTube Shorts videos from specified channels to identify viral content patterns.

## Features

- Download YouTube Shorts videos from multiple channels
- Track download history to avoid duplicate downloads
- Rate-limiting protection to prevent API throttling
- Simple GUI interface for managing channels and downloads
- Customizable output folder for downloaded videos

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

## Channel Management

- Channels are stored in a `channels.txt` file in the application directory
- Each channel URL should be on a separate line
- You can manually edit this file or use the GUI to add/remove channels

## Troubleshooting Downloads

### Failed Downloads
If you see "FAILED download" messages, this could be due to:

1. **Already Downloaded**: The video was previously downloaded (check your output folder)
2. **Rate Limiting**: YouTube is throttling your requests (the app includes pauses to mitigate this)
3. **Video Unavailability**: The video may be private, deleted, or region-restricted
4. **Network Issues**: Temporary connection problems

### Improving Download Success
- Add longer pauses between downloads by modifying the delay values in the code
- Run downloads during off-peak hours
- Use a VPN if you're experiencing regional restrictions
- Check that your output folder has proper write permissions

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. Add YouTube channels using the "Add Channel" button
3. Select an output folder for downloaded videos
4. Click "Start Analysis" to begin downloading videos
</augment_code_snippet>

You can copy this entire content and replace what's currently in your README.md file. This includes the original API Key Setup section that you already have, plus the new Channel Management and Troubleshooting Downloads sections, as well as Features and Usage sections.



CMD RUN
cd C:\PythonProjects\youtube-shorts-bulk-downloader-1
C:\Users\karee\AppData\Local\Programs\Python\Python313\python.exe main.py


