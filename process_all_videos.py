#!/usr/bin/env python3
"""
Process all videos in the download folder and add to database.
"""

from pathlib import Path
from video_processor import process_video, VideoDatabase
import time

videos_dir = Path("download")
db_path = "video_database.json"

# Find all MP4 files
video_files = sorted(videos_dir.glob("*.mp4"))

if not video_files:
    print("No video files found in download/ folder")
    exit(1)

print("="*70)
print("PROCESSING ALL VIDEOS")
print("="*70)
print(f"\nFound {len(video_files)} video(s) to process\n")

# Check existing database
db = VideoDatabase(db_path)
existing_videos = db.get_all_videos()
existing_ids = {v['id'] for v in existing_videos}

print(f"Current database has {len(existing_videos)} video(s)\n")

processed = 0
skipped = 0
failed = 0

for idx, video_path in enumerate(video_files, 1):
    print(f"\n{'='*70}")
    print(f"VIDEO {idx}/{len(video_files)}: {video_path.name}")
    print(f"{'='*70}\n")
    
    # Generate video ID to check if it exists
    video_id = db.generate_video_id(str(video_path))
    
    if video_id in existing_ids:
        print(f"⊘ SKIPPED - Already in database (ID: {video_id})")
        skipped += 1
        continue
    
    try:
        start_time = time.time()
        
        # Determine title based on filename
        filename = video_path.stem
        if "fedspeech1" in filename.lower():
            title = "Federal Reserve Speech #1"
            campaign = "Fed 2025"
        elif "fedspeech2" in filename.lower():
            title = "Federal Reserve Speech #2"
            campaign = "Fed 2025"
        elif "fedspeech3" in filename.lower():
            title = "Federal Reserve Speech #3"
            campaign = "Fed 2025"
        else:
            title = video_path.stem.replace("_", " ").title()
            campaign = "Campaign 2025"
        
        # Process video
        video_id = process_video(
            str(video_path),
            db_path=db_path,
            title=title,
            campaign=campaign
        )
        
        elapsed = time.time() - start_time
        print(f"\n✓ SUCCESS! Processed in {elapsed:.1f}s")
        processed += 1
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        failed += 1
        import traceback
        traceback.print_exc()

# Final summary
print(f"\n{'='*70}")
print("PROCESSING COMPLETE")
print(f"{'='*70}\n")
print(f"Processed: {processed}")
print(f"Skipped:   {skipped} (already in database)")
print(f"Failed:    {failed}")
print(f"Total:     {len(video_files)}")

# Show updated database stats
print(f"\n{'='*70}")
print("UPDATED DATABASE")
print(f"{'='*70}\n")

db = VideoDatabase(db_path)
stats = db.get_stats()

print(f"Total videos:       {stats['total_videos']}")
print(f"Total fingerprints: {stats['total_fingerprints']}")
print(f"Total duration:     {stats['total_duration']:.1f}s ({stats['total_duration']/60:.1f} minutes)")
print(f"Avg fingerprints:   {stats['avg_fingerprints_per_video']:.1f} per video")

print(f"\n{'='*70}")
print("View database: python3.10 video_processor.py --list")
print(f"{'='*70}\n")

