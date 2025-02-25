import os
import json
import datetime
import yt_dlp
import time
import random
import pandas as pd

class ViralAnalyzer:
    def __init__(self, api_key=None, progress_var=None, progress_label_var=None):
        """
        Initialize the ViralAnalyzer with optional progress tracking.
        
        Args:
            api_key (str): Not used in this version as we're using yt-dlp
            progress_var: Optional tkinter variable for progress bar
            progress_label_var: Optional tkinter variable for progress label
        """
        self.progress_var = progress_var
        self.progress_label_var = progress_label_var
    
    def update_label(self, text):
        """Update the progress label if available."""
        if self.progress_label_var:
            try:
                self.progress_label_var.set(text)
            except Exception:
                print(f"GUI update error: {text}")
    
    def update_progress(self, value):
        """Update the progress bar if available."""
        if self.progress_var:
            try:
                self.progress_var.set(value)
            except Exception:
                print(f"Progress update error: {value}")
    
    def get_channel_videos(self, channel_url, top_n=11):
        """
        Get the top viral videos from a channel using yt-dlp.
        
        Args:
            channel_url (str): YouTube channel URL
            top_n (int): Number of top videos to return
            
        Returns:
            DataFrame: Top videos sorted by comments, views, and upload date
        """
        self.update_label(f"Fetching videos from {channel_url}...")
        
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
            
            videos = info.get('entries', [])
            video_data = []

            # Extract metadata
            self.update_label(f"Processing {len(videos)} videos...")
            for i, video in enumerate(videos):
                video_data.append({
                    'title': video.get('title'),
                    'url': video.get('url'),
                    'video_id': video.get('id'),
                    'views': int(video.get('view_count', 0)),
                    'comments': int(video.get('comment_count', 0)),
                    'upload_date': video.get('upload_date')  # YYYYMMDD format
                })
                
                # Update progress every 10 videos
                if i % 10 == 0 and self.progress_var:
                    self.update_progress(int((i / len(videos)) * 100))

            # Convert to DataFrame
            df = pd.DataFrame(video_data)
            
            if df.empty:
                self.update_label("No videos found in channel")
                return df
                
            # Sorting: Most Comments → Most Views → Newest Upload
            df = df.sort_values(by=['comments', 'views', 'upload_date'], 
                               ascending=[False, False, False])

            # Return Top N
            self.update_label(f"Found {len(df)} videos, returning top {top_n}")
            return df.head(top_n)
            
        except Exception as e:
            self.update_label(f"Error fetching videos: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def analyze_channel(self, channel_url, output_folder, max_videos=100):
        """
        Analyze a YouTube channel to find viral videos.
        
        Args:
            channel_url (str): URL of the YouTube channel
            output_folder (str): Folder to save metadata
            max_videos (int): Maximum number of videos to analyze
            
        Returns:
            DataFrame: DataFrame containing viral videos sorted by engagement
        """
        self.update_label(f"Analyzing channel: {channel_url}")
        
        # Get top videos from channel
        df_videos = self.get_channel_videos(channel_url, top_n=max_videos)
        
        if df_videos.empty:
            self.update_label("No videos found to analyze")
            return df_videos
        
        # Save metadata to JSON file
        metadata_path = os.path.join(output_folder, "viral_videos_metadata.json")
        try:
            df_videos.to_json(metadata_path, orient="records", indent=4)
            self.update_label(f"Saved metadata to {metadata_path}")
        except Exception as e:
            self.update_label(f"Error saving metadata: {str(e)}")
        
        return df_videos
    
    def download_viral_videos(self, viral_videos_df, output_folder, limit=10):
        """
        Download the top viral videos.
        
        Args:
            viral_videos_df (DataFrame): DataFrame containing viral videos
            output_folder (str): Folder to save downloaded videos
            limit (int): Maximum number of videos to download
            
        Returns:
            list: Paths of downloaded videos
        """
        if viral_videos_df.empty:
            self.update_label("No videos to download")
            return []
        
        # Limit the number of videos to download
        videos_to_download = viral_videos_df.head(limit)
        total_videos = len(videos_to_download)
        
        self.update_label(f"Downloading {total_videos} viral videos...")
        downloaded_paths = []
        
        for i, (_, video) in enumerate(videos_to_download.iterrows()):
            video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
            video_title = video['title']
            
            self.update_label(f"Downloading {i+1}/{total_videos}: {video_title}")
            self.update_progress(int((i / total_videos) * 100))
            
            # Set up yt-dlp options
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    if info:
                        filename = ydl.prepare_filename(info)
                        downloaded_paths.append(filename)
                        self.update_label(f"Successfully downloaded: {os.path.basename(filename)}")
            except Exception as e:
                self.update_label(f"Error downloading {video_title}: {str(e)}")
            
            # Add delay between downloads to avoid rate limiting
            if i < total_videos - 1:
                sleep_time = random.uniform(11, 21)
                self.update_label(f"Rate limiting pause for {int(sleep_time)} seconds...")
                time.sleep(sleep_time)
        
        self.update_label(f"Downloaded {len(downloaded_paths)}/{total_videos} videos")
        self.update_progress(100)
        
        return downloaded_paths
