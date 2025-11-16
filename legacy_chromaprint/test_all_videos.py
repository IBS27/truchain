#!/usr/bin/env python3
"""
Comprehensive test: Create clips from all videos and verify against all videos.
This proves the system can distinguish between different videos.
"""

import subprocess
from pathlib import Path
from verification import VideoVerifier
from video_processor import VideoDatabase
import time

def create_clip(video_path, start, duration, output_name):
    """Create a clip from a video."""
    cmd = [
        'ffmpeg', '-i', video_path, '-ss', str(start), '-t', str(duration),
        '-c', 'copy', '-y', output_name
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")

print_header("COMPREHENSIVE MULTI-VIDEO TEST")

# Get all videos from database
db = VideoDatabase("video_database.json")
all_videos = db.get_all_videos()

print(f"Database contains {len(all_videos)} videos:\n")
for i, video in enumerate(all_videos, 1):
    print(f"  {i}. {video['title']} ({video['duration']/60:.1f} min)")

# Prepare test clips directory
test_dir = Path("multi_video_test_clips")
test_dir.mkdir(exist_ok=True)

print("\n" + "="*70)
print("CREATING TEST CLIPS FROM EACH VIDEO")
print("="*70 + "\n")

test_cases = []

# Create one clip from each video
for i, video in enumerate(all_videos, 1):
    video_file = Path("download") / video['metadata']['filename']
    
    if not video_file.exists():
        print(f"⚠️  Video file not found: {video_file}")
        continue
    
    # Create a 20-second clip from 2 minutes into each video
    clip_name = f"clip_from_video{i}.mp4"
    clip_path = test_dir / clip_name
    
    print(f"Creating clip from Video #{i}: {video['title']}")
    print(f"  Extracting 20 seconds from 2:00 mark...")
    
    try:
        create_clip(str(video_file), 120, 20, str(clip_path))
        size_mb = clip_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Created: {clip_name} ({size_mb:.2f} MB)\n")
        
        test_cases.append({
            'clip_path': str(clip_path),
            'clip_name': clip_name,
            'source_video': video['title'],
            'source_video_id': video['id'],
            'expected_timestamp': 120
        })
    except Exception as e:
        print(f"  ✗ Failed: {e}\n")

if not test_cases:
    print("No test clips created!")
    exit(1)

# Now verify each clip
print("="*70)
print("VERIFYING EACH CLIP")
print("="*70)

verifier = VideoVerifier("video_database.json")
results = []

for idx, test in enumerate(test_cases, 1):
    print(f"\n{'─'*70}")
    print(f"TEST {idx}/{len(test_cases)}: {test['clip_name']}")
    print(f"{'─'*70}")
    print(f"Source: {test['source_video']}")
    print(f"Expected: Should match Video #{idx} at ~120s\n")
    
    start_time = time.time()
    matches = verifier.verify_clip(test['clip_path'], threshold=0.85, min_consecutive_matches=2)
    elapsed = time.time() - start_time
    
    if not matches:
        print("❌ NO MATCH FOUND")
        print(f"✗ FAILED: Expected to match {test['source_video']}")
        results.append({
            'test': test['clip_name'],
            'expected': test['source_video'],
            'matched': None,
            'status': 'FAIL',
            'time': elapsed
        })
    else:
        match = matches[0]
        matched_correct = match.video_id == test['source_video_id']
        timestamp_close = abs(match.original_timestamp - test['expected_timestamp']) <= 10
        
        print(f"✓ MATCH FOUND")
        print(f"  Matched video: {match.video_title}")
        print(f"  Timestamp: {match.original_timestamp:.0f}s (expected ~{test['expected_timestamp']}s)")
        print(f"  Confidence: {match.confidence:.1%}")
        
        if matched_correct and timestamp_close:
            print(f"\n✅ SUCCESS: Correctly identified source video and timestamp!")
            status = 'PASS'
        elif matched_correct:
            print(f"\n⚠️ PARTIAL: Correct video but timestamp off by {abs(match.original_timestamp - test['expected_timestamp']):.0f}s")
            status = 'PARTIAL'
        else:
            print(f"\n✗ FAILED: Matched wrong video!")
            print(f"   Expected: {test['source_video']}")
            print(f"   Got: {match.video_title}")
            status = 'WRONG_VIDEO'
        
        results.append({
            'test': test['clip_name'],
            'expected': test['source_video'],
            'matched': match.video_title,
            'status': status,
            'confidence': match.confidence,
            'time': elapsed
        })
    
    print(f"Verification time: {elapsed:.2f}s")

# Summary
print_header("FINAL RESULTS")

passed = sum(1 for r in results if r['status'] == 'PASS')
partial = sum(1 for r in results if r['status'] == 'PARTIAL')
failed = sum(1 for r in results if r['status'] in ['FAIL', 'WRONG_VIDEO'])

print(f"Total tests: {len(results)}")
print(f"✅ Passed: {passed}")
print(f"⚠️ Partial: {partial}")
print(f"✗ Failed: {failed}\n")

for i, r in enumerate(results, 1):
    status_icon = {'PASS': '✅', 'PARTIAL': '⚠️', 'FAIL': '✗', 'WRONG_VIDEO': '✗'}[r['status']]
    matched_info = f" -> {r['matched']}" if r['matched'] else " -> No match"
    conf_info = f" ({r.get('confidence', 0):.1%})" if 'confidence' in r else ""
    
    print(f"{i}. {status_icon} {r['test']}")
    print(f"   Expected: {r['expected']}{matched_info}{conf_info}")

print(f"\n{'='*70}")

if passed == len(results):
    print("🎉 PERFECT! All clips correctly matched to their source videos!")
    print("\n✅ System can distinguish between different videos")
    print("✅ Accurate timestamp detection")
    print(f"✅ Fast verification ({sum(r['time'] for r in results)/len(results):.2f}s avg)")
elif passed + partial == len(results):
    print("✅ GOOD! All clips matched correctly (some timestamp variations)")
    print("\n✅ System can distinguish between different videos")
    print(f"✅ Fast verification ({sum(r['time'] for r in results)/len(results):.2f}s avg)")
else:
    print(f"⚠️ {failed} test(s) failed")
    print("\nCheck why some clips didn't match correctly")

print(f"{'='*70}\n")

print(f"Test clips saved in: {test_dir}/")
print(f"Database has {len(all_videos)} videos with {db.get_stats()['total_fingerprints']} total fingerprints\n")

