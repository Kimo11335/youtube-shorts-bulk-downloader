import os
import json
import datetime
import yt_dlp
from googleapiclient.discovery import build
import isodate
import time
import random

class ViralAnalyzer:
    def __init__(self, api_key, progress_var=None, progress_label_var=None):
        """
        Initialize the ViralAnalyzer with YouTube API key and optional progress tracking.
        
        Args:
            api_key (str): YouTube Data API key
            progress_var: Optional tkinter variable for progress bar
            progress_label_var: Optional tkinter variable for progress label
        """
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.progress_var = progress_var
        self.progress_label_var = progress_label_var
    
    def update_label(self, text):
        """Update the progress label if available."""
        if self.progress_label_var:
            try:
                self.progress_label_var.set(text)
            except Exception:
                print(f"GUI update error: {text}")
        else:
            print(text)
    
    def update_progress(self, value):
        """Update the progress bar if available."""
        if self.progress_var:
            try:
                self.progress_var.set(value)
            except Exception:
                print(f"Progress update error: {value}")
    
    def get_channel_id(self, channel_name):
        """
        Fetch the Channel ID from the channel username or URL.
        
        Args:
            channel_name (str): Channel name, username, or URL
        
        Returns:
            str: Channel ID or None if not found
        """
        # If it's a URL, extract the username or channel ID
        if "youtube.com" in channel_name:
            if "@" in channel_name:
                channel_name = channel_name.split("@")[1].split("/")[0]
            elif "/c/" in channel_name:
                channel_name = channel_name.split("/c/")[1].split("/")[0]
            elif "/channel/" in channel_name:
                return channel_name.split("/channel/")[1].split("/")[0]
        
        self.update_label(f"Searching for channel: {channel_name}")
        
        try:
            request = self.youtube.search().list(
                q=channel_name,
                type="channel",
                part="id,snippet",
                maxResults=1
            )
            response = request.execute()
            
            if "items" in response and response["items"]:
                channel_id = response["items"][0]["id"]["channelId"]
                channel_title = response["items"][0]["snippet"]["title"]
                self.update_label(f"Found channel: {channel_title} ({channel_id})")
                return channel_id
            else:
                self.update_label(f"Channel '{channel_name}' not found.")
                return None
        except Exception as e:
            self.update_label(f"Error finding channel: {str(e)}")
            return None
    
    def get_shorts_videos(self, channel_id, max_videos=100):
        """
        Retrieve Shorts videos (duration < 60s) from the channel.
        
        Args:
            channel_id (str): YouTube channel ID
            max_videos (int): Maximum number of videos to retrieve
        
        Returns:
            list: List of video data dictionaries
        """
        shorts = []
        next_page_token = None
        page_count = 0
        max_pages = 10  # Limit API calls
        
        self.update_label(f"Retrieving videos from channel {channel_id}")
        
        try:
            while page_count < max_pages:
                request = self.youtube.search().list(
                    channelId=channel_id,
                    part="id",
                    maxResults=50,
                    type="video",
                    pageToken=next_page_token,
                    order="date"  # Get most recent videos first
                )
                response = request.execute()
                
                video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
                
                if video_ids:
                    # Get details for all videos in batch
                    videos_data = self.get_videos_details(video_ids)
                    
                    # Filter for shorts and add to list
                    for video_data in videos_data:
                        if video_data and video_data["duration"] < 60:  # Ensure it's a Short
                            shorts.append(video_data)
                            self.update_label(f"Found Short: {video_data['title']} ({len(shorts)}/{max_videos})")
                
                # Update progress
                self.update_progress(min(100, int((len(shorts) / max_videos) * 100)))
                
                # Check if we need to continue
                next_page_token = response.get("nextPageToken")
                if not next_page_token or len(shorts) >= max_videos:
                    break
                
                page_count += 1
                time.sleep(1)  # Avoid API quota issues
            
            self.update_label(f"Found {len(shorts)} Shorts videos")
            return shorts[:max_videos]
        
        except Exception as e:
            self.update_label(f"Error retrieving videos: {str(e)}")
            return shorts
    
    def get_videos_details(self, video_ids):
        """
        Retrieve details for multiple videos in a single API call.
        
        Args:
            video_ids (list): List of YouTube video IDs
        
        Returns:
            list: List of video data dictionaries
        """
        if not video_ids:
            return []
        
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids)
            )
            response = request.execute()
            
            results = []
            for video in response.get("items", []):
                snippet = video["snippet"]
                stats = video["statistics"]
                content_details = video["contentDetails"]
                
                # Extract relevant metrics
                video_id = video["id"]
                title = snippet["title"]
                views = int(stats.get("viewCount", 0))
                comments = int(stats.get("commentCount", 0))
                likes = int(stats.get("likeCount", 0))
                publish_date = snippet["publishedAt"]
                duration = self.parse_duration(content_details["duration"])
                
                # Calculate age of the video in days
                days_since_upload = (datetime.datetime.utcnow() - 
                                    datetime.datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")).days
                days_since_upload = max(1, days_since_upload)  # Avoid division by zero
                
                video_data = {
                    "video_id": video_id,
                    "title": title,
                    "views": views,
                    "comments": comments,
                    "likes": likes,
                    "days_since_upload": days_since_upload,
                    "duration": duration,
                    "publish_date": publish_date
                }
                
                results.append(video_data)
            
            return results
        
        except Exception as e:
            self.update_label(f"Error getting video details: {str(e)}")
            return []
    
    def parse_duration(self, duration):
        """
        Convert ISO 8601 duration (PTXXMXXS) to seconds.
        
        Args:
            duration (str): ISO 8601 duration string
        
        Returns:
            int: Duration in seconds
        """
        try:
            return int(isodate.parse_duration(duration).total_seconds())
        except:
            return 0
    
    def calculate_viral_score(self, video):
        """
        Calculate viral score based on views, engagement, and video age.
        
        Args:
            video (dict): Video data dictionary
        
        Returns:
            float: Viral score
        """
        views_per_day = video["views"] / max(1, video["days_since_upload"])
        likes_to_views = video["likes"] / max(1, video["views"])
        comments_to_views = video["comments"] / max(1, video["views"])
        
        # Calculate score with weights
        score = (views_per_day * 0.6) + (likes_to_views * 0.2 * 10000) + (comments_to_views * 0.2 * 10000)
        return score
    
    def analyze_channel(self, channel_name, output_folder, max_videos=100):
        """
        Analyze a channel's Shorts videos and identify the most viral ones.
        
        Args:
            channel_name (str): Channel name or URL
            output_folder (str): Folder to save results
            max_videos (int): Maximum number of videos to analyze
        
        Returns:
            list: List of top viral videos with scores
        """
        # Get channel ID
        channel_id = self.get_channel_id(channel_name)
        if not channel_id:
            return []
        
        # Get shorts videos
        shorts = self.get_shorts_videos(channel_id, max_videos)
        if not shorts:
            self.update_label("No Shorts videos found on this channel.")
            return []
        
        # Calculate viral score for each video
        self.update_label("Calculating viral scores...")
        for video in shorts:
            video["viral_score"] = self.calculate_viral_score(video)
        
        # Sort by viral score
        top_shorts = sorted(shorts, key=lambda x: x["viral_score"], reverse=True)
        
        # Save metadata
        os.makedirs(output_folder, exist_ok=True)
        metadata_path = os.path.join(output_folder, "viral_shorts_metadata.json")
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(top_shorts, f, indent=4)
        
        self.update_label(f"Analysis complete. Found {len(top_shorts)} videos.")
        self.update_label(f"Metadata saved to {metadata_path}")
        
        return top_shorts
    
    def download_viral_videos(self, videos, output_folder, limit=50):
        """
        Download the top viral videos.
        
        Args:
            videos (list): List of video data dictionaries
            output_folder (str): Folder to save videos
            limit (int): Maximum number of videos to download
        
        Returns:
            list: Paths of downloaded videos
        """
        if not videos:
            return []
        
        # Limit to top videos
        top_videos = videos[:limit]
        total_videos = len(top_videos)
        downloaded_paths = []
        
        self.update_label(f"Preparing to download top {total_videos} viral videos...")
        
        for index, video in enumerate(top_videos, 1):
            video_id = video["video_id"]
            title = video["title"]
            
            self.update_label(f"Downloading {index}/{total_videos}: {title}")
            self.update_progress(int((index / total_videos) * 100))
            
            try:
                # Download the video
                video_url = f"https://www.youtube.com/shorts/{video_id}"
                filepath = self.download_video(video_url, output_folder)
                
                if filepath:
                    downloaded_paths.append(filepath)
                    self.update_label(f"Downloaded {index}/{total_videos}: {title}")
                else:
                    self.update_label(f"Failed to download {index}/{total_videos}: {title}")
                
                # Add delay to avoid rate limiting
                if index < total_videos:
                    delay = random.uniform(2, 5)
                    time.sleep(delay)
                    
                    # Longer pause every 10 videos
                    if index % 10 == 0:
                        pause = random.uniform(15, 30)
                        self.update_label(f"Rate limiting pause for {int(pause)} seconds...")
                        time.sleep(pause)
            
            except Exception as e:
                self.update_label(f"Error downloading video {index}: {str(e)}")
        
        self.update_label(f"Download complete. Successfully downloaded {len(downloaded_paths)}/{total_videos} videos")
        return downloaded_paths
    
    def download_video(self, video_url, output_folder):
        """
        Download a single YouTube video using yt-dlp.
        
        Args:
            video_url (str): YouTube video URL
            output_folder (str): Folder to save the video
        
        Returns:
            str: Path to downloaded file or None if failed
        """
        os.makedirs(output_folder, exist_ok=True)
        
        class DownloadLogger:
            def debug(self, msg):
                if msg.startswith('[download] Destination:'):
                    self.filename = msg.split('Destination: ')[1]
            
            def warning(self, msg):
                pass
            
            def error(self, msg):
                pass
        
        logger = DownloadLogger()
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'no_warnings': True,
            'logger': logger,
            'age_limit': 99
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                if hasattr(logger, 'filename') and os.path.exists(logger.filename):
                    return logger.filename
            return None
        except Exception as e:
            self.update_label(f"Error downloading video: {str(e)}")
            return None
