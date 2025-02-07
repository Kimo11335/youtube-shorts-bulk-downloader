import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
from datetime import datetime, timedelta
import threading
import time
import os
from downloader import download_videos_from_links, get_short_links
from utils import extract_channel_name

# Set default path to the user's "Videos" folder
DEFAULT_DOWNLOAD_PATH = os.path.expanduser("~/Videos")
CHANNELS_FILE = "channels.txt"  # File to store the list of channels


def browse_folder(folder_var):
    """Open a dialog for folder selection."""
    folder_selected = filedialog.askdirectory(initialdir=folder_var.get())
    if folder_selected:
        folder_var.set(folder_selected)


def add_channel_to_list(channel_entry, channel_listbox, progress_label_var):
    """Add a channel name to the list."""
    channel_name = channel_entry.get().strip()
    if not channel_name:
        progress_label_var.set("Error: Please enter a channel name.")
        return

    # Validate the channel URL
    if not extract_channel_name(channel_name):
        progress_label_var.set("Error: Invalid channel URL.")
        return

    # Check for duplicates
    if channel_name in channel_listbox.get(0, tk.END):
        progress_label_var.set("Error: Channel already in the list.")
        return

    channel_listbox.insert(tk.END, channel_name)
    channel_entry.delete(0, tk.END)
    progress_label_var.set(f"Added channel: {channel_name}")


def remove_selected_channel(channel_listbox, progress_label_var):
    """Remove the selected channel from the list."""
    selected = channel_listbox.curselection()
    if not selected:
        progress_label_var.set("Error: No channel selected.")
        return

    channel_listbox.delete(selected[0])
    progress_label_var.set("Channel removed.")


def on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, max_videos=None):
    """Handle the button click for downloads (supports both full and limited)."""
    output_directory = folder_var.get()
    if not output_directory:
        progress_label_var.set("Error: Please select a folder.")
        return

    # Create the root folder if it doesn't exist
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

            # Extract channel name
            channel_name = extract_channel_name(channel_url)
            if not channel_name:
                progress_label_var.set(f"Error: Invalid channel URL - {channel_url}")
                continue

            # Create subfolder for the channel
            channel_folder = os.path.join(output_directory, channel_name)
            try:
                os.makedirs(channel_folder, exist_ok=True)
            except OSError as e:
                progress_label_var.set(f"Error: Failed to create folder for {channel_name} - {e}")
                continue

            # Get short links based on max_videos
            short_links = get_short_links(channel_url, progress_var, progress_label_var, max_videos=max_videos)
            if not short_links:
                progress_label_var.set(f"Channel {index}: No videos found.")
                continue

            download_videos_from_links(short_links, channel_folder, progress_var, progress_label_var)
            progress_label_var.set(f"Channel {index} completed.")

        progress_label_var.set("All channels processed.")

    Thread(target=download_channels).start()


def save_channels(channel_listbox):
    """Save the list of channels to a file."""
    channels = channel_listbox.get(0, tk.END)
    with open(CHANNELS_FILE, "w") as file:
        for channel in channels:
            file.write(f"{channel}\n")


def load_channels(channel_listbox):
    """Load the list of channels from a file."""
    try:
        with open(CHANNELS_FILE, "r") as file:
            for line in file:
                channel = line.strip()
                if channel:
                    channel_listbox.insert(tk.END, channel)
    except FileNotFoundError:
        pass  # Ignore if the file doesn't exist (e.g., first run)


def schedule_download(folder_var, channel_listbox, progress_var, progress_label_var, next_run_label):
    """Schedule the script to run at the next scheduled time."""
    next_run_time = datetime.now() + timedelta(hours=1)  # Start 1 hour from now
    next_run_label.set(f"Next Run At: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def run_schedule():
        nonlocal next_run_time
        while True:
            current_time = datetime.now()
            if current_time >= next_run_time:
                # Run the download with 11 videos (scheduled behavior)
                on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, max_videos=11)

                # Increment the next run time by 1 hour
                next_run_time += timedelta(hours=1)
                next_run_label.set(f"Next Run At: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Sleep for a short interval to avoid excessive CPU usage
            time.sleep(10)

    # Start the scheduling logic in a separate thread
    threading.Thread(target=run_schedule, daemon=True).start()


def run_gui():
    """Run the graphical user interface."""
    root = tk.Tk()
    root.title("YouTube Shorts Bulk Downloader")

    # Styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#2E2E2E", foreground="#FFFFFF")
    style.configure("TButton", background="#555555", foreground="#FFFFFF")
    style.configure("TEntry", fieldbackground="#555555", foreground="#FFFFFF")
    style.configure("Horizontal.TProgressbar", troughcolor="#555555", bordercolor="#555555", background="#009688")
    style.configure("TFrame", background="#2E2E2E")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Folder Selection
    folder_var = tk.StringVar(value=DEFAULT_DOWNLOAD_PATH)
    ttk.Label(main_frame, text="Select the folder to save videos:").grid(column=0, row=0, sticky=tk.W, pady=10)
    ttk.Entry(main_frame, textvariable=folder_var, state="readonly", width=50).grid(column=1, row=0, sticky=(tk.W, tk.E), pady=10)
    ttk.Button(main_frame, text="Browse", command=lambda: browse_folder(folder_var)).grid(column=2, row=0, sticky=tk.W, pady=10)

    # Channel URL Entry
    channel_entry = ttk.Entry(main_frame, width=50)
    channel_entry.grid(column=1, row=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    ttk.Button(
        main_frame, text="Add Channel",
        command=lambda: add_channel_to_list(channel_entry, channel_listbox, progress_label_var)
    ).grid(column=2, row=1, sticky=tk.W, pady=10)

    # Channel Listbox
    channel_listbox = tk.Listbox(main_frame, height=10, width=50)
    channel_listbox.grid(column=1, row=2, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    ttk.Button(
        main_frame, text="Remove Selected",
        command=lambda: remove_selected_channel(channel_listbox, progress_label_var)
    ).grid(column=2, row=2, sticky=tk.W, pady=10)

    # Download All Button
    progress_var = tk.IntVar()
    progress_label_var = tk.StringVar()
    ttk.Button(
        main_frame, text="Download All",
        command=lambda: on_start_button_click(folder_var, channel_listbox, progress_var, progress_label_var, max_videos=None)
    ).grid(column=0, row=3, columnspan=3, pady=10)

    # Progress Bar
    ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", variable=progress_var, style="Horizontal.TProgressbar").grid(column=0, row=4, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    # Progress Label
    ttk.Label(main_frame, textvariable=progress_label_var).grid(column=0, row=5, columnspan=3, pady=5, sticky=(tk.W, tk.E))

    # Next Run Time Section
    next_run_label = tk.StringVar(value="Next Run Time Not Set")
    ttk.Label(main_frame, textvariable=next_run_label).grid(column=0, row=6, columnspan=3, sticky=(tk.W, tk.E), pady=5)

    # Load saved channels
    load_channels(channel_listbox)

    # Start scheduling
    schedule_download(folder_var, channel_listbox, progress_var, progress_label_var, next_run_label)

    # Save channels when the window is closed
    root.protocol("WM_DELETE_WINDOW", lambda: [save_channels(channel_listbox), root.destroy()])

    root.mainloop()
