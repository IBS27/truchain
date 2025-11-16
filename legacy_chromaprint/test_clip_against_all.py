#!/usr/bin/env python3
"""
Test a single clip against EVERY video in the database.
Shows detailed comparison results for each video.
"""

import sys
from pathlib import Path
from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase
from verification import VideoVerifier

def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")

def print_section(title):
    print("\n" + "-"*70)
    print(title)
    print("-"*70)

if len(sys.argv) < 2:
    print("Usage: python3.10 test_clip_against_all.py <clip_file> [threshold]")
    print("\nTests a clip against EVERY video in the database.")
    print("\nExamples:")
    print("  python3.10 test_clip_against_all.py user_clip.mp4")
    print("  python3.10 test_clip_against_all.py clip.mp4 0.80")
    sys.exit(1)

clip_path = sys.argv[1]
threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.85

if not Path(clip_path).exists():
    print(f"Error: Clip file not found: {clip_path}")
    sys.exit(1)

print_header("TEST CLIP AGAINST ALL VIDEOS")

print(f"Clip: {clip_path}")
print(f"Similarity threshold: {threshold:.0%}\n")

# Load database
db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

if not all_videos:
    print("Error: No videos in database!")
    print("Add videos first: python3.10 process_all_videos.py")
    sys.exit(1)

print(f"Database contains {len(all_videos)} video(s):\n")
for i, video in enumerate(all_videos, 1):
    print(f"  {i}. {video['title']} ({video['duration']/60:.1f} min, {len(video['fingerprints'])} fingerprints)")

# Generate fingerprints for the clip
print_section("Processing Clip")

fingerprinter = AudioFingerprinter(clip_path)
print(f"\nExtracting audio and generating fingerprints...")
clip_fps = fingerprinter.generate_fingerprints()
clip_duration = fingerprinter.get_duration()

print(f"✓ Generated {len(clip_fps)} fingerprints from {clip_duration:.1f}s clip")

# Create verifier for similarity calculation
verifier = VideoVerifier("video_database.json")

# Test against each video individually
print_header("TESTING AGAINST EACH VIDEO")

results = []

for video_idx, video in enumerate(all_videos, 1):
    print(f"\n{'='*70}")
    print(f"VIDEO {video_idx}/{len(all_videos)}: {video['title']}")
    print(f"{'='*70}\n")
    
    video_fps = video['fingerprints']
    
    # Find best matches for this video
    best_matches = []
    
    for clip_fp in clip_fps:
        best_similarity = 0
        best_timestamp = -1
        
        for video_fp in video_fps:
            similarity = verifier.calculate_similarity(clip_fp, video_fp)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_timestamp = video_fp['timestamp']
        
        if best_similarity >= threshold:
            best_matches.append({
                'clip_time': clip_fp['timestamp'],
                'video_time': best_timestamp,
                'similarity': best_similarity
            })
    
    # Show results for this video
    if not best_matches:
        print("❌ NO STRONG MATCHES")
        print(f"   No fingerprints exceeded {threshold:.0%} similarity threshold")
        results.append({
            'video': video['title'],
            'video_id': video['id'],
            'matches': 0,
            'status': 'NO_MATCH'
        })
    else:
        print(f"✓ Found {len(best_matches)} matching fingerprint(s):\n")
        
        # Show first few matches
        for i, match in enumerate(best_matches[:5], 1):
            clip_min = int(match['clip_time'] // 60)
            clip_sec = int(match['clip_time'] % 60)
            video_min = int(match['video_time'] // 60)
            video_sec = int(match['video_time'] % 60)
            
            print(f"  {i}. Clip {clip_min:2d}:{clip_sec:02d} -> Video {video_min:2d}:{video_sec:02d} "
                  f"({match['similarity']:.1%} similar)")
        
        if len(best_matches) > 5:
            print(f"  ... and {len(best_matches) - 5} more matches")
        
        # Calculate average similarity
        avg_similarity = sum(m['similarity'] for m in best_matches) / len(best_matches)
        
        # Check if matches are consecutive
        timestamps = [m['video_time'] for m in best_matches]
        is_continuous = all(abs(timestamps[i+1] - timestamps[i]) <= 10 
                           for i in range(len(timestamps)-1)) if len(timestamps) > 1 else True
        
        print(f"\n  Average similarity: {avg_similarity:.1%}")
        print(f"  Match type: {'Continuous' if is_continuous else 'Scattered'}")
        
        if not is_continuous:
            print(f"  ⚠️  Timestamps are SCATTERED - possible editing detected")
        
        results.append({
            'video': video['title'],
            'video_id': video['id'],
            'matches': len(best_matches),
            'avg_similarity': avg_similarity,
            'continuous': is_continuous,
            'status': 'MATCH'
        })

# Final Summary
print_header("SUMMARY")

matched_videos = [r for r in results if r['status'] == 'MATCH']
no_match_videos = [r for r in results if r['status'] == 'NO_MATCH']

print(f"Tested against: {len(results)} video(s)")
print(f"Matches found:  {len(matched_videos)}")
print(f"No matches:     {len(no_match_videos)}\n")

if matched_videos:
    print("MATCHED VIDEOS:")
    for i, result in enumerate(matched_videos, 1):
        print(f"\n{i}. {result['video']}")
        print(f"   Matches: {result['matches']} fingerprints")
        print(f"   Avg similarity: {result['avg_similarity']:.1%}")
        print(f"   Type: {'✓ Continuous clip' if result['continuous'] else '⚠️ Scattered/edited'}")
    
    print(f"\n{'='*70}")
    
    if len(matched_videos) == 1:
        video = matched_videos[0]
        if video['continuous']:
            print("✅ AUTHENTIC CLIP DETECTED")
            print(f"   This clip appears to be from: {video['video']}")
            print(f"   It's a continuous, unedited segment")
        else:
            print("⚠️ EDITED CONTENT DETECTED")
            print(f"   This clip contains audio from: {video['video']}")
            print(f"   BUT timestamps are scattered - possible editing")
    else:
        print("⚠️ MULTIPLE VIDEO MATCHES")
        print("   This clip matches multiple videos")
        print("   This is unusual and should be investigated")
else:
    print("NO MATCHES FOUND")
    print("\nPossible reasons:")
    print("  • Clip is not from any video in database")
    print("  • Audio quality is too degraded")
    print("  • Clip is heavily edited/manipulated")
    print(f"  • Similarity threshold ({threshold:.0%}) is too strict")
    print("\nTry:")
    print(f"  python3.10 test_clip_against_all.py {clip_path} 0.75")

print(f"\n{'='*70}\n")

# Show which videos had NO matches
if no_match_videos:
    print("Videos with NO matches:")
    for result in no_match_videos:
        print(f"  • {result['video']}")
    print()

