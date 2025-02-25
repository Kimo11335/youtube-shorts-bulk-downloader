import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime, timedelta
import threading
import time
import os
import traceback
import random
from downloader import download_videos_from_links, get_short_links
from utils import extract_channel_name

DEFAULT_DOWNLOAD_PATH = "C:\\PythonProjects\\Videos"
CHANNELS_FILE = "channels.txt"

def run_gui():
    class DownloadHistory(tk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.history_text = tk.Text(self, height=3, width=50, wrap=tk.WORD)
            self.history_text.pack(fill=tk.BOTH, expand=True)
            self.history_text.config(state=tk.DISABLED)

        def add_entry(self, text):
            self.history_text.config(state=tk.NORMAL)
            self.history_text.insert(tk.END, f"{text}\n")
            self.history_text.see(tk.END)
            self.history_text.config(state=tk.DISABLED)

        def clear(self):
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            self.history_text.config(state=tk.DISABLED)

    def browse_folder(folder_var):
        folder_selected = filedialog.askdirectory(initialdir=folder_var.get())
        if folder_selected:
            folder_var.set(folder_selected)

    def add_channel_to_list(channel_entry, channel_listbox, progress_label_var):
        channel_name = channel_entry.get().strip()
        if not channel_name:
            progress_label_var.set("Error: Please enter a channel name.")
            return

        if not extract_channel_name(channel_name):
            progress_label_var.set("Error: Invalid channel URL.")
            return

        if channel_name in channel_listbox.get(0, tk.END):
            progress_label_var.set("Error: Channel already in the list.")
            return

        channel_listbox.insert(tk.END, channel_name)
        channel_entry.delete(0, tk.END)
        progress_label_var.set(f"Added channel: {channel_name}")

    def remove_selected_channel(channel_listbox, progress_label_var):
        selected = channel_listbox.curselection()
        if not selected:
            progress_label_var.set("Error: No channel selected.")
            return

        channel_listbox.delete(selected[0])
        progress_label_var.set("Channel removed.")

    def update_download_history(history_widget, filepath):
        history_widget.add_entry(f"Downloaded: {filepath}")

    def on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, history_widget, current_channel_var, max_videos=None):
        from viral_analyzer import ViralAnalyzer
        from config import YOUTUBE_API_KEY, MAX_VIDEOS_TO_ANALYZE, MAX_VIDEOS_TO_DOWNLOAD
        
        output_directory = folder_var.get()
        if not output_directory:
            progress_label_var.set("Error: Please select a folder.")
            return

        try:
            os.makedirs(output_directory, exist_ok=True)
        except OSError as e:
            progress_label_var.set(f"Error: Failed to create folder - {e}")
            return

        channels = channel_listbox.get(0, tk.END)
        if not channels:
            progress_label_var.set("Error: No channels in the list.")
            return

        def custom_progress_callback(filepath):
            history_widget.after(0, lambda: update_download_history(history_widget, filepath))

        def download_channels():
            total_channels = len(channels)
            for index, channel_url in enumerate(channels, start=1):
                channel_name = extract_channel_name(channel_url)
                current_channel_var.set(f"Current Channel: {channel_name}")
                progress_label_var.set(f"Processing channel {index}/{total_channels}...")

                if not channel_name:
                    progress_label_var.set(f"Error: Invalid channel URL - {channel_url}")
                    continue

                channel_folder = os.path.join(output_directory, channel_name)
                try:
                    os.makedirs(channel_folder, exist_ok=True)
                except OSError as e:
                    progress_label_var.set(f"Error: Failed to create folder for {channel_name} - {e}")
                    continue

                # Use ViralAnalyzer instead of direct download
                try:
                    # Initialize the viral analyzer with progress tracking
                    analyzer = ViralAnalyzer(YOUTUBE_API_KEY, progress_var, progress_label_var)
                    
                    # Analyze the channel to find viral videos
                    progress_label_var.set(f"Analyzing viral potential for {channel_name}...")
                    viral_videos = analyzer.analyze_channel(
                        channel_url, 
                        channel_folder, 
                        max_videos=MAX_VIDEOS_TO_ANALYZE
                    )
                    
                    if not viral_videos:
                        progress_label_var.set(f"No viral videos found for {channel_name}")
                        continue
                    
                    # Download the top viral videos
                    progress_label_var.set(f"Downloading top {MAX_VIDEOS_TO_DOWNLOAD} viral videos for {channel_name}...")
                    downloaded_paths = analyzer.download_viral_videos(
                        viral_videos, 
                        channel_folder, 
                        limit=MAX_VIDEOS_TO_DOWNLOAD
                    )
                    
                    # Update download history
                    for path in downloaded_paths:
                        custom_progress_callback(path)
                    
                    progress_label_var.set(f"Channel {index}: Downloaded {len(downloaded_paths)} viral videos.")
                    
                except Exception as e:
                    progress_label_var.set(f"Error analyzing channel {channel_name}: {str(e)}")
                    continue

                if index < total_channels:
                    pause_time = random.randint(60, 300)
                    progress_label_var.set(f"Channel {index} completed. Pausing for {pause_time} seconds...")
                    time.sleep(pause_time)

            progress_label_var.set("All channels processed.")
            current_channel_var.set("Current Channel: None")

        threading.Thread(target=download_channels).start()

    def save_channels(channel_listbox):
        channels = channel_listbox.get(0, tk.END)
        with open(CHANNELS_FILE, "w") as file:
            for channel in channels:
                file.write(f"{channel}\n")

    def load_channels(channel_listbox):
        try:
            with open(CHANNELS_FILE, "r") as file:
                for line in file:
                    channel = line.strip()
                    if channel:
                        channel_listbox.insert(tk.END, channel)
        except FileNotFoundError:
            pass

    def schedule_download(folder_var, channel_listbox, progress_var, progress_label_var, history_widget, current_channel_var, next_run_label):
        def run_schedule():
            # Remove the immediate download call
            # on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, 
            #                     history_widget, current_channel_var, max_videos=11)
            
            next_run_time = datetime.now() + timedelta(hours=1)
            next_run_label.set(f"Next Run At: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            while True:
                current_time = datetime.now()
                if current_time >= next_run_time:
                    on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, 
                                        history_widget, current_channel_var, max_videos=11)
                    next_run_time += timedelta(hours=1)
                    next_run_label.set(f"Next Run At: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(10)

        threading.Thread(target=run_schedule, daemon=True).start()

    try:
        root = tk.Tk()
        root.title("YouTube Shorts Bulk Downloader")

        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        folder_var = tk.StringVar(value=DEFAULT_DOWNLOAD_PATH)
        ttk.Label(main_frame, text="Select folder to save videos:").grid(column=0, row=0, sticky=tk.W, pady=10)
        ttk.Entry(main_frame, textvariable=folder_var, state="readonly", width=50).grid(column=1, row=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Button(main_frame, text="Browse", command=lambda: browse_folder(folder_var)).grid(column=2, row=0, sticky=tk.W, pady=10)

        channel_entry = ttk.Entry(main_frame, width=50)
        channel_entry.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=10)
        ttk.Button(main_frame, text="Add Channel", 
                command=lambda: add_channel_to_list(channel_entry, channel_listbox, progress_label_var)
                ).grid(column=2, row=1, sticky=tk.W, pady=10)

        channel_listbox = tk.Listbox(main_frame, height=10, width=50)
        channel_listbox.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=10)
        ttk.Button(main_frame, text="Remove Selected",
                command=lambda: remove_selected_channel(channel_listbox, progress_label_var)
                ).grid(column=2, row=2, sticky=tk.W, pady=10)

        progress_var = tk.IntVar()
        progress_label_var = tk.StringVar(value="Ready")
        next_run_label = tk.StringVar(value="Next Run: Not Scheduled")
        current_channel_var = tk.StringVar(value="Current Channel: None")

        ttk.Label(main_frame, textvariable=current_channel_var, 
                 font=('TkDefaultFont', 10, 'bold')).grid(column=1, row=3, pady=5)

        ttk.Label(main_frame, text="Recent Downloads:").grid(column=0, row=4, sticky=tk.W, pady=5)
        history_widget = DownloadHistory(main_frame)
        history_widget.grid(column=1, row=4, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(main_frame, text="Download All",
                command=lambda: on_start_button_click(folder_var, channel_listbox, progress_var, 
                                                    progress_label_var, history_widget, current_channel_var)
                ).grid(column=1, row=5, pady=10)

        ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", 
                    variable=progress_var).grid(column=1, row=6, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(main_frame, textvariable=progress_label_var).grid(column=1, row=7, pady=5)
        ttk.Label(main_frame, textvariable=next_run_label).grid(column=1, row=8, pady=5)

        load_channels(channel_listbox)
        schedule_download(folder_var, channel_listbox, progress_var, progress_label_var, 
                         history_widget, current_channel_var, next_run_label)
        root.protocol("WM_DELETE_WINDOW", lambda: [save_channels(channel_listbox), root.destroy()])

        root.mainloop()
        
    except Exception as e:
        print(f"Error in GUI: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_gui()
