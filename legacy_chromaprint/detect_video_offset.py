#!/usr/bin/env python3
"""
Detect time offset between videos with same content.
Handles cases where same speech has different start times.
"""

from video_processor import VideoDatabase
from verification import VideoVerifier
import numpy as np

def find_best_alignment(video1_fps, video2_fps, verifier, sample_size=20):
    """
    Find the time offset between two videos by testing different alignments.
    Returns (offset, avg_similarity) where offset is the time difference.
    """
    # Sample fingerprints from video1 (skip first/last 10% to avoid intros/outros)
    start_idx = len(video1_fps) // 10
    end_idx = len(video1_fps) - len(video1_fps) // 10
    
    if end_idx - start_idx < sample_size:
        sample_size = max(5, end_idx - start_idx)
    
    sample_indices = np.linspace(start_idx, end_idx - 1, sample_size, dtype=int)
    samples = [video1_fps[i] for i in sample_indices]
    
    # Try different offsets (from -300s to +300s, in 5s steps)
    best_offset = 0
    best_avg_similarity = 0
    
    offset_range = range(-60, 61)  # -300s to +300s (60 * 5s steps)
    
    for offset_steps in offset_range:
        total_similarity = 0
        valid_comparisons = 0
        
        for sample in samples:
            sample_idx = int(sample['timestamp'] / 5)
            target_idx = sample_idx + offset_steps
            
            if 0 <= target_idx < len(video2_fps):
                similarity = verifier.calculate_similarity(
                    sample,
                    video2_fps[target_idx]
                )
                total_similarity += similarity
                valid_comparisons += 1
        
        if valid_comparisons > 0:
            avg_similarity = total_similarity / valid_comparisons
            
            if avg_similarity > best_avg_similarity:
                best_avg_similarity = avg_similarity
                best_offset = offset_steps * 5  # Convert to seconds
    
    return best_offset, best_avg_similarity

print("="*70)
print("DETECTING TIME OFFSETS BETWEEN VIDEOS")
print("="*70)
print("\nThis finds if videos contain same content at different timestamps\n")

db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

if len(all_videos) < 2:
    print("Need at least 2 videos in database")
    exit(1)

print(f"Analyzing {len(all_videos)} videos:\n")
for i, v in enumerate(all_videos, 1):
    print(f"  {i}. {v['title']} ({v['duration']/60:.1f} min, {len(v['fingerprints'])} fingerprints)")

verifier = VideoVerifier("video_database.json")

print("\n" + "="*70)
print("COMPARING ALL VIDEO PAIRS")
print("="*70)

# Compare each pair of videos
video1 = all_videos[0]
video1_fps = video1['fingerprints']

for video_idx in range(1, len(all_videos)):
    video2 = all_videos[video_idx]
    video2_fps = video2['fingerprints']
    
    print(f"\n{'─'*70}")
    print(f"Comparing: {video1['title']}")
    print(f"      vs:  {video2['title']}")
    print(f"{'─'*70}\n")
    
    print("Searching for best time alignment...")
    offset, similarity = find_best_alignment(video1_fps, video2_fps, verifier)
    
    print(f"\n  Best alignment found:")
    print(f"    Time offset: {offset}s")
    print(f"    Avg similarity: {similarity:.1%}")
    
    if similarity >= 0.85:
        print(f"\n  ✅ SAME CONTENT DETECTED!")
        if offset == 0:
            print(f"     Videos start at the same time")
        elif offset > 0:
            print(f"     Video #1 starts {offset}s AFTER Video #{video_idx + 1}")
        else:
            print(f"     Video #1 starts {abs(offset)}s BEFORE Video #{video_idx + 1}")
    elif similarity >= 0.75:
        print(f"\n  ⚠️ LIKELY SAME CONTENT (with degradation)")
        if offset == 0:
            print(f"     Videos start at the same time")
        elif offset > 0:
            print(f"     Video #1 starts {offset}s AFTER Video #{video_idx + 1}")
        else:
            print(f"     Video #1 starts {abs(offset)}s BEFORE Video #{video_idx + 1}")
    else:
        print(f"\n  ✗ DIFFERENT CONTENT")
        print(f"     Videos contain different speeches")

print("\n" + "="*70)
print("SUMMARY")
print("="*70 + "\n")

# Check all pairs
same_content_pairs = []

for i in range(len(all_videos)):
    for j in range(i + 1, len(all_videos)):
        video_i_fps = all_videos[i]['fingerprints']
        video_j_fps = all_videos[j]['fingerprints']
        
        offset, similarity = find_best_alignment(video_i_fps, video_j_fps, verifier)
        
        if similarity >= 0.75:
            same_content_pairs.append({
                'video1': all_videos[i]['title'],
                'video2': all_videos[j]['title'],
                'offset': offset,
                'similarity': similarity
            })

if same_content_pairs:
    print(f"Found {len(same_content_pairs)} pair(s) with same content:\n")
    for pair in same_content_pairs:
        print(f"  • {pair['video1']}")
        print(f"    = {pair['video2']}")
        print(f"    Offset: {pair['offset']}s, Similarity: {pair['similarity']:.1%}\n")
    
    print("Recommendation:")
    print("  ✓ These videos contain the same speech")
    print("  ✓ A clip from one should match all of them")
    print("  ✓ Use threshold 0.75-0.85 depending on quality")
else:
    print("No videos with same content detected")
    print("All videos contain different speeches")

print("\n" + "="*70 + "\n")

