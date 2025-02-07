import os
import subprocess
import yt_dlp
import time

def get_short_links(channel_url, progress_var, progress_label_var, max_videos=None):
    """Extract short links from a YouTube channel."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    if max_videos:
        ydl_opts['playlist_end'] = max_videos  # Restrict to max_videos if set

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            if 'entries' in result:
                video_ids = [entry['id'] for entry in result['entries']]
                return [f'https://www.youtube.com/shorts/{video_id}' for video_id in video_ids]
    except Exception as e:
        progress_label_var.set(f"Error: Failed to fetch videos - {e}")

    return []


def download_videos_from_links(links, output_path, progress_var, progress_label_var):
    """
    Download videos from provided YouTube Shorts links.
    """
    print(f"Downloading {len(links)} video(s) to: {output_path}")  # Debugging
    total_links = len(links)
    for index, link in enumerate(links, start=1):
        try:
            print(f"Downloading video {index}/{total_links}: {link}")  # Debugging
            subprocess.run(
                [
                    'yt-dlp',
                    '--quiet',
                    '--cookies', 'cookies.txt',  # Use cookies
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',  # Mimic a browser
                    '--referer', 'https://www.youtube.com/',  # Add referer header
                    '--output', os.path.join(output_path, '%(title)s.%(ext)s'),
                    link
                ],
                check=True
            )
            progress_label_var.set(f"Downloading video {index}/{total_links}: Success")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download video {index}/{total_links}: {e}")  # Debugging
            progress_label_var.set(f"Downloading video {index}/{total_links}: Failed - {e}")
        finally:
            progress_var.set(int((index / total_links) * 100))
        time.sleep(5)  # Add a 5-second delay between downloads