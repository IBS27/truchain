#!/usr/bin/env python3
"""
Debug why clips from same speech aren't matching all videos.
Shows similarity scores across all videos to diagnose the issue.
"""

from pathlib import Path
from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase
from verification import VideoVerifier

print("="*70)
print("DEBUGGING SAME CONTENT ACROSS DIFFERENT UPLOADS")
print("="*70)

# Load database
db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

print(f"\nDatabase has {len(all_videos)} videos\n")

# Create a clip from video 1 at 3:00 mark
print("Creating test clip from Video #1 at 3:00 (180s)...")
import subprocess

test_clip = "debug_test_clip.mp4"
cmd = [
    'ffmpeg', '-i', 'download/fedspeech1.mp4', '-ss', '180', '-t', '20',
    '-c', 'copy', '-y', test_clip
]
subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
print(f"✓ Created: {test_clip}\n")

# Generate fingerprints
print("Generating fingerprints for test clip...")
fp_test = AudioFingerprinter(test_clip)
test_fps = fp_test.generate_fingerprints()
print(f"✓ Generated {len(test_fps)} fingerprints\n")

# Create verifier
verifier = VideoVerifier("video_database.json")

print("="*70)
print("COMPARING AGAINST EACH VIDEO")
print("="*70)

for video_idx, video in enumerate(all_videos, 1):
    print(f"\n{'─'*70}")
    print(f"VIDEO {video_idx}: {video['title']}")
    print(f"{'─'*70}\n")
    
    video_fps = video['fingerprints']
    
    # Check each test fingerprint against this video
    print("Checking similarity at 180s mark (where clip was extracted):")
    
    # Test fingerprint should match around index 36 (180s / 5s intervals)
    expected_idx = 36  # 180 / 5
    
    for test_idx, test_fp in enumerate(test_fps[:3]):  # Check first 3 fingerprints
        test_time = test_fp['timestamp']
        
        # Check against expected position in video
        video_idx_to_check = expected_idx + test_idx
        
        if video_idx_to_check < len(video_fps):
            video_fp = video_fps[video_idx_to_check]
            similarity = verifier.calculate_similarity(test_fp, video_fp)
            
            print(f"  Test fingerprint {test_idx} ({test_time}s) vs Video position {video_fp['timestamp']}s:")
            print(f"    Similarity: {similarity:.2%}")
            
            if similarity >= 0.85:
                print(f"    ✓ MATCH (≥85%)")
            elif similarity >= 0.75:
                print(f"    ⚠️ Close (≥75%, might match with lower threshold)")
            else:
                print(f"    ✗ Too different (<75%)")
    
    # Also search for best match in entire video
    print(f"\n  Searching entire video for best match...")
    best_similarity = 0
    best_idx = -1
    
    for vid_idx, video_fp in enumerate(video_fps):
        similarity = verifier.calculate_similarity(test_fps[0], video_fp)
        if similarity > best_similarity:
            best_similarity = similarity
            best_idx = vid_idx
    
    print(f"  Best match: {best_similarity:.2%} at {video_fps[best_idx]['timestamp']}s")
    
    if best_similarity >= 0.85:
        print(f"  ✓ Would match with 85% threshold")
    elif best_similarity >= 0.75:
        print(f"  ⚠️ Would match with 75% threshold")
    elif best_similarity >= 0.65:
        print(f"  ⚠️ Would need 65% threshold")
    else:
        print(f"  ✗ Very different content (even at low thresholds)")

print("\n" + "="*70)
print("ANALYSIS")
print("="*70 + "\n")

print("If all 3 videos are the same speech:")
print("  • They should all show ≥85% similarity at the same timestamp")
print("  • If only 1-2 match, it means different encodings/quality")
print("\nRecommendations:")
print("  1. If similarities are 75-85%: Lower threshold to 0.75")
print("  2. If similarities are 65-75%: Use 0.70 for same-content detection")
print("  3. If similarities are <65%: Videos might have different audio processing")

print("\n" + "="*70 + "\n")

# Cleanup
import os
if os.path.exists(test_clip):
    os.remove(test_clip)
    print(f"Cleaned up: {test_clip}\n")

