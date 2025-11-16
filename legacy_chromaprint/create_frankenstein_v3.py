#!/usr/bin/env python3
"""
Frankenstein V3: Longer clips (10-15 seconds) that should match
but reveal scattered timestamps, showing the video is edited.
"""

import subprocess
from pathlib import Path

video_path = "download/fedspeech1.mp4"
clips_dir = Path("frankenstein_clips_v3")
clips_dir.mkdir(exist_ok=True)

print("="*70)
print("CREATING FRANKENSTEIN VIDEO V3")
print("Testing: Longer clips (10-15s) to demonstrate editing detection")
print("="*70)

# Create 5 clips from vastly different timestamps
# These are long enough to match but from completely different parts
timestamps_and_durations = [
    (200, 12),   # 3:20 for 12 seconds
    (800, 15),   # 13:20 for 15 seconds
    (1400, 10),  # 23:20 for 10 seconds
    (2000, 12),  # 33:20 for 12 seconds
    (2600, 11),  # 43:20 for 11 seconds
]

print(f"\nCreating {len(timestamps_and_durations)} clips:\n")

clip_files = []

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
    print(f"  [{i}/5] {minutes:2d}:{seconds:02d} for {clip_duration}s -> {clip_name}")

# Concat
concat_file = clips_dir / "concat_list.txt"
with open(concat_file, 'w') as f:
    for clip_file in clip_files:
        f.write(f"file '{Path(clip_file).name}'\n")

output_path = clips_dir / "frankenstein_v3.mp4"

print(f"\nMerging clips...")

subprocess.run(
    ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'concat_list.txt',
     '-c', 'copy', '-y', 'frankenstein_v3.mp4'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True,
    cwd=str(clips_dir)
)

output_size = output_path.stat().st_size / (1024 * 1024)
total_duration = sum(d for _, d in timestamps_and_durations)

print(f"\n{'='*70}")
print("FRANKENSTEIN V3 CREATED!")
print(f"{'='*70}")
print(f"\nOutput: {output_path}")
print(f"Size: {output_size:.2f} MB")
print(f"Total duration: {total_duration} seconds (~1 minute)\n")

print("Source timestamps (SCATTERED across video):")
for i, (ts, dur) in enumerate(timestamps_and_durations, 1):
    mins = ts // 60
    secs = ts % 60
    end_ts = ts + dur
    end_mins = end_ts // 60
    end_secs = end_ts % 60
    print(f"  Segment {i}: {mins:2d}:{secs:02d} - {end_mins:2d}:{end_secs:02d} (from {ts}s, {dur}s)")

# Save info
timestamp_file = clips_dir / "timestamps.txt"
with open(timestamp_file, 'w') as f:
    f.write("FRANKENSTEIN V3 - Source Timestamps\n")
    f.write("="*50 + "\n\n")
    f.write("This video splices together clips from:\n\n")
    for i, (ts, dur) in enumerate(timestamps_and_durations, 1):
        mins = ts // 60
        secs = ts % 60
        f.write(f"Segment {i}: {mins:2d}:{secs:02d} ({ts}s) for {dur}s\n")
    f.write("\nThese timestamps are scattered across the 55-minute video.\n")
    f.write("If the system detects multiple matches at different timestamps,\n")
    f.write("this reveals the video has been EDITED.\n")

print(f"\n{'='*70}")
print("EXPECTED RESULT:")
print(f"{'='*70}")
print("With 10-15 second clips, the system SHOULD:")
print("  ✓ Detect multiple matches")
print("  ✓ Show timestamps at: ~200s, ~800s, ~1400s, ~2000s, ~2600s")
print("  ✓ Reveal the video is SPLICED from different parts")
print("  ✓ Flag as potentially manipulated content")
print("\nThis demonstrates the system can detect edited videos!")
print(f"{'='*70}\n")

