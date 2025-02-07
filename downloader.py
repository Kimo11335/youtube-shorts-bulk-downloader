import os
import subprocess
import yt_dlp
import time
import tkinter as tk
from threading import Thread

def extract_shorts_playlist(channel_url):
    """Convert channel URL to shorts playlist URL."""
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
    """Extract short links from a YouTube channel."""
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
        update_label(progress_label_var, f"Error: Failed to fetch videos - {e}")
        print(f"Error details: {str(e)}")
        return []

def update_label(label_var, text):
    """Thread-safe update of tkinter label."""
    try:
        label_var.set(text)
    except tk.TclError:
        print(f"GUI update error: {text}")

def update_progress(progress_var, value):
    """Thread-safe update of progress bar."""
    try:
        progress_var.set(value)
    except tk.TclError:
        print(f"Progress update error: {value}")

def download_single_video(link, output_path):
    """Download a single video with error handling."""
    try:
        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best',  # Prefer WebM format
            'outtmpl': os.path.join(output_path, '%(title)s.webm'),  # Force .webm extension
            'no_warnings': True,
            'ignoreerrors': True,
            'merge_output_format': 'webm'  # Force WebM as output format
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return True
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

def download_videos_from_links(links, output_path, progress_var, progress_label_var):
    """Download videos from provided YouTube Shorts links."""
    print(f"Downloading {len(links)} video(s) to: {output_path}")
    total_links = len(links)
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    for index, link in enumerate(links, start=1):
        try:
            # Update progress
            update_label(progress_label_var, f"Downloading video {index}/{total_links}")
            
            # Download video using yt-dlp library directly instead of subprocess
            success = download_single_video(link, output_path)
            
            if success:
                update_label(progress_label_var, f"Downloaded video {index}/{total_links}")
            else:
                update_label(progress_label_var, f"Skipped video {index}/{total_links} (unavailable)")
                
        except Exception as e:
            print(f"Error processing video {index}/{total_links}: {e}")
            update_label(progress_label_var, f"Failed to download video {index}/{total_links}")
            
        finally:
            update_progress(progress_var, int((index / total_links) * 100))
            time.sleep(1)  # Brief delay between downloads
    
    update_label(progress_label_var, "Download completed!")