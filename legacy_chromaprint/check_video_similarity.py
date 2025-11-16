#!/usr/bin/env python3
"""
Check if videos contain the same content by sampling multiple points.
This determines if they're truly the same speech or different content.
"""

from video_processor import VideoDatabase
from verification import VideoVerifier

print("="*70)
print("CHECKING IF VIDEOS CONTAIN SAME CONTENT")
print("="*70 + "\n")

db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

if len(all_videos) < 2:
    print("Need at least 2 videos in database")
    exit(1)

print(f"Comparing {len(all_videos)} videos:\n")
for i, v in enumerate(all_videos, 1):
    print(f"  {i}. {v['title']} ({v['duration']/60:.1f} min)")

verifier = VideoVerifier("video_database.json")

print("\n" + "="*70)
print("SAMPLING FINGERPRINTS FROM EACH VIDEO")
print("="*70 + "\n")

# Sample fingerprints from different points in each video
sample_points = [36, 120, 240, 400]  # Indices (= timestamps / 5)

# Get sample fingerprints from Video 1
video1_fps = all_videos[0]['fingerprints']
video1_samples = []

print(f"Sampling from Video #1: {all_videos[0]['title']}")
for idx in sample_points:
    if idx < len(video1_fps):
        fp = video1_fps[idx]
        video1_samples.append(fp)
        print(f"  Sample at {fp['timestamp']}s")

print(f"\n{len(video1_samples)} samples collected\n")

# Compare against each other video
print("="*70)
print("COMPARING SAMPLES AGAINST OTHER VIDEOS")
print("="*70)

for video_idx in range(1, len(all_videos)):
    video = all_videos[video_idx]
    print(f"\n{'─'*70}")
    print(f"VIDEO #{video_idx + 1}: {video['title']}")
    print(f"{'─'*70}\n")
    
    video_fps = video['fingerprints']
    
    # For each sample, find best match in this video
    total_best_similarity = 0
    matches_above_80 = 0
    
    for sample_idx, sample_fp in enumerate(video1_samples):
        best_similarity = 0
        best_timestamp = -1
        
        # Search entire video
        for vid_fp in video_fps:
            similarity = verifier.calculate_similarity(sample_fp, vid_fp)
            if similarity > best_similarity:
                best_similarity = similarity
                best_timestamp = vid_fp['timestamp']
        
        total_best_similarity += best_similarity
        if best_similarity >= 0.80:
            matches_above_80 += 1
        
        status = "✓" if best_similarity >= 0.85 else "⚠️" if best_similarity >= 0.75 else "✗"
        
        print(f"  Sample {sample_idx + 1} (from {sample_fp['timestamp']}s):")
        print(f"    {status} Best match: {best_similarity:.1%} at {best_timestamp}s")
    
    avg_similarity = total_best_similarity / len(video1_samples)
    
    print(f"\n  Average best match: {avg_similarity:.1%}")
    print(f"  Matches ≥80%: {matches_above_80}/{len(video1_samples)}")
    
    if avg_similarity >= 0.85:
        print(f"  ✅ SAME CONTENT - Videos contain same speech")
    elif avg_similarity >= 0.70:
        print(f"  ⚠️ SIMILAR - Possibly same speech with heavy processing")
    else:
        print(f"  ✗ DIFFERENT - Videos contain different content")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70 + "\n")

print("If videos are the SAME speech:")
print("  • Average similarity should be ≥85%")
print("  • Most samples should match at similar timestamps")
print("\nIf videos are DIFFERENT speeches:")
print("  • Average similarity will be <70%")
print("  • Samples will match at random scattered timestamps")
print("\nCurrent findings suggest:")

avg_similarities = []
for video_idx in range(1, len(all_videos)):
    video_fps = all_videos[video_idx]['fingerprints']
    total = 0
    for sample_fp in video1_samples:
        best = max(verifier.calculate_similarity(sample_fp, vid_fp) 
                  for vid_fp in video_fps)
        total += best
    avg = total / len(video1_samples)
    avg_similarities.append(avg)

if all(sim >= 0.85 for sim in avg_similarities):
    print("  ✅ All videos contain the SAME speech")
    print("  → System should match clips to all videos")
    print("  → Threshold of 0.85 works for all")
elif any(sim >= 0.70 for sim in avg_similarities):
    print("  ⚠️ Some videos might be same speech with different encoding")
    print("  → Try threshold of 0.70-0.75 for those videos")
else:
    print("  ✗ Videos appear to be DIFFERENT speeches")
    print("  → This is expected behavior")
    print("  → Each clip should only match its source video")

print("\n" + "="*70 + "\n")

