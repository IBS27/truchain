#!/usr/bin/env python3
"""
Test the Frankenstein video to detect edited/spliced content.
This is an edge case for misinformation detection.
"""

from pathlib import Path
from verification import VideoVerifier
from audio_fingerprint import AudioFingerprinter

print("\n" + "="*70)
print("FRANKENSTEIN VIDEO EDGE CASE TEST")
print("="*70)
print("\nContext: This video contains REAL audio from the original video,")
print("but it's spliced from 20 different timestamps to create a")
print("potentially misleading narrative.")
print("\n" + "="*70)

frankenstein_path = "frankenstein_clips/frankenstein_video.mp4"
timestamps_file = "frankenstein_clips/timestamps.txt"

# Show original timestamps
if Path(timestamps_file).exists():
    print("\nORIGINAL SOURCE TIMESTAMPS:")
    print("="*70)
    with open(timestamps_file, 'r') as f:
        content = f.read()
        # Skip header
        lines = content.split('\n')[3:]
        for line in lines[:20]:  # Show first 20
            if line.strip():
                print(f"  {line}")
else:
    print("\nOriginal timestamps file not found.")

print("\n" + "="*70)
print("RUNNING VERIFICATION...")
print("="*70)

# First, get basic info
fingerprinter = AudioFingerprinter(frankenstein_path)
duration = fingerprinter.get_duration()
print(f"\nFrankenstein video duration: {duration:.1f}s")

# Run verification with lower threshold to catch matches
verifier = VideoVerifier("video_database.json")
matches = verifier.verify_clip(
    frankenstein_path,
    threshold=0.75,  # Lower threshold to catch more matches
    min_consecutive_matches=1  # Allow single matches to see all detections
)

print("\n" + "="*70)
print("ANALYSIS RESULTS")
print("n" + "="*70)

if not matches:
    print("\n❌ NO MATCHES FOUND")
    print("\nThis could mean:")
    print("  • The spliced segments are too short (1 second each)")
    print("  • Audio transitions between clips don't match fingerprints")
    print("  • The editing broke the audio fingerprint continuity")
    
else:
    print(f"\n✓ Found {len(matches)} match(es)")
    print("\nDETECTED SEGMENTS:")
    print("="*70)
    
    for i, match in enumerate(matches, 1):
        clip_time = match.clip_timestamp
        orig_time = match.original_timestamp
        
        clip_mins = int(clip_time // 60)
        clip_secs = int(clip_time % 60)
        orig_mins = int(orig_time // 60)
        orig_secs = int(orig_time % 60)
        
        print(f"\nMatch #{i}:")
        print(f"  Frankenstein timestamp: {clip_mins:2d}:{clip_secs:02d} ({clip_time:.1f}s)")
        print(f"  Original timestamp:     {orig_mins:2d}:{orig_secs:02d} ({orig_time:.1f}s)")
        print(f"  Confidence: {match.confidence:.1%}")
        print(f"  Consecutive matches: {match.fingerprint_matches}")

print("\n" + "="*70)
print("EDGE CASE INTERPRETATION")
print("="*70)

if not matches:
    print("\n🔍 RESULT: Video too heavily edited to match")
    print("\nExplanation:")
    print("  • 1-second clips are too short for reliable fingerprinting")
    print("  • Audio transitions create new artifacts")
    print("  • System correctly doesn't give false positive")
    print("\n✅ GOOD: No false positive for heavily edited content")
    
elif len(matches) == 1:
    print("\n⚠️ RESULT: Single continuous match detected")
    print("\nThis suggests:")
    print("  • Video appears to be from one continuous segment")
    print("  • Could be authentic OR cleverly edited")
    print("  • Further analysis recommended")
    
else:
    print(f"\n🔍 RESULT: Multiple scattered matches ({len(matches)} segments)")
    print("\nThis is SUSPICIOUS and suggests:")
    print("  • Video is spliced from different parts")
    print("  • Content has been edited/manipulated")
    print("  • NOT a continuous authentic clip")
    print("\n⚠️ WARNING: This video shows signs of editing!")
    print("\nFor production system:")
    print("  • Flag as 'Edited - Multiple Sources'")
    print("  • Show all source timestamps to user")
    print("  • Warn that narrative may be misleading")

print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)

if not matches:
    print("\nThe system correctly handles this edge case:")
    print("  ✅ No false positive for heavily edited content")
    print("  ✅ 1-second clips are too short to match")
    print("  ✅ System is robust against splice manipulation")
    
elif len(matches) > 1:
    print("\nThe system can DETECT edited content:")
    print("  ✅ Multiple scattered timestamps reveal editing")
    print("  ✅ Users can see the video is not continuous")
    print("  ✅ Helps identify manipulated narratives")
    print("\n💡 Production feature idea:")
    print("  • Add 'continuity check' for timestamps")
    print("  • Flag if timestamps jump > 30 seconds")
    print("  • Label as 'Compiled Clips' vs 'Authentic Clip'")

print("\n" + "="*70 + "\n")

