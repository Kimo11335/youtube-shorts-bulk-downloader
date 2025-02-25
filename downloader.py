import os
import yt_dlp
import time
import random
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("downloader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_shorts_playlist(channel_url):
    if '@' in channel_url:
        username = channel_url.split('@')[1].split('/')[0]
        return f"https://www.youtube.com/@{username}/shorts"
    elif '/c/' in channel_url:
        channel_name = channel_url.split('/c/')[1].split('/')[0]
        return f"https://www.youtube.com/c/{channel_name}/shorts"
    elif '/channel/' in channel_url:
        channel_id = channel_url.split('/channel/')[1].split('/')[0]
        return f"https://www.youtube.com/channel/{channel_id}/shorts"
    return f"{channel_url.rstrip('/')}/shorts"

def get_short_links(channel_url, progress_var, progress_label_var, max_videos=None):
    playlist_url = extract_shorts_playlist(channel_url)
    logger.info(f"Fetching shorts from playlist: {playlist_url}")
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'no_warnings': True,
        'ignore_no_formats_error': True,
        'age_limit': 99
    }

    if max_videos:
        ydl_opts['playlist_end'] = max_videos

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            update_label(progress_label_var, "Fetching videos from channel...")
            result = ydl.extract_info(playlist_url, download=False)
            
            if result and 'entries' in result:
                links = [f'https://www.youtube.com/shorts/{entry["id"]}' 
                       for entry in result['entries'] 
                       if entry and 'id' in entry]
                logger.info(f"Found {len(links)} shorts in channel")
                return links
            else:
                update_label(progress_label_var, "No videos found in channel")
                logger.warning(f"No videos found in channel: {channel_url}")
                return []
                
    except Exception as e:
        update_label(progress_label_var, f"Error: Failed to fetch videos - {str(e)}")
        logger.error(f"Failed to fetch videos from {channel_url}: {str(e)}")
        return []

def update_label(label_var, text):
    try:
        label_var.set(text)
        logger.debug(f"UI update: {text}")
    except Exception as e:
        logger.error(f"GUI update error: {text} - {str(e)}")
        print(f"GUI update error: {text}")

def update_progress(progress_var, value):
    try:
        progress_var.set(value)
    except Exception as e:
        logger.error(f"Progress update error: {value} - {str(e)}")
        print(f"Progress update error: {value}")

class DownloadLogger:
    def debug(self, msg):
        if msg.startswith('[download] Destination:'):
            self.filename = msg.split('Destination: ')[1]
            logger.debug(f"Download destination: {self.filename}")
    
    def warning(self, msg):
        logger.warning(f"yt-dlp warning: {msg}")
    
    def error(self, msg):
        logger.error(f"yt-dlp error: {msg}")

def download_single_video(link, output_path):
    logger.info(f"Attempting to download: {link}")
    download_logger = DownloadLogger()
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'no_warnings': True,
        'logger': download_logger,
        'progress_hooks': [],
        'age_limit': 99,
        'overwrites': False,  # Prevent overwriting existing files
        # Rate limiting options
        'limit_rate': '1M',
        'sleep_interval': 5,
        'max_sleep_interval': 30,
        'sleep_interval_requests': 2,
        'throttled_rate': '100K'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Check if the file already exists before downloading
            info = ydl.extract_info(link, download=False)
            if info:
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    logger.info(f"File already exists: {filename}")
                    print(f"File already exists: {filename}")
                    return True, filename
            
            # If file doesn't exist, proceed with download
            ydl.download([link])
            if hasattr(download_logger, 'filename') and os.path.exists(download_logger.filename):
                logger.info(f"Successfully downloaded: {download_logger.filename}")
                return True, download_logger.filename
        logger.warning(f"Download completed but file not found for: {link}")
        return False, None
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e).lower()
        if "already been downloaded" in error_message:
            # Extract the filename from the error message if possible
            logger.info(f"File already downloaded: {error_message}")
            print(f"File already downloaded: {error_message}")
            return True, None  # Consider this a success
        elif "rate limit" in error_message or "429" in error_message:
            logger.warning(f"Rate limit error: {error_message}")
            print(f"Rate limit error: {error_message}")
        else:
            logger.error(f"Download error: {error_message}")
            print(f"Download error: {error_message}")
        return False, None
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        print(f"Error downloading video: {str(e)}")
        return False, None

def download_videos_from_links(links, output_path, progress_var, progress_label_var, progress_callback=None):
    total_links = len(links)
    successful_downloads = 0
    
    logger.info(f"Starting download of {total_links} videos to {output_path}")
    os.makedirs(output_path, exist_ok=True)
    
    for index, link in enumerate(links, start=1):
        try:
            update_label(progress_label_var, f"Downloading video {index}/{total_links}")
            
            # Initial small delay before each download attempt
            time.sleep(random.uniform(2, 5))
            
            success, filepath = download_single_video(link, output_path)
            
            if success and filepath:
                successful_downloads += 1
                update_label(progress_label_var, 
                    f"Downloaded video {index}/{total_links} (Success: {successful_downloads})")
                logger.info(f"Download success ({index}/{total_links}): {filepath}")
                if progress_callback:
                    progress_callback(filepath)
            else:
                update_label(progress_label_var, f"Skipped video {index}/{total_links} (unavailable)")
                logger.warning(f"Skipped video {index}/{total_links}: {link}")
                
        except Exception as e:
            logger.error(f"Error processing video {index}/{total_links}: {e}")
            print(f"Error processing video {index}/{total_links}: {e}")
            update_label(progress_label_var, f"Failed to download video {index}/{total_links}")
            
        finally:
            update_progress(progress_var, int((index / total_links) * 100))
            
            # Sleep 21-31 seconds after every video download (changed from 11-21)
            sleep_time = random.uniform(21, 31)
            logger.info(f"Rate limiting pause for {int(sleep_time)} seconds...")
            update_label(progress_label_var, f"Rate limiting pause for {int(sleep_time)} seconds...")
            time.sleep(sleep_time)
            
            # Additional longer pause every 10 videos
            if index % 10 == 0:
                delay = random.uniform(15, 30)
                logger.info(f"Extended rate limiting pause for {int(delay)} seconds...")
                update_label(progress_label_var, f"Extended rate limiting pause for {int(delay)} seconds...")
                time.sleep(delay)
    
    logger.info(f"Download completed! Successfully downloaded {successful_downloads}/{total_links} videos")
    update_label(progress_label_var, 
        f"Download completed! Successfully downloaded {successful_downloads}/{total_links} videos")
