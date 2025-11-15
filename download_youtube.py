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


def get_format_selector(quality="best"):
    """
    Get format selector based on quality preference.
    
    Args:
        quality: Quality level - "best", "high" (720p), "medium" (480p), "low" (360p), or custom format string
    
    Returns:
        Format selector string for yt-dlp
    """
    quality_map = {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "high": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
        "medium": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]",
        "low": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]",
    }
    
    return quality_map.get(quality.lower(), quality)


def download_video(url, output_path="./downloads", quality="best"):
    """
    Download a YouTube video from the given URL.
    
    Args:
        url: YouTube video URL
        output_path: Directory where the video will be saved
        quality: Video quality - "best", "high" (720p), "medium" (480p), "low" (360p), or custom format string
    """
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': get_format_selector(quality),
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            print(f"Output directory: {output_path}")
            print(f"Quality: {quality}")
            ydl.download([url])
            print("\nDownload completed successfully!")
    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python download_youtube.py <youtube_url> [output_directory] [quality]")
        print("\nQuality options:")
        print("  best   - Highest quality available (default)")
        print("  high   - 720p")
        print("  medium - 480p")
        print("  low    - 360p or lower")
        print("\nExamples:")
        print("  python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ ./my_videos")
        print("  python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ ./my_videos medium")
        sys.exit(1)
    
    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "./downloads"
    quality = sys.argv[3] if len(sys.argv) > 3 else "best"
    
    download_video(url, output_path, quality)


if __name__ == "__main__":
    main()

