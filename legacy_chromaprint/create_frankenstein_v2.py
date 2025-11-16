#!/usr/bin/env python3
"""
Create a more sophisticated Frankenstein video with longer clips (3-5 seconds).
This tests if the system can detect editing through scattered timestamps.
"""

import subprocess
from pathlib import Path
import random

video_path = "download/fedspeech1.mp4"
clips_dir = Path("frankenstein_clips_v2")
clips_dir.mkdir(exist_ok=True)

print("="*70)
print("CREATING FRANKENSTEIN VIDEO V2")
print("Testing: Longer clips (3-5 seconds) for better detection")
print("="*70)

# Get video duration
cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
       '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
duration = float(result.stdout.strip())

print(f"\nOriginal video duration: {duration:.1f}s")

# Create 10 clips of varying lengths (3-5 seconds) from scattered timestamps
timestamps_and_durations = [
    (100, 4),   # 1:40 for 4 seconds
    (500, 5),   # 8:20 for 5 seconds
    (900, 3),   # 15:00 for 3 seconds
    (1200, 4),  # 20:00 for 4 seconds
    (1500, 5),  # 25:00 for 5 seconds
    (1800, 3),  # 30:00 for 3 seconds
    (2100, 4),  # 35:00 for 4 seconds
    (2400, 5),  # 40:00 for 5 seconds
    (2700, 3),  # 45:00 for 3 seconds
    (3000, 4),  # 50:00 for 4 seconds
]

print(f"Creating {len(timestamps_and_durations)} clips with 3-5 second lengths\n")

clip_files = []

print("Extracting clips:")
for i, (timestamp, clip_duration) in enumerate(timestamps_and_durations, 1):
    clip_name = f"segment_{i:02d}.mp4"
    clip_path = clips_dir / clip_name
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(timestamp),
        '-t', str(clip_duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y',
        str(clip_path)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    clip_files.append(str(clip_path))
    
    minutes = timestamp // 60
    seconds = timestamp % 60
    print(f"  [{i:2d}/10] {minutes:2d}:{seconds:02d} for {clip_duration}s -> {clip_name}")

# Create concat file
concat_file = clips_dir / "concat_list.txt"
with open(concat_file, 'w') as f:
    for clip_file in clip_files:
        f.write(f"file '{Path(clip_file).name}'\n")

# Concatenate all clips
output_path = clips_dir / "frankenstein_v2.mp4"

print(f"\nMerging {len(clip_files)} clips...")

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
    check=True,
    cwd=str(clips_dir)
)

output_size = output_path.stat().st_size / (1024 * 1024)
total_duration = sum(d for _, d in timestamps_and_durations)

print(f"\n{'='*70}")
print("FRANKENSTEIN V2 CREATED!")
print(f"{'='*70}")
print(f"\nOutput: {output_path}")
print(f"Size: {output_size:.2f} MB")
print(f"Total duration: {total_duration} seconds")
print(f"\nSource timestamps:")

for i, (ts, dur) in enumerate(timestamps_and_durations, 1):
    mins = ts // 60
    secs = ts % 60
    print(f"  Segment {i:2d}: {mins:2d}:{secs:02d} ({ts}s) - {dur}s")

# Save timestamp info
timestamp_file = clips_dir / "timestamps.txt"
with open(timestamp_file, 'w') as f:
    f.write("FRANKENSTEIN V2 - Source Timestamps\n")
    f.write("="*50 + "\n\n")
    for i, (ts, dur) in enumerate(timestamps_and_durations, 1):
        mins = ts // 60
        secs = ts % 60
        f.write(f"Segment {i:2d}: {mins:2d}:{secs:02d} ({ts}s) - Duration: {dur}s\n")

print(f"\n{'='*70}")
print("EDGE CASE V2:")
print(f"{'='*70}")
print("Longer clips (3-5s each) should match better.")
print("Expected behavior:")
print("  • System SHOULD detect matches")
print("  • Timestamps will be SCATTERED (100s, 500s, 900s, etc.)")
print("  • This reveals the video is EDITED")
print("\nVerify with:")
print(f"  python3.10 verification.py {output_path}")
print(f"{'='*70}\n")

