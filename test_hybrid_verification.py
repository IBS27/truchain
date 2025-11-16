#!/usr/bin/env python3
"""
Test Hybrid Verification: Content Matching + Speaker Verification

This demonstrates the full two-stage verification process:
1. Stage 1 (V2): Find WHAT was said using word-level text matching
2. Stage 2 (Speaker): Verify WHO said it using audio embeddings
"""

from pathlib import Path
from verification_v2 import VideoVerifierV2
from speaker_verification import SpeakerVerifier


def test_full_verification(
    clip_path: str,
    text_threshold: float = 0.80,
    speaker_threshold: float = 0.85
):
    """
    Test full hybrid verification on a clip.
    
    Args:
        clip_path: Path to video clip to verify
        text_threshold: Minimum text similarity for content match
        speaker_threshold: Minimum speaker similarity for voice match
    """
    print(f"\n{'='*80}")
    print("HYBRID VERIFICATION TEST: CONTENT + SPEAKER")
    print(f"{'='*80}\n")
    
    print(f"Clip: {Path(clip_path).name}")
    print(f"Text Threshold: {text_threshold:.1%}")
    print(f"Speaker Threshold: {speaker_threshold:.1%}\n")
    
    # ========================================================================
    # STAGE 1: CONTENT VERIFICATION (Text Matching)
    # ========================================================================
    print(f"{'─'*80}")
    print("STAGE 1: CONTENT VERIFICATION")
    print(f"{'─'*80}\n")
    
    v2_system = VideoVerifierV2(
        similarity_threshold=text_threshold
    )
    
    content_result = v2_system.verify_clip(clip_path, video_directory="download")
    
    if not content_result['verified']:
        print(f"\n{'='*80}")
        print("❌ FINAL RESULT: NOT VERIFIED")
        print(f"{'='*80}")
        print(f"Reason: Content not found in database")
        print(f"Text Similarity: {content_result['best_match']['similarity']:.2%}")
        print(f"Text Threshold: {text_threshold:.2%}\n")
        return {
            'verified': False,
            'reason': 'content_not_found',
            'content_result': content_result
        }
    
    print(f"\n✓ Content Match Found!")
    print(f"  Video: {content_result['best_match']['video_name']}")
    print(f"  Timestamp: {content_result['best_match']['start_time']:.1f}s - {content_result['best_match']['end_time']:.1f}s")
    print(f"  Text Similarity: {content_result['best_match']['similarity']:.2%}")
    
    # ========================================================================
    # STAGE 2: SPEAKER VERIFICATION (Audio Embeddings)
    # ========================================================================
    print(f"\n{'─'*80}")
    print("STAGE 2: SPEAKER VERIFICATION")
    print(f"{'─'*80}\n")
    
    verifier = SpeakerVerifier()
    
    # Get matched timestamps
    original_video_path = f"download/{content_result['best_match']['video_name']}"
    start_time = content_result['best_match']['start_time']
    end_time = content_result['best_match']['end_time']
    duration = end_time - start_time
    
    # Verify speaker (analyze first 10 seconds or full duration, whichever is shorter)
    verify_duration = min(10.0, duration)
    
    speaker_result = verifier.verify_speaker(
        clip_path=clip_path,
        clip_start=0,  # Start of clip
        clip_duration=verify_duration,
        original_path=original_video_path,
        original_start=start_time,
        original_duration=verify_duration,
        threshold=speaker_threshold
    )
    
    # ========================================================================
    # FINAL RESULT
    # ========================================================================
    print(f"\n{'='*80}")
    
    if content_result['verified'] and speaker_result['verified']:
        print("✅ FINAL RESULT: FULLY VERIFIED")
        print(f"{'='*80}")
        print(f"✓ Content Match: {content_result['best_match']['similarity']:.2%}")
        print(f"✓ Speaker Match: {speaker_result['similarity']:.2%}")
        print(f"\nThis clip is an authentic excerpt from:")
        print(f"  Video: {content_result['best_match']['video_name']}")
        print(f"  Time: {start_time:.1f}s - {end_time:.1f}s")
        print(f"  Spoken by: The same person in the original video")
        final_verified = True
        final_reason = "fully_verified"
        
    elif content_result['verified'] and not speaker_result['verified']:
        print("⚠️  FINAL RESULT: PARTIAL VERIFICATION")
        print(f"{'='*80}")
        print(f"✓ Content Match: {content_result['best_match']['similarity']:.2%}")
        print(f"✗ Speaker Match: {speaker_result['similarity']:.2%}")
        print(f"\nWARNING: Content matches, but different speaker detected!")
        print(f"  Possible voiceover or deepfake")
        print(f"  Original Video: {content_result['best_match']['video_name']}")
        print(f"  Time: {start_time:.1f}s - {end_time:.1f}s")
        final_verified = False
        final_reason = "speaker_mismatch"
        
    else:
        print("❌ FINAL RESULT: NOT VERIFIED")
        print(f"{'='*80}")
        print(f"Content verification failed")
        final_verified = False
        final_reason = "content_not_found"
    
    print(f"{'='*80}\n")
    
    return {
        'verified': final_verified,
        'reason': final_reason,
        'content_result': content_result,
        'speaker_result': speaker_result
    }


def main():
    """Run hybrid verification tests."""
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 80)
        print("HYBRID VERIFICATION TEST")
        print("=" * 80)
        print("\nUsage: python test_hybrid_verification.py <clip_path> [text_threshold] [speaker_threshold]")
        print("\nExample:")
        print("  python test_hybrid_verification.py test_clips/exact_clip.mp4")
        print("  python test_hybrid_verification.py my_clip.mp4 0.80 0.85")
        print("\nThresholds:")
        print("  text_threshold: 0.0-1.0 (default: 0.80)")
        print("  speaker_threshold: 0.0-1.0 (default: 0.85)")
        print("\nThis will:")
        print("  1. Find content matches using word-level text matching")
        print("  2. Verify speaker identity using audio embeddings")
        print("  3. Return final verdict: verified / partial / not verified")
        print()
        sys.exit(1)
    
    clip_path = sys.argv[1]
    text_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.80
    speaker_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.85
    
    if not Path(clip_path).exists():
        print(f"Error: Clip not found: {clip_path}")
        sys.exit(1)
    
    result = test_full_verification(
        clip_path=clip_path,
        text_threshold=text_threshold,
        speaker_threshold=speaker_threshold
    )
    
    # Exit code: 0 if verified, 1 otherwise
    sys.exit(0 if result['verified'] else 1)


if __name__ == "__main__":
    main()

