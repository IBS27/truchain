#!/usr/bin/env python3
"""Verify all test clips and show results."""

from pathlib import Path
from verification import VideoVerifier

clips_dir = Path("test_clips")

# Test clip information
test_clips = [
    {
        "file": "clip1_beginning_20s.mp4",
        "expected_start": 30,
        "duration": 20,
        "description": "Beginning (30s mark)"
    },
    {
        "file": "clip2_middle_30s.mp4",
        "expected_start": 600,
        "duration": 30,
        "description": "Middle (10 minutes)"
    },
    {
        "file": "clip3_end_15s.mp4",
        "expected_start": 3000,
        "duration": 15,
        "description": "Near end (50 minutes)"
    },
    {
        "file": "clip4_degraded_25s.mp4",
        "expected_start": 1200,
        "duration": 25,
        "description": "Degraded quality (20 minutes)"
    },
    {
        "file": "clip5_short_10s.mp4",
        "expected_start": 1800,
        "duration": 10,
        "description": "Short clip (30 minutes)"
    }
]

print("\n" + "="*70)
print("VERIFYING ALL TEST CLIPS")
print("="*70)

verifier = VideoVerifier("video_database.json")

results = []

for idx, clip_info in enumerate(test_clips, 1):
    clip_path = clips_dir / clip_info['file']
    
    if not clip_path.exists():
        print(f"\n[{idx}/5] ✗ {clip_info['file']} - FILE NOT FOUND")
        continue
    
    print(f"\n{'='*70}")
    print(f"[{idx}/5] {clip_info['file']}")
    print(f"{'='*70}")
    print(f"Description: {clip_info['description']}")
    print(f"Expected timestamp: {clip_info['expected_start']}s")
    print(f"Duration: {clip_info['duration']}s")
    print()
    
    # Verify clip
    matches = verifier.verify_clip(str(clip_path), threshold=0.80, min_consecutive_matches=2)
    
    if matches:
        match = matches[0]
        time_diff = abs(match.original_timestamp - clip_info['expected_start'])
        
        print(f"\n{'─'*70}")
        print("RESULT: ✅ MATCH FOUND!")
        print(f"{'─'*70}")
        print(f"  Video: {match.video_title}")
        print(f"  Detected timestamp: {match.original_timestamp}s")
        print(f"  Expected timestamp: {clip_info['expected_start']}s")
        print(f"  Accuracy: ±{time_diff}s")
        print(f"  Confidence: {match.confidence:.1%}")
        print(f"  Matching fingerprints: {match.fingerprint_matches}")
        
        if time_diff <= 5:
            print(f"  Timestamp accuracy: ✅ EXCELLENT")
        elif time_diff <= 10:
            print(f"  Timestamp accuracy: ✓ GOOD")
        else:
            print(f"  Timestamp accuracy: ⚠ ACCEPTABLE")
        
        results.append({
            'clip': clip_info['file'],
            'found': True,
            'confidence': match.confidence,
            'accuracy': time_diff
        })
    else:
        print(f"\n{'─'*70}")
        print("RESULT: ❌ NO MATCH FOUND")
        print(f"{'─'*70}")
        results.append({
            'clip': clip_info['file'],
            'found': False
        })

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

found = sum(1 for r in results if r['found'])
total = len(results)

print(f"\nMatches found: {found}/{total}")
print()

for result in results:
    if result['found']:
        print(f"✅ {result['clip']}")
        print(f"   Confidence: {result['confidence']:.1%}, Accuracy: ±{result['accuracy']}s")
    else:
        print(f"❌ {result['clip']}")

if found == total:
    print("\n🎉 ALL CLIPS VERIFIED SUCCESSFULLY!")
    avg_confidence = sum(r['confidence'] for r in results if r['found']) / found
    avg_accuracy = sum(r['accuracy'] for r in results if r['found']) / found
    print(f"\nAverage confidence: {avg_confidence:.1%}")
    print(f"Average accuracy: ±{avg_accuracy:.1f}s")

print("\n" + "="*70)

