#!/usr/bin/env python3
"""
Test Speaker Verification Standalone

This tests ONLY the speaker verification component without needing content matching.
Uses cached transcriptions, so no API key needed.
"""

from pathlib import Path
from speaker_verification import SpeakerVerifier


def test_authentic_clip():
    """
    Test 1: Authentic clip from the same video
    Expected: High similarity (> 0.85)
    """
    print("\n" + "="*80)
    print("TEST 1: AUTHENTIC CLIP")
    print("="*80)
    print("Testing: 15-second clip from fedspeech1.mp4 (2:00-2:15)")
    print("Against: Same location in original fedspeech1.mp4")
    print("Expected: ✓ HIGH SIMILARITY (same speaker)\n")
    
    verifier = SpeakerVerifier()
    
    result = verifier.verify_speaker(
        clip_path="test_clips/speaker_test_clip.mp4",
        clip_start=0,
        clip_duration=10,  # Analyze first 10 seconds
        original_path="download/fedspeech1.mp4",
        original_start=120,  # 2:00 mark (where clip was extracted)
        original_duration=10,
        threshold=0.85
    )
    
    return result


def test_different_recording():
    """
    Test 2: Same content, different recording
    Expected: High similarity (same speaker = Jerome Powell)
    """
    print("\n" + "="*80)
    print("TEST 2: DIFFERENT RECORDING (Same Speaker)")
    print("="*80)
    print("Testing: First 10 seconds of fedspeech1.mp4")
    print("Against: First 10 seconds of fedspeech2.mp4")
    print("Expected: ✓ HIGH SIMILARITY (same speaker, different recording)\n")
    
    verifier = SpeakerVerifier()
    
    result = verifier.verify_speaker(
        clip_path="download/fedspeech1.mp4",
        clip_start=10,
        clip_duration=10,
        original_path="download/fedspeech2.mp4",
        original_start=10,
        original_duration=10,
        threshold=0.85
    )
    
    return result


def test_different_speaker():
    """
    Test 3: Different speaker (if available)
    Expected: Low similarity (< 0.85)
    """
    print("\n" + "="*80)
    print("TEST 3: DIFFERENT SPEAKER")
    print("="*80)
    print("Testing: First 10 seconds of fedspeech1.mp4")
    print("Against: First 10 seconds of fedspeechdifferent.mp4")
    print("Expected: ✗ LOW SIMILARITY (different speaker)\n")
    
    # Check if different video exists
    if not Path("download/fedspeechdifferent.mp4").exists():
        print("⚠️  Skipping: fedspeechdifferent.mp4 not found")
        print("   (This would test against a different speaker)")
        return None
    
    verifier = SpeakerVerifier()
    
    result = verifier.verify_speaker(
        clip_path="download/fedspeech1.mp4",
        clip_start=10,
        clip_duration=10,
        original_path="download/fedspeechdifferent.mp4",
        original_start=10,
        original_duration=10,
        threshold=0.85
    )
    
    return result


def main():
    """Run all speaker verification tests."""
    print("\n" + "="*80)
    print("SPEAKER VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis tests the speaker verification system using audio embeddings.")
    print("No OpenAI API key needed - testing speaker identity only.\n")
    
    results = []
    
    # Test 1: Authentic clip
    result1 = test_authentic_clip()
    results.append(("Authentic Clip", result1))
    
    # Test 2: Different recording
    result2 = test_different_recording()
    results.append(("Different Recording", result2))
    
    # Test 3: Different speaker
    result3 = test_different_speaker()
    if result3:
        results.append(("Different Speaker", result3))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    for name, result in results:
        if result:
            status = "✓ VERIFIED" if result['verified'] else "✗ NOT VERIFIED"
            print(f"{name:25} {status:15} (similarity: {result['similarity']:.2%})")
    
    print("\n" + "="*80)
    print("All tests completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

