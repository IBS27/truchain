#!/usr/bin/env python3
"""
Pre-process videos for verification V2
Transcribes all videos in a directory and caches them.
"""

import sys
from pathlib import Path
from word_transcription import WordTranscriber


def process_all_videos(video_directory: str = "download"):
    """
    Pre-process all videos in a directory.
    Transcribes each video and caches the results.
    
    Args:
        video_directory: Directory containing videos
    """
    print("\n" + "="*80)
    print("VIDEO PRE-PROCESSING - WORD-LEVEL TRANSCRIPTION")
    print("="*80)
    print(f"\nDirectory: {video_directory}\n")
    
    # Find all video files
    video_dir = Path(video_directory)
    if not video_dir.exists():
        print(f"Error: Directory not found: {video_directory}")
        return
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
    
    if not video_files:
        print(f"No video files found in {video_directory}")
        return
    
    print(f"Found {len(video_files)} video(s) to process\n")
    
    # Initialize transcriber
    transcriber = WordTranscriber()
    
    # Process each video
    successful = 0
    failed = 0
    cached = 0
    
    for i, video_path in enumerate(video_files, 1):
        print(f"[{i}/{len(video_files)}] {video_path.name}")
        print("-"*80)
        
        try:
            # Check if already cached
            cache_path = transcriber.get_cache_path(str(video_path))
            was_cached = cache_path.exists()
            
            # Transcribe (will use cache if available)
            transcription = transcriber.transcribe_with_word_timestamps(str(video_path))
            
            if was_cached:
                cached += 1
            else:
                successful += 1
            
            print()
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
            failed += 1
    
    # Summary
    print("="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"\nTotal videos: {len(video_files)}")
    print(f"✓ Newly transcribed: {successful}")
    print(f"✓ Loaded from cache: {cached}")
    print(f"✗ Failed: {failed}")
    print(f"\nCache directory: {transcriber.CACHE_DIR.absolute()}")
    print()


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-process videos with word-level transcription")
    parser.add_argument("--directory", default="download", help="Directory containing videos")
    
    args = parser.parse_args()
    
    process_all_videos(args.directory)


if __name__ == "__main__":
    main()

