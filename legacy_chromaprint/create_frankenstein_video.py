#!/usr/bin/env python3
"""
Create a 'Frankenstein' video by splicing together clips from different parts.
This simulates edited videos that create false narratives.
"""

import subprocess
import os
from pathlib import Path
import random

video_path = "download/fedspeech1.mp4"
clips_dir = Path("frankenstein_clips")
clips_dir.mkdir(exist_ok=True)

print("="*70)
print("CREATING FRANKENSTEIN VIDEO")
print("Testing edge case: Spliced clips from different timestamps")
print("="*70)

# Get video duration
cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
       '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
duration = float(result.stdout.strip())

print(f"\nOriginal video duration: {duration:.1f}s")
print(f"Creating 20 clips of 1 second each from different timestamps\n")

# Generate 20 random timestamps spread across the video
# Avoid first and last 30 seconds to ensure clean extraction
timestamps = sorted(random.sample(range(30, int(duration) - 30), 20))

clip_files = []

print("Extracting clips:")
for i, timestamp in enumerate(timestamps, 1):
    clip_name = f"segment_{i:02d}.mp4"
    clip_path = clips_dir / clip_name
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(timestamp),
        '-t', '1',  # 1 second
        '-c:v', 'libx264',  # Re-encode to ensure consistency
        '-c:a', 'aac',
        '-y',
        str(clip_path)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    clip_files.append(str(clip_path))
    
    minutes = timestamp // 60
    seconds = timestamp % 60
    print(f"  [{i:2d}/20] Timestamp {timestamp:4d}s ({minutes:2d}:{seconds:02d}) -> {clip_name}")

# Create concat file for ffmpeg with absolute paths
concat_file = clips_dir / "concat_list.txt"
with open(concat_file, 'w') as f:
    for clip_file in clip_files:
        # Use absolute path
        abs_path = Path(clip_file).absolute()
        f.write(f"file '{abs_path}'\n")

# Concatenate all clips
output_path = clips_dir / "frankenstein_video.mp4"

print(f"\nMerging {len(clip_files)} clips into one video...")

cmd = [
    'ffmpeg',
    '-f', 'concat',
    '-safe', '0',
    '-i', str(concat_file),
    '-c', 'copy',
    '-y',
    str(output_path)
]

subprocess.run(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True
)

# Get output file size
output_size = output_path.stat().st_size / (1024 * 1024)

print(f"\n{'='*70}")
print("FRANKENSTEIN VIDEO CREATED!")
print(f"{'='*70}")
print(f"\nOutput: {output_path}")
print(f"Size: {output_size:.2f} MB")
print(f"Duration: ~20 seconds (20 x 1-second clips)")
print(f"\nClips are from these timestamps:")

# Show timestamp distribution
for i, ts in enumerate(timestamps, 1):
    minutes = ts // 60
    seconds = ts % 60
    print(f"  Segment {i:2d}: {minutes:2d}:{seconds:02d} ({ts}s)")

print(f"\n{'='*70}")
print("EDGE CASE TO TEST:")
print(f"{'='*70}")
print("This video contains REAL audio from the original video,")
print("but spliced from 20 different timestamps.")
print("\nExpected behavior:")
print("  • System should detect multiple matches")
print("  • BUT timestamps should be scattered/non-continuous")
print("  • This reveals the video is edited/manipulated")
print("\nVerify with:")
print(f"  python3.10 verification.py {output_path}")
print(f"{'='*70}\n")

# Save timestamp information
timestamp_file = clips_dir / "timestamps.txt"
with open(timestamp_file, 'w') as f:
    f.write("FRANKENSTEIN VIDEO - Source Timestamps\n")
    f.write("="*50 + "\n\n")
    for i, ts in enumerate(timestamps, 1):
        minutes = ts // 60
        seconds = ts % 60
        f.write(f"Segment {i:2d}: {minutes:2d}:{seconds:02d} ({ts}s)\n")

print(f"Timestamp information saved to: {timestamp_file}")

