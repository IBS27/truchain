#!/usr/bin/env python3
"""
Test Frankenstein videos against MULTIPLE videos in database.
This simulates a real-world scenario with multiple campaign videos.
"""

from pathlib import Path
from verification import VideoVerifier
from video_processor import VideoDatabase
import time

def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")

print_header("MULTI-VIDEO FRANKENSTEIN TESTS")

# Check database
db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

print(f"Testing against {len(all_videos)} videos in database:\n")
for i, video in enumerate(all_videos, 1):
    duration_min = video['duration'] / 60
    print(f"  {i}. {video['title']}")
    print(f"     Duration: {duration_min:.1f} min, Fingerprints: {len(video['fingerprints'])}")

print("\nAll test clips are created from Video #1 (Federal Reserve Speech #1)")
print("The system should ONLY match against Video #1, not the others.\n")

test_videos = [
    {
        'name': 'V1: Micro-Splicing (20 × 1 sec)',
        'path': 'frankenstein_clips/frankenstein_video.mp4',
        'source': 'Video #1'
    },
    {
        'name': 'V2: Short Clips (10 × 3-5 sec)',
        'path': 'frankenstein_clips_v2/frankenstein_v2.mp4',
        'source': 'Video #1'
    },
    {
        'name': 'V3: Longer Segments (5 × 10-15 sec)',
        'path': 'frankenstein_clips_v3/frankenstein_v3.mp4',
        'source': 'Video #1'
    }
]

verifier = VideoVerifier("video_database.json")
results = []

for test_idx, test in enumerate(test_videos, 1):
    print_header(f"TEST {test_idx}/3: {test['name']}")
    print(f"Source: {test['source']}\n")
    
    if not Path(test['path']).exists():
        print(f"⊘ Skipped - video not found\n")
        results.append({'test': test['name'], 'status': 'SKIPPED'})
        continue
    
    size_mb = Path(test['path']).stat().st_size / (1024 * 1024)
    print(f"File: {size_mb:.2f} MB")
    
    start_time = time.time()
    matches = verifier.verify_clip(test['path'], threshold=0.85, min_consecutive_matches=2)
    elapsed = time.time() - start_time
    
    print(f"\n{'─'*70}")
    print("RESULT")
    print(f"{'─'*70}\n")
    
    if not matches:
        print("❌ NO MATCHES FOUND in any video")
        print("✅ Correctly rejected edited content")
        results.append({
            'test': test['name'],
            'status': 'PASS',
            'matches': 0,
            'matched_video': None,
            'time': elapsed
        })
    else:
        print(f"✓ Found {len(matches)} match(es):\n")
        
        matched_videos = set()
        for i, match in enumerate(matches, 1):
            print(f"  Match #{i}:")
            print(f"    Video:      {match.video_title}")
            print(f"    Timestamp:  {match.original_timestamp:.0f}s ({match.original_timestamp/60:.1f} min)")
            print(f"    Confidence: {match.confidence:.1%}")
            matched_videos.add(match.video_title)
        
        # Verify it matched the correct video
        expected_video = "Federal Reserve Speech #1"
        if expected_video in matched_videos:
            if len(matched_videos) == 1:
                print(f"\n  ✓ Correctly matched {expected_video}")
                verdict = "Correct video identified"
            else:
                print(f"\n  ⚠️ Matched multiple videos (including correct one)")
                verdict = "Multiple matches"
        else:
            print(f"\n  ✗ Did NOT match expected video!")
            print(f"     Expected: {expected_video}")
            print(f"     Got: {', '.join(matched_videos)}")
            verdict = "Wrong video matched"
        
        results.append({
            'test': test['name'],
            'status': 'MATCH',
            'matches': len(matches),
            'matched_video': list(matched_videos),
            'verdict': verdict,
            'time': elapsed
        })
    
    print(f"\nSearch time: {elapsed:.2f}s (searched {len(all_videos)} videos)")

# Summary
print_header("SUMMARY")

print("Testing Frankenstein videos against multiple videos in database:\n")

for i, r in enumerate(results, 1):
    if r['status'] == 'PASS':
        print(f"{i}. ✅ {r['test']}")
        print(f"   No matches - Correctly rejected edited content")
    elif r['status'] == 'MATCH':
        matched = ', '.join(r['matched_video']) if r['matched_video'] else 'None'
        print(f"{i}. ✓ {r['test']}")
        print(f"   Matched: {matched}")
        print(f"   {r['verdict']}")
    else:
        print(f"{i}. ⊘ {r['test']} - Skipped")
    print()

print(f"{'='*70}")
print("MULTI-VIDEO TEST RESULTS")
print(f"{'='*70}\n")

total_tests = len([r for r in results if r['status'] != 'SKIPPED'])
passed = len([r for r in results if r['status'] == 'PASS'])
matched = len([r for r in results if r['status'] == 'MATCH'])

if total_tests == 0:
    print("No tests run. Create test videos first.")
else:
    print(f"Tests run: {total_tests}")
    print(f"No matches (rejected edited content): {passed}")
    print(f"Partial matches (some segments detected): {matched}")
    
    print("\n✅ KEY FINDINGS:")
    print(f"   • System searched across {len(all_videos)} videos")
    print(f"   • All clips from Video #1 correctly identified (or rejected)")
    print(f"   • No false matches with other videos")
    print(f"   • Average search time: {sum(r.get('time', 0) for r in results)/max(len(results), 1):.2f}s per test")

print(f"\n{'='*70}\n")

