#!/usr/bin/env python3
"""
Create test clips and verify them.
Shows different scenarios and results.
"""

import subprocess
import os
from pathlib import Path

# Create test_clips directory
clips_dir = Path("test_clips")
clips_dir.mkdir(exist_ok=True)

video_path = "download/fedspeech1.mp4"

print("="*70)
print("Creating Test Clips from Federal Reserve Speech")
print("="*70)

# Define test clips with different characteristics
test_clips = [
    {
        "name": "clip1_beginning_20s.mp4",
        "start": 30,
        "duration": 20,
        "description": "20-second clip from beginning (30s mark)",
        "command_extra": ["-c", "copy"]  # Fast copy, no re-encoding
    },
    {
        "name": "clip2_middle_30s.mp4",
        "start": 600,
        "duration": 30,
        "description": "30-second clip from middle (10 minutes in)",
        "command_extra": ["-c", "copy"]
    },
    {
        "name": "clip3_end_15s.mp4",
        "start": 3000,
        "duration": 15,
        "description": "15-second clip near end (50 minutes in)",
        "command_extra": ["-c", "copy"]
    },
    {
        "name": "clip4_degraded_25s.mp4",
        "start": 1200,
        "duration": 25,
        "description": "25-second degraded quality clip (20 minutes in, lower bitrate, mono)",
        "command_extra": ["-b:a", "64k", "-ac", "1"]  # Lower quality
    },
    {
        "name": "clip5_short_10s.mp4",
        "start": 1800,
        "duration": 10,
        "description": "10-second short clip (30 minutes in)",
        "command_extra": ["-c", "copy"]
    }
]

# Create each clip
for idx, clip_info in enumerate(test_clips, 1):
    print(f"\n[{idx}/{len(test_clips)}] Creating: {clip_info['name']}")
    print(f"    Description: {clip_info['description']}")
    
    output_path = clips_dir / clip_info['name']
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(clip_info['start']),
        '-t', str(clip_info['duration']),
        *clip_info['command_extra'],
        '-y',
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # Get file size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"    ✓ Created successfully ({size_mb:.2f} MB)")
        
    except subprocess.CalledProcessError as e:
        print(f"    ✗ Failed to create clip")

print("\n" + "="*70)
print("Test Clips Created Successfully!")
print("="*70)
print(f"\nLocation: {clips_dir}/")
print("\nCreated clips:")
for clip_info in test_clips:
    clip_path = clips_dir / clip_info['name']
    if clip_path.exists():
        size_mb = clip_path.stat().st_size / (1024 * 1024)
        print(f"  • {clip_info['name']} ({size_mb:.2f} MB)")
        print(f"    Start: {clip_info['start']}s, Duration: {clip_info['duration']}s")

print("\n" + "="*70)
print("To verify a clip, run:")
print("  python3.10 verification.py test_clips/<clip_name>")
print("="*70)

