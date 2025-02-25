import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from viral_analyzer import ViralAnalyzer
from config import YOUTUBE_API_KEY, MAX_VIDEOS_TO_ANALYZE, MAX_VIDEOS_TO_DOWNLOAD

def run_viral_analyzer_gui():
    def browse_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            folder_var.set(folder_selected)
    
    def on_analyze_button_click():
        channel_name = channel_entry.get().strip()
        output_dir = folder_var.get()