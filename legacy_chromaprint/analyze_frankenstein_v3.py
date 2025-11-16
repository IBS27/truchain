#!/usr/bin/env python3
"""
Detailed analysis of Frankenstein V3 to show ALL matching segments.
"""

from pathlib import Path
from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase
from verification import VideoVerifier

print("\n" + "="*70)
print("FRANKENSTEIN V3 - DETAILED ANALYSIS")
print("="*70)

# Load expected timestamps
timestamps_file = "frankenstein_clips_v3/timestamps.txt"
print("\nEXPECTED SOURCE TIMESTAMPS:")
print("="*70)
if Path(timestamps_file).exists():
    with open(timestamps_file, 'r') as f:
        for line in f.readlines()[3:8]:  # Get the timestamp lines
            print(f"  {line.strip()}")
else:
    print("  Segment 1:  3:20 (200s) for 12s")
    print("  Segment 2: 13:20 (800s) for 15s")
    print("  Segment 3: 23:20 (1400s) for 10s")
    print("  Segment 4: 33:20 (2000s) for 12s")
    print("  Segment 5: 43:20 (2600s) for 11s")

# Generate fingerprints for frankenstein video
frank_path = "frankenstein_clips_v3/frankenstein_v3.mp4"
print(f"\n{'='*70}")
print("GENERATING FINGERPRINTS")
print("="*70)

print("\nProcessing Frankenstein video...")
fp_frank = AudioFingerprinter(frank_path)
frank_fps = fp_frank.generate_fingerprints()

print(f"Generated {len(frank_fps)} fingerprints from Frankenstein video")

# Load database
print("\nLoading original video fingerprints from database...")
db = VideoDatabase("video_database.json")
orig_video = db.get_all_videos()[0]
orig_fps = orig_video['fingerprints']

print(f"Database has {len(orig_fps)} fingerprints from original video")

# Create verifier for similarity calculation
verifier = VideoVerifier("video_database.json")

# Check each fingerprint individually
print(f"\n{'='*70}")
print("ANALYZING EACH 5-SECOND SEGMENT")
print("="*70)

matches_found = []

for frank_idx, frank_fp in enumerate(frank_fps):
    frank_time = frank_fp['timestamp']
    best_similarity = 0
    best_orig_idx = -1
    best_orig_time = -1
    
    # Search through all original fingerprints
    for orig_idx, orig_fp in enumerate(orig_fps):
        similarity = verifier.calculate_similarity(frank_fp, orig_fp)
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_orig_idx = orig_idx
            best_orig_time = orig_fp['timestamp']
    
    # Show results for this segment
    frank_mins = int(frank_time // 60)
    frank_secs = int(frank_time % 60)
    orig_mins = int(best_orig_time // 60)
    orig_secs = int(best_orig_time % 60)
    
    status = "✓ MATCH" if best_similarity >= 0.85 else "  weak"
    
    print(f"\nFrankenstein {frank_mins:2d}:{frank_secs:02d} ({frank_time:.0f}s):")
    print(f"  {status} -> Original {orig_mins:2d}:{orig_secs:02d} ({best_orig_time:.0f}s)")
    print(f"  Similarity: {best_similarity:.1%}")
    
    if best_similarity >= 0.85:
        matches_found.append({
            'frank_time': frank_time,
            'orig_time': best_orig_time,
            'similarity': best_similarity
        })

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print("="*70)

print(f"\nTotal strong matches (≥85% similarity): {len(matches_found)}")

if matches_found:
    print("\nMatched segments reveal SOURCE timestamps:")
    for i, match in enumerate(matches_found, 1):
        frank_mins = int(match['frank_time'] // 60)
        frank_secs = int(match['frank_time'] % 60)
        orig_mins = int(match['orig_time'] // 60)
        orig_secs = int(match['orig_time'] % 60)
        
        print(f"  {i}. At {frank_mins:2d}:{frank_secs:02d} in Frankenstein "
              f"-> from {orig_mins:2d}:{orig_secs:02d} in original "
              f"({match['similarity']:.1%})")
    
    # Check if timestamps are scattered
    orig_timestamps = [m['orig_time'] for m in matches_found]
    if len(orig_timestamps) > 1:
        max_gap = max(orig_timestamps[i+1] - orig_timestamps[i] 
                     for i in range(len(orig_timestamps)-1))
        
        print(f"\n{'='*70}")
        print("EDITING DETECTION ANALYSIS")
        print("="*70)
        
        if max_gap > 300:  # 5 minutes
            print("\n🚨 EDITING DETECTED!")
            print(f"  • Timestamps jump by up to {max_gap:.0f}s ({max_gap/60:.1f} minutes)")
            print("  • This video is SPLICED from different parts")
            print("  • Content has been manipulated/edited")
            print("\n⚠️  WARNING: This is NOT a continuous authentic clip!")
            print("\n💡 Production System Recommendation:")
            print("  • Flag as 'Edited Content - Multiple Sources'")
            print("  • Display all source timestamps to user")
            print("  • Warn: 'This video combines clips from different times'")
        else:
            print("\n✓ Appears to be continuous segment")
            print(f"  • Maximum timestamp gap: {max_gap:.0f}s")
            print("  • Likely authentic clip")
else:
    print("\n✗ No strong matches found")
    print("  Video too heavily edited to match")

print("\n" + "="*70 + "\n")

