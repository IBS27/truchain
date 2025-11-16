#!/usr/bin/env python3
"""
Test if heavily compressed videos contain same content.
Creates audio samples for manual verification + tests with lower thresholds.
"""

import subprocess
from pathlib import Path
from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase
from verification import VideoVerifier

print("="*70)
print("TESTING FOR SAME CONTENT WITH HEAVY COMPRESSION")
print("="*70 + "\n")

# Extract 10-second audio samples from each video at 5:00 mark
sample_dir = Path("audio_samples")
sample_dir.mkdir(exist_ok=True)

videos = [
    ("download/fedspeech1.mp4", "Video #1"),
    ("download/fedspeech2.mp4", "Video #2"),
    ("download/fedspeech3.mp4", "Video #3")
]

print("Extracting 10-second audio samples from 5:00 mark...\n")

samples = []
for video_path, name in videos:
    if not Path(video_path).exists():
        print(f"⊘ {name} not found")
        continue
    
    output = sample_dir / f"{Path(video_path).stem}_sample.wav"
    
    cmd = [
        'ffmpeg', '-i', video_path, '-ss', '300', '-t', '10',
        '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
        '-y', str(output)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    samples.append((output, name))
    print(f"✓ {name}: {output}")

print(f"\n{'='*70}")
print("MANUAL VERIFICATION")
print(f"{'='*70}\n")

print("Audio samples saved to: audio_samples/")
print("\nTo manually verify if they're the same:")
print("  1. Listen to: audio_samples/fedspeech1_sample.wav")
print("  2. Listen to: audio_samples/fedspeech2_sample.wav")
print("  3. Listen to: audio_samples/fedspeech3_sample.wav")
print("\nIf they sound the same, the videos contain same speech.")

# Now test with various lower thresholds
print(f"\n{'='*70}")
print("TESTING WITH MULTIPLE THRESHOLDS")
print(f"{'='*70}\n")

# Create a test clip from video 1
test_clip = "test_compression_clip.mp4"
cmd = [
    'ffmpeg', '-i', 'download/fedspeech1.mp4', '-ss', '300', '-t', '20',
    '-c', 'copy', '-y', test_clip
]
subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

print("Created test clip from Video #1 at 5:00 mark\n")

# Test with different thresholds
thresholds = [0.85, 0.75, 0.70, 0.65, 0.60, 0.55]

verifier = VideoVerifier("video_database.json")
db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

results = {}

for threshold in thresholds:
    print(f"Testing with threshold: {threshold:.0%}")
    print(f"{'─'*70}")
    
    matches = verifier.verify_clip(test_clip, threshold=threshold, min_consecutive_matches=1)
    
    matched_videos = set()
    if matches:
        for match in matches:
            matched_videos.add(match.video_title)
            print(f"  ✓ {match.video_title} ({match.confidence:.1%})")
    else:
        print(f"  ✗ No matches")
    
    results[threshold] = matched_videos
    print()

# Analysis
print(f"{'='*70}")
print("ANALYSIS")
print(f"{'='*70}\n")

print("Matches at different thresholds:\n")
for threshold, matched in results.items():
    count = len(matched)
    print(f"  {threshold:.0%}: {count}/3 videos matched")
    if matched:
        for v in matched:
            print(f"      • {v}")

# Find optimal threshold
optimal_threshold = None
for threshold in thresholds:
    if len(results[threshold]) == 3:
        optimal_threshold = threshold
        break

print(f"\n{'='*70}")

if optimal_threshold:
    print(f"✅ SOLUTION FOUND!")
    print(f"{'='*70}\n")
    print(f"  Use threshold: {optimal_threshold:.0%}")
    print(f"  At this threshold, clips will match all 3 videos")
    print(f"\n  To use this threshold:")
    print(f"    python3.10 verification.py clip.mp4 --threshold {optimal_threshold}")
else:
    max_matches = max(len(v) for v in results.values())
    best_threshold = [t for t, v in results.items() if len(v) == max_matches][0]
    
    print(f"⚠️ PARTIAL SOLUTION")
    print(f"{'='*70}\n")
    print(f"  Best threshold: {best_threshold:.0%}")
    print(f"  Matches {max_matches}/3 videos")
    
    if max_matches == 1:
        print(f"\n  Videos appear to be DIFFERENT content")
        print(f"  Even at low thresholds, only original video matches")
    else:
        print(f"\n  Some videos match at {best_threshold:.0%}")
        print(f"  Other videos might have heavy compression/processing")

print(f"\n{'='*70}\n")

# Cleanup
import os
if os.path.exists(test_clip):
    os.remove(test_clip)

