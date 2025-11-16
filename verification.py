#!/usr/bin/env python3
"""
Verification Module
Match user-submitted video clips against stored fingerprints.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from audio_fingerprint import AudioFingerprinter
from video_processor import VideoDatabase


@dataclass
class Match:
    """Represents a match between clip and original video."""
    video_id: str
    video_title: str
    clip_timestamp: float
    original_timestamp: float
    confidence: float
    fingerprint_matches: int
    
    def __str__(self):
        return (
            f"Match found in video '{self.video_title}' (ID: {self.video_id})\n"
            f"  Clip timestamp: {self.clip_timestamp:.1f}s\n"
            f"  Original timestamp: {self.original_timestamp:.1f}s\n"
            f"  Confidence: {self.confidence:.1%}\n"
            f"  Matching fingerprints: {self.fingerprint_matches}"
        )


class VideoVerifier:
    """Verify if a clip exists in the database of original videos."""
    
    def __init__(self, db_path: str = "video_database.json"):
        """
        Initialize verifier with database.
        
        Args:
            db_path: Path to video database
        """
        self.db = VideoDatabase(db_path)
        if len(self.db.get_all_videos()) == 0:
            print("Warning: Database is empty. No videos to match against.")
    
    def calculate_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """
        Calculate similarity between two fingerprints using chromaprint comparison.
        Uses bit counting on XOR of fingerprint integers (proper audio fingerprint comparison).
        
        Args:
            fp1: First fingerprint dict with 'fingerprint' array
            fp2: Second fingerprint dict with 'fingerprint' array
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Get fingerprint arrays
        arr1 = fp1.get('fingerprint', [])
        arr2 = fp2.get('fingerprint', [])
        
        if not arr1 or not arr2:
            # Fallback to hash comparison if no arrays
            hash1 = fp1.get('hash', '')
            hash2 = fp2.get('hash', '')
            if len(hash1) != len(hash2):
                return 0.0
            differences = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            return 1.0 - (differences / len(hash1))
        
        # Use shorter length for comparison
        min_len = min(len(arr1), len(arr2))
        if min_len == 0:
            return 0.0
        
        # Calculate bit differences using XOR and popcount
        total_bits = 0
        different_bits = 0
        
        for i in range(min_len):
            # XOR the two integers to find differing bits
            xor_result = arr1[i] ^ arr2[i]
            # Count number of set bits (differing bits)
            different_bits += bin(xor_result).count('1')
            # Each integer has 32 bits
            total_bits += 32
        
        # Calculate similarity (inverse of bit error rate)
        if total_bits == 0:
            return 0.0
        
        similarity = 1.0 - (different_bits / total_bits)
        return similarity
    
    def find_matches(
        self,
        clip_fingerprints: List[Dict],
        threshold: float = 0.85,
        min_consecutive_matches: int = 2
    ) -> List[Match]:
        """
        Find matches for clip fingerprints in database.
        
        Args:
            clip_fingerprints: List of fingerprint dicts from clip
            threshold: Minimum similarity threshold (0.0 to 1.0)
            min_consecutive_matches: Minimum consecutive fingerprints that must match
        
        Returns:
            List of Match objects
        """
        matches = []
        all_videos = self.db.get_all_videos()
        
        print(f"\nSearching against {len(all_videos)} videos in database...")
        print(f"Clip has {len(clip_fingerprints)} fingerprints to match")
        print(f"Similarity threshold: {threshold:.0%}")
        print(f"Minimum consecutive matches: {min_consecutive_matches}")
        
        for video in all_videos:
            print(f"\n  Checking video: {video['title']}...")
            video_fps = video['fingerprints']
            
            # Try to find sequences of matching fingerprints
            for clip_idx, clip_fp in enumerate(clip_fingerprints):
                best_match_similarity = 0.0
                best_match_idx = -1
                
                # Search for this clip fingerprint in video
                for video_idx, video_fp in enumerate(video_fps):
                    similarity = self.calculate_similarity(
                        clip_fp,
                        video_fp
                    )
                    
                    if similarity > best_match_similarity:
                        best_match_similarity = similarity
                        best_match_idx = video_idx
                
                # Check if we found a good match
                if best_match_similarity >= threshold:
                    # Verify consecutive matches
                    consecutive_matches = 1
                    total_similarity = best_match_similarity
                    
                    # Check following fingerprints
                    for offset in range(1, min(
                        len(clip_fingerprints) - clip_idx,
                        len(video_fps) - best_match_idx
                    )):
                        next_clip_fp = clip_fingerprints[clip_idx + offset]
                        next_video_fp = video_fps[best_match_idx + offset]
                        
                        similarity = self.calculate_similarity(
                            next_clip_fp,
                            next_video_fp
                        )
                        
                        if similarity >= threshold:
                            consecutive_matches += 1
                            total_similarity += similarity
                        else:
                            break
                    
                    # If we have enough consecutive matches, record it
                    if consecutive_matches >= min_consecutive_matches:
                        avg_confidence = total_similarity / consecutive_matches
                        
                        match = Match(
                            video_id=video['id'],
                            video_title=video['title'],
                            clip_timestamp=clip_fp['timestamp'],
                            original_timestamp=video_fps[best_match_idx]['timestamp'],
                            confidence=avg_confidence,
                            fingerprint_matches=consecutive_matches
                        )
                        
                        matches.append(match)
                        
                        # Skip ahead to avoid duplicate matches
                        clip_fingerprints = clip_fingerprints[clip_idx + consecutive_matches:]
                        break
        
        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches
    
    def verify_clip(
        self,
        clip_path: str,
        threshold: float = 0.85,
        min_consecutive_matches: int = 2
    ) -> List[Match]:
        """
        Verify if a clip exists in the database.
        
        Args:
            clip_path: Path to clip video file
            threshold: Minimum similarity threshold (default: 0.85)
            min_consecutive_matches: Minimum consecutive matches required (default: 2)
        
        Returns:
            List of Match objects (empty if no matches found)
        """
        print(f"\n{'='*60}")
        print(f"Verifying Clip: {Path(clip_path).name}")
        print(f"{'='*60}")
        
        # Generate fingerprints for clip
        fingerprinter = AudioFingerprinter(clip_path)
        clip_fingerprints = fingerprinter.generate_fingerprints()
        
        # Find matches
        print(f"\n{'='*60}")
        print("Searching for Matches")
        print(f"{'='*60}")
        
        matches = self.find_matches(
            clip_fingerprints,
            threshold=threshold,
            min_consecutive_matches=min_consecutive_matches
        )
        
        return matches


def main():
    """Command-line interface for clip verification."""
    if len(sys.argv) < 2:
        print("Usage: python verification.py <clip_file> [options]")
        print("\nOptions:")
        print("  --db <path>           Database file (default: video_database.json)")
        print("  --threshold <float>   Similarity threshold 0.0-1.0 (default: 0.85)")
        print("  --min-matches <int>   Min consecutive matches (default: 2)")
        print("\nExamples:")
        print("  python verification.py clip.mp4")
        print("  python verification.py clip.mp4 --threshold 0.9")
        print("  python verification.py clip.mp4 --db custom_db.json --min-matches 3")
        sys.exit(1)
    
    # Parse arguments
    clip_path = sys.argv[1]
    db_path = "video_database.json"
    threshold = 0.85
    min_consecutive_matches = 2
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--db' and i + 1 < len(sys.argv):
            db_path = sys.argv[i + 1]
            i += 2
        elif arg == '--threshold' and i + 1 < len(sys.argv):
            threshold = float(sys.argv[i + 1])
            i += 2
        elif arg == '--min-matches' and i + 1 < len(sys.argv):
            min_consecutive_matches = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    # Validate inputs
    if not Path(clip_path).exists():
        print(f"Error: Clip file not found: {clip_path}")
        sys.exit(1)
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        print("Please process some videos first using video_processor.py")
        sys.exit(1)
    
    try:
        # Verify clip
        verifier = VideoVerifier(db_path)
        matches = verifier.verify_clip(
            clip_path,
            threshold=threshold,
            min_consecutive_matches=min_consecutive_matches
        )
        
        # Display results
        print(f"\n{'='*60}")
        print("VERIFICATION RESULTS")
        print(f"{'='*60}\n")
        
        if matches:
            print(f"✓ MATCH FOUND! Found {len(matches)} match(es):\n")
            for i, match in enumerate(matches, 1):
                print(f"Match #{i}:")
                print(match)
                print()
        else:
            print("✗ NO MATCH FOUND")
            print("This clip does not appear to be from any video in the database.")
            print("\nPossible reasons:")
            print("  - Clip is from a different video")
            print("  - Audio quality is too degraded")
            print("  - Try lowering the --threshold parameter")
        
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

