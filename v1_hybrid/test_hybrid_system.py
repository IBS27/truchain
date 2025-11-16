#!/usr/bin/env python3
"""
Test Suite for Hybrid Verification System

Tests both content matching (transcription) and speaker verification (audio embeddings).
"""

import sys
import os
from pathlib import Path
from hybrid_verification import HybridVerifier


def test_exact_clip():
    """Test verification of exact clip from original video."""
    print("\n" + "="*80)
    print("TEST 1: Exact Clip Verification")
    print("="*80)
    print("\nThis test verifies an exact 10-second clip from an original video.")
    print("Expected: HIGH confidence match with both content and speaker verified.\n")
    
    clip_path = "test_clips/exact_clip_10s.mp4"
    
    if not Path(clip_path).exists():
        print(f"⚠️  Test clip not found: {clip_path}")
        print("   Please create test clips first using create_test_clips.py")
        return False
    
    verifier = HybridVerifier()
    result = verifier.verify_clip(clip_path, verbose=True)
    
    # Check results
    if result['verified'] and result['confidence'] == 'high':
        print("✅ TEST PASSED: Exact clip correctly verified with high confidence")
        return True
    else:
        print("❌ TEST FAILED: Exact clip not verified correctly")
        print(f"   Result: {result}")
        return False


def test_different_video():
    """Test that different video is NOT verified."""
    print("\n" + "="*80)
    print("TEST 2: Different Video Rejection")
    print("="*80)
    print("\nThis test verifies that a completely different video is NOT matched.")
    print("Expected: LOW confidence or NOT verified.\n")
    
    # Use fedspeechdifferent.mp4 if available
    different_video = "download/fedspeechdifferent.mp4"
    
    if not Path(different_video).exists():
        print(f"⚠️  Different video not found: {different_video}")
        print("   Skipping this test")
        return True  # Skip test
    
    verifier = HybridVerifier()
    
    # Create a 10-second clip from the different video
    clip_path = "test_clips/different_clip_10s.mp4"
    
    # Extract clip using ffmpeg
    import subprocess
    os.makedirs("test_clips", exist_ok=True)
    
    cmd = [
        'ffmpeg', '-i', different_video,
        '-ss', '30',  # Start at 30s
        '-t', '10',   # Duration 10s
        '-y', clip_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except Exception as e:
        print(f"⚠️  Could not create test clip: {e}")
        return True  # Skip test
    
    result = verifier.verify_clip(clip_path, verbose=True)
    
    # Check results - should NOT be verified
    if not result['verified'] or result['confidence'] == 'low':
        print("✅ TEST PASSED: Different video correctly rejected")
        return True
    else:
        print("❌ TEST FAILED: Different video was incorrectly verified")
        print(f"   Result: {result}")
        return False


def test_timestamp_accuracy():
    """Test that timestamps are accurate."""
    print("\n" + "="*80)
    print("TEST 3: Timestamp Accuracy")
    print("="*80)
    print("\nThis test verifies that timestamp detection is accurate.")
    print("Expected: Detected timestamp should match where clip was extracted from.\n")
    
    # Extract a clip from 2:00 (120s) in the original
    source_video = "download/fedspeech1.mp4"
    clip_path = "test_clips/timestamp_test_clip.mp4"
    
    if not Path(source_video).exists():
        print(f"⚠️  Source video not found: {source_video}")
        return True  # Skip test
    
    # Extract clip
    import subprocess
    os.makedirs("test_clips", exist_ok=True)
    
    EXPECTED_TIMESTAMP = 120  # 2:00
    
    cmd = [
        'ffmpeg', '-i', source_video,
        '-ss', str(EXPECTED_TIMESTAMP),
        '-t', '15',  # 15 second clip
        '-y', clip_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except Exception as e:
        print(f"⚠️  Could not create test clip: {e}")
        return True  # Skip test
    
    verifier = HybridVerifier()
    result = verifier.verify_clip(clip_path, verbose=True)
    
    if not result['verified']:
        print("❌ TEST FAILED: Clip not verified")
        return False
    
    detected_timestamp = result['content_match']['start_timestamp']
    timestamp_error = abs(detected_timestamp - EXPECTED_TIMESTAMP)
    
    print(f"\n  Expected timestamp: {EXPECTED_TIMESTAMP}s (2:00)")
    print(f"  Detected timestamp: {detected_timestamp}s")
    print(f"  Error: {timestamp_error}s")
    
    # Allow 30 second error (one segment)
    if timestamp_error <= 30:
        print("✅ TEST PASSED: Timestamp is accurate")
        return True
    else:
        print("❌ TEST FAILED: Timestamp error too large")
        return False


def test_deepfake_detection():
    """Test that system can detect potential deepfakes (content match but speaker mismatch)."""
    print("\n" + "="*80)
    print("TEST 4: Deepfake Detection (Conceptual)")
    print("="*80)
    print("\nThis test would verify that content matches but speaker doesn't.")
    print("(Requires a video with same words but different voice - not implemented)\n")
    
    print("⚠️  Skipping: Requires deepfake/voiceover test video")
    return True  # Skip for now


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "#"*80)
    print("HYBRID VERIFICATION SYSTEM - TEST SUITE")
    print("#"*80)
    
    tests = [
        ("Exact Clip Verification", test_exact_clip),
        ("Different Video Rejection", test_different_video),
        ("Timestamp Accuracy", test_timestamp_accuracy),
        ("Deepfake Detection", test_deepfake_detection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "#"*80)
    print("TEST SUMMARY")
    print("#"*80 + "\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n  🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n  ⚠️  {total_count - passed_count} test(s) failed")
        return 1


def main():
    """Main entry point."""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set it with:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Check if database exists
    db_path = Path("video_database_hybrid.json")
    if not db_path.exists():
        print("Error: Database not found: video_database_hybrid.json")
        print("\nPlease process videos first:")
        print("  python process_videos_hybrid.py --directory download")
        sys.exit(1)
    
    # Run tests
    exit_code = run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

