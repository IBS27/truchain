#!/usr/bin/env python3
"""
Show EXACT similarity scores for a clip against all videos.
No threshold filtering - shows raw numbers.
"""

import sys
from pathlib import Path
from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase
from verification import VideoVerifier

if len(sys.argv) < 2:
    print("Usage: python3.10 show_exact_similarity.py <clip_file>")
    sys.exit(1)

clip_path = sys.argv[1]

if not Path(clip_path).exists():
    print(f"Error: File not found: {clip_path}")
    sys.exit(1)

print("="*70)
print("EXACT SIMILARITY SCORES (NO THRESHOLD)")
print("="*70)
print(f"\nClip: {clip_path}\n")

# Load database
db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

print(f"Testing against {len(all_videos)} videos:\n")

# Generate fingerprints for clip
print("Processing clip...")
fingerprinter = AudioFingerprinter(clip_path)
clip_fps = fingerprinter.generate_fingerprints()
print(f"✓ Generated {len(clip_fps)} fingerprints\n")

# Create verifier
verifier = VideoVerifier("video_database.json")

print("="*70)
print("DETAILED SIMILARITY SCORES")
print("="*70)

# Test against each video
for video_idx, video in enumerate(all_videos, 1):
    print(f"\n{'─'*70}")
    print(f"VIDEO {video_idx}: {video['title']}")
    print(f"{'─'*70}\n")
    
    video_fps = video['fingerprints']
    
    # For each clip fingerprint, find best match in video
    all_similarities = []
    
    for clip_fp_idx, clip_fp in enumerate(clip_fps):
        best_similarity = 0
        best_video_timestamp = -1
        
        for video_fp in video_fps:
            similarity = verifier.calculate_similarity(clip_fp, video_fp)
            if similarity > best_similarity:
                best_similarity = similarity
                best_video_timestamp = video_fp['timestamp']
        
        all_similarities.append({
            'clip_time': clip_fp['timestamp'],
            'best_similarity': best_similarity,
            'video_time': best_video_timestamp
        })
        
        clip_min = int(clip_fp['timestamp'] // 60)
        clip_sec = int(clip_fp['timestamp'] % 60)
        video_min = int(best_video_timestamp // 60)
        video_sec = int(best_video_timestamp % 60)
        
        print(f"  Clip fingerprint {clip_fp_idx + 1} ({clip_min:2d}:{clip_sec:02d}):")
        print(f"    Best match: {best_similarity:.2%} at video {video_min:2d}:{video_sec:02d}")
    
    # Calculate average
    avg_similarity = sum(s['best_similarity'] for s in all_similarities) / len(all_similarities)
    
    print(f"\n  {'─'*66}")
    print(f"  AVERAGE SIMILARITY: {avg_similarity:.2%}")
    print(f"  {'─'*66}")
    
    # Show interpretation
    if avg_similarity >= 0.95:
        print(f"  → 🎯 PERFECT MATCH (same content, same source)")
    elif avg_similarity >= 0.85:
        print(f"  → ✅ STRONG MATCH (very likely same content)")
    elif avg_similarity >= 0.75:
        print(f"  → ⚠️ MODERATE MATCH (possibly same content, different encoding)")
    elif avg_similarity >= 0.65:
        print(f"  → ⚠️ WEAK MATCH (similar but different)")
    else:
        print(f"  → ✗ NO MATCH (different content)")

print("\n" + "="*70)
print("COMPARISON SUMMARY")
print("="*70 + "\n")

# Summary table
for video_idx, video in enumerate(all_videos, 1):
    video_fps = video['fingerprints']
    
    # Calculate average similarity
    total = 0
    for clip_fp in clip_fps:
        best = max(verifier.calculate_similarity(clip_fp, video_fp) 
                  for video_fp in video_fps)
        total += best
    
    avg = total / len(clip_fps)
    
    # Status
    if avg >= 0.85:
        status = "✅ MATCH"
    elif avg >= 0.65:
        status = "⚠️ SIMILAR"
    else:
        status = "✗ DIFFERENT"
    
    print(f"{video_idx}. {video['title']}")
    print(f"   Avg similarity: {avg:.2%}  ({status})")

print("\n" + "="*70 + "\n")

