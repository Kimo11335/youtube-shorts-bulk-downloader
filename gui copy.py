# Displays the user interface (windows, buttons, input fields, progress bar).
# Handles user interactions (e.g., button clicks, folder selection).
# Delegates the actual work (e.g., downloading) to other modules like downloader.py.
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
from downloader import download_videos_from_links, get_short_links

def browse_folder(folder_var):
    """Open a dialog for folder selection."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)

def on_start_button_click(folder_var, channel_entry, progress_var, progress_label_var):
    """Handle the start button click."""
    output_directory = folder_var.get()
    if not output_directory:
        progress_label_var.set("Error: Please select a folder.")
        return

    channel_url = channel_entry.get()
    if not channel_url:
        progress_label_var.set("Error: Please enter a valid URL.")
        return

    short_links = get_short_links(channel_url, progress_var, progress_label_var)
    if not short_links:
        progress_label_var.set("Error: No videos found.")
        return

    Thread(target=download_videos_from_links, args=(short_links, output_directory, progress_var, progress_label_var)).start()

def run_gui():
    """Run the graphical user interface."""
    root = tk.Tk()
    root.title("Shorts Bulk DL By Sewer")

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
    folder_var = tk.StringVar()
    ttk.Label(main_frame, text="Select the folder to save videos:").grid(column=0, row=0, sticky=tk.W, pady=10)
    ttk.Entry(main_frame, textvariable=folder_var, state="readonly", width=50).grid(column=1, row=0, sticky=(tk.W, tk.E), pady=10)
    ttk.Button(main_frame, text="Browse", command=lambda: browse_folder(folder_var)).grid(column=2, row=0, sticky=tk.W, pady=10)

    # Channel URL
    ttk.Label(main_frame, text="Enter the YouTube channel URL:").grid(column=0, row=1, sticky=tk.W, pady=10)
    channel_entry = ttk.Entry(main_frame, width=50)
    channel_entry.grid(column=1, row=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)

    # Start Button
    progress_var = tk.IntVar()
    progress_label_var = tk.StringVar()
    ttk.Button(
        main_frame, text="Start Download",
        command=lambda: on_start_button_click(folder_var, channel_entry, progress_var, progress_label_var)
    ).grid(column=0, row=2, columnspan=3, pady=10)

    # Progress Bar
    ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", variable=progress_var, style="Horizontal.TProgressbar").grid(column=0, row=3, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    # Progress Label
    ttk.Label(main_frame, textvariable=progress_label_var).grid(column=0, row=4, columnspan=3, pady=5, sticky=(tk.W, tk.E))

    root.mainloop()
