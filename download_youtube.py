#!/usr/bin/env python3
"""
Simple YouTube Video Downloader
Downloads videos from YouTube using yt-dlp
"""

import sys
import os
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)


def download_video(url, output_path="./downloads"):
    """
    Download a YouTube video from the given URL.
    
    Args:
        url: YouTube video URL
        output_path: Directory where the video will be saved
    """
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            print(f"Output directory: {output_path}")
            ydl.download([url])
            print("\nDownload completed successfully!")
    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python download_youtube.py <youtube_url> [output_directory]")
        print("\nExample:")
        print("  python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ ./my_videos")
        sys.exit(1)
    
    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "./downloads"
    
    download_video(url, output_path)


if __name__ == "__main__":
    main()

