import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
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

def on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, max_videos=None):
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

    def download_channels():
        total_channels = len(channels)
        for index, channel_url in enumerate(channels, start=1):
            progress_label_var.set(f"Processing channel {index}/{total_channels}...")

            channel_name = extract_channel_name(channel_url)
            if not channel_name:
                progress_label_var.set(f"Error: Invalid channel URL - {channel_url}")
                continue

            channel_folder = os.path.join(output_directory, channel_name)
            try:
                os.makedirs(channel_folder, exist_ok=True)
            except OSError as e:
                progress_label_var.set(f"Error: Failed to create folder for {channel_name} - {e}")
                continue

            short_links = get_short_links(channel_url, progress_var, progress_label_var, max_videos=max_videos)
            if not short_links:
                progress_label_var.set(f"Channel {index}: No videos found.")
                continue

            download_videos_from_links(short_links, channel_folder, progress_var, progress_label_var)
            progress_label_var.set(f"Channel {index} completed.")

            if index < total_channels:
                pause_time = random.randint(60, 300)  # Random pause between 1-5 minutes
                progress_label_var.set(f"Channel {index} completed. Pausing for {pause_time} seconds...")
                time.sleep(pause_time)

        progress_label_var.set("All channels processed.")

    Thread(target=download_channels).start()

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

def schedule_download(folder_var, channel_listbox, progress_var, progress_label_var, next_run_label):
    def run_schedule():
        # Run immediately first
        on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, max_videos=11)
        
        # Set next run time to 1 hour from now
        next_run_time = datetime.now() + timedelta(hours=1)
        next_run_label.set(f"Next Run At: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while True:
            current_time = datetime.now()
            if current_time >= next_run_time:
                on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, max_videos=11)
                next_run_time += timedelta(hours=1)
                next_run_label.set(f"Next Run At: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(10)

    threading.Thread(target=run_schedule, daemon=True).start()

def run_gui():
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
        
        ttk.Button(main_frame, text="Download All",
                command=lambda: on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var)
                ).grid(column=1, row=3, pady=10)

        ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", 
                    variable=progress_var).grid(column=1, row=4, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(main_frame, textvariable=progress_label_var).grid(column=1, row=5, pady=5)

        next_run_label = tk.StringVar(value="Next Run: Not Scheduled")
        ttk.Label(main_frame, textvariable=next_run_label).grid(column=1, row=6, pady=5)

        load_channels(channel_listbox)
        schedule_download(folder_var, channel_listbox, progress_var, progress_label_var, next_run_label)
        root.protocol("WM_DELETE_WINDOW", lambda: [save_channels(channel_listbox), root.destroy()])

        print("GUI initialized, starting mainloop...")
        root.mainloop()
        print("GUI mainloop ended")
        
    except Exception as e:
        print(f"Error in GUI: {e}")
        traceback.print_exc()