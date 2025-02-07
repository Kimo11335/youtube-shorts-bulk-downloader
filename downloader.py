import os
import yt_dlp
import time
from threading import Thread
import random

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
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'no_warnings': True,
        'ignore_no_formats_error': True,
    }

    if max_videos:
        ydl_opts['playlist_end'] = max_videos

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            update_label(progress_label_var, "Fetching videos from channel...")
            result = ydl.extract_info(playlist_url, download=False)
            
            if result and 'entries' in result:
                return [f'https://www.youtube.com/shorts/{entry["id"]}' 
                       for entry in result['entries'] 
                       if entry and 'id' in entry]
            else:
                update_label(progress_label_var, "No videos found in channel")
                return []
                
    except Exception as e:
        update_label(progress_label_var, f"Error: Failed to fetch videos - {str(e)}")
        return []

def update_label(label_var, text):
    try:
        label_var.set(text)
    except Exception:
        print(f"GUI update error: {text}")

def update_progress(progress_var, value):
    try:
        progress_var.set(value)
    except Exception:
        print(f"Progress update error: {value}")

def download_single_video(link, output_path):
    try:
        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'no_warnings': True,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return True
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

def download_videos_from_links(links, output_path, progress_var, progress_label_var):
    total_links = len(links)
    successful_downloads = 0
    
    os.makedirs(output_path, exist_ok=True)
    
    for index, link in enumerate(links, start=1):
        try:
            update_label(progress_label_var, f"Downloading video {index}/{total_links}")
            
            # Add random delay between downloads (2-5 seconds)
            time.sleep(random.uniform(2, 5))
            
            success = download_single_video(link, output_path)
            
            if success:
                successful_downloads += 1
                update_label(progress_label_var, 
                    f"Downloaded video {index}/{total_links} (Success: {successful_downloads})")
            else:
                update_label(progress_label_var, f"Skipped video {index}/{total_links} (unavailable)")
                
        except Exception as e:
            print(f"Error processing video {index}/{total_links}: {e}")
            update_label(progress_label_var, f"Failed to download video {index}/{total_links}")
            
        finally:
            update_progress(progress_var, int((index / total_links) * 100))
            
            # Add longer delay after every 10 videos
            if index % 10 == 0:
                delay = random.uniform(15, 30)
                update_label(progress_label_var, f"Rate limiting pause for {int(delay)} seconds...")
                time.sleep(delay)
    
    update_label(progress_label_var, 
        f"Download completed! Successfully downloaded {successful_downloads}/{total_links} videos")