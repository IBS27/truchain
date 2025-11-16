#!/usr/bin/env python3
"""Debug script to check fingerprint matching."""

import sys
from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase
from verification import VideoVerifier

# Process original and clip
original = "download/fedspeech1.mp4"
clip = "test_clips/exact_clip.mp4"

print("Generating fingerprints for original (first 30 seconds only for comparison)...")
fp_orig = AudioFingerprinter(original)
orig_fps = fp_orig.generate_fingerprints()

print(f"\nOriginal video fingerprints (first 5):")
for i, fp in enumerate(orig_fps[:5]):
    print(f"  {i}: Time {fp['timestamp']}s -> {fp['hash'][:32]}...")

print("\nGenerating fingerprints for clip...")
fp_clip = AudioFingerprinter(clip)
clip_fps = fp_clip.generate_fingerprints()

print(f"\nClip fingerprints (all {len(clip_fps)}):")
for i, fp in enumerate(clip_fps):
    print(f"  {i}: Time {fp['timestamp']}s -> {fp['hash'][:32]}...")

# Check similarity between clip fingerprints and original around the 60s mark
print("\n" + "="*70)
print("Comparing clip fingerprints with original around 60s mark")
print("="*70)

# Clip starts at 60s, so compare with fingerprints at indices 12-16 (60s, 65s, 70s, 75s)
clip_start_idx = 12  # 60 seconds / 5 seconds per fingerprint

# Create verifier instance to use its similarity calculation
verifier = VideoVerifier()

for clip_idx, clip_fp in enumerate(clip_fps):
    expected_orig_idx = clip_start_idx + clip_idx
    if expected_orig_idx < len(orig_fps):
        orig_fp = orig_fps[expected_orig_idx]
        
        # Compare hashes
        are_equal = clip_fp['hash'] == orig_fp['hash']
        
        # Calculate proper chromaprint similarity
        similarity = verifier.calculate_similarity(clip_fp, orig_fp)
        
        print(f"\nClip fingerprint {clip_idx} (t={clip_fp['timestamp']}s):")
        print(f"  vs Original fingerprint {expected_orig_idx} (t={orig_fp['timestamp']}s):")
        print(f"  Exact match: {are_equal}")
        print(f"  Chromaprint similarity: {similarity:.2%}")
        print(f"  Clip hash:     {clip_fp['hash'][:48]}...")
        print(f"  Original hash: {orig_fp['hash'][:48]}...")
        if 'fingerprint' in clip_fp and 'fingerprint' in orig_fp:
            print(f"  Fingerprint arrays: {len(clip_fp['fingerprint'])} vs {len(orig_fp['fingerprint'])} integers")

