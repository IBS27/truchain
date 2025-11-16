#!/usr/bin/env python3
"""
ML-based Verification Module
Match user-submitted video clips against stored embeddings using neural network embeddings.
"""

import os
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase


@dataclass
class Match:
    """Represents a match between clip and original video."""
    video_id: str
    video_title: str
    clip_timestamp: float
    original_timestamp: float
    confidence: float
    matching_segments: int
    
    def __str__(self):
        return (
            f"Match found in video '{self.video_title}' (ID: {self.video_id})\n"
            f"  Clip timestamp: {self.clip_timestamp:.1f}s\n"
            f"  Original timestamp: {self.original_timestamp:.1f}s\n"
            f"  Confidence: {self.confidence:.1%}\n"
            f"  Matching segments: {self.matching_segments}"
        )


class MLVideoVerifier:
    """Verify videos using ML-based audio embeddings."""
    
    def __init__(self, db_path: str = "video_database_ml.json"):
        """
        Initialize verifier with database.
        
        Args:
            db_path: Path to video database (with embeddings)
        """
        self.db = VideoDatabase(db_path)
        self.embedder = None  # Lazy load
        
        if len(self.db.get_all_videos()) == 0:
            print("Warning: Database is empty. No videos to match against.")
    
    def _ensure_embedder_loaded(self):
        """Lazy load the embedder (since it's heavy)."""
        if self.embedder is None:
            print("Loading ML model...")
            self.embedder = AudioEmbedder()
    
    def calculate_similarity(self, emb1: Dict, emb2: Dict) -> float:
        """
        Calculate similarity between two embeddings.
        
        Args:
            emb1: First embedding dict
            emb2: Second embedding dict
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        vec1 = np.array(emb1['embedding'])
        vec2 = np.array(emb2['embedding'])
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2)
        
        # Convert from [-1, 1] to [0, 1]
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def find_matches(
        self,
        clip_embeddings: List[Dict],
        threshold: float = 0.75,
        min_consecutive: int = 2
    ) -> List[Match]:
        """
        Find matches for clip embeddings in database.
        
        Args:
            clip_embeddings: List of embedding dicts from clip
            threshold: Minimum similarity threshold (0.0 to 1.0)
            min_consecutive: Minimum consecutive embeddings that must match
        
        Returns:
            List of Match objects
        """
        matches = []
        all_videos = self.db.get_all_videos()
        
        print(f"\nSearching against {len(all_videos)} videos in database...")
        print(f"Clip has {len(clip_embeddings)} embeddings to match")
        print(f"Similarity threshold: {threshold:.0%}")
        print(f"Minimum consecutive matches: {min_consecutive}")
        
        for video in all_videos:
            print(f"\n  Checking video: {video['title']}...")
            video_embs = video['fingerprints']  # Actually embeddings in ML db
            
            # Try to find sequences of matching embeddings
            for clip_idx, clip_emb in enumerate(clip_embeddings):
                best_sim = 0.0
                best_video_idx = -1
                
                # Search for this clip embedding in video
                for video_idx, video_emb in enumerate(video_embs):
                    sim = self.calculate_similarity(clip_emb, video_emb)
                    
                    if sim > best_sim:
                        best_sim = sim
                        best_video_idx = video_idx
                
                # Check if we found a good match
                if best_sim >= threshold:
                    # Verify consecutive matches
                    consecutive = 1
                    total_sim = best_sim
                    
                    # Check following embeddings
                    for offset in range(1, min(
                        len(clip_embeddings) - clip_idx,
                        len(video_embs) - best_video_idx
                    )):
                        next_clip_emb = clip_embeddings[clip_idx + offset]
                        next_video_emb = video_embs[best_video_idx + offset]
                        
                        next_sim = self.calculate_similarity(
                            next_clip_emb,
                            next_video_emb
                        )
                        
                        if next_sim >= threshold:
                            consecutive += 1
                            total_sim += next_sim
                        else:
                            break
                    
                    # If we have enough consecutive matches, record it
                    if consecutive >= min_consecutive:
                        avg_confidence = total_sim / consecutive
                        
                        match = Match(
                            video_id=video['id'],
                            video_title=video['title'],
                            clip_timestamp=clip_emb['timestamp'],
                            original_timestamp=video_embs[best_video_idx]['timestamp'],
                            confidence=avg_confidence,
                            matching_segments=consecutive
                        )
                        
                        matches.append(match)
                        print(f"    ✓ Match at {clip_emb['timestamp']:.1f}s (confidence: {avg_confidence:.1%})")
                        
                        # Skip ahead to avoid duplicate matches
                        clip_embeddings = clip_embeddings[clip_idx + consecutive:]
                        break
        
        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches
    
    def verify_clip(
        self,
        clip_path: str,
        threshold: float = 0.75,
        min_consecutive: int = 2
    ) -> List[Match]:
        """
        Verify if a clip exists in the database.
        
        Args:
            clip_path: Path to clip video file
            threshold: Minimum similarity threshold (default: 0.75)
            min_consecutive: Minimum consecutive matches required (default: 2)
        
        Returns:
            List of Match objects (empty if no matches found)
        """
        print(f"\n{'='*70}")
        print(f"ML-Based Video Verification")
        print(f"{'='*70}")
        print(f"Clip: {Path(clip_path).name}")
        print(f"{'='*70}")
        
        # Ensure embedder is loaded
        self._ensure_embedder_loaded()
        
        # Generate embeddings for clip
        clip_embeddings = self.embedder.generate_embeddings(clip_path)
        
        # Find matches
        print(f"\n{'='*70}")
        print("Searching for Matches")
        print(f"{'='*70}")
        
        matches = self.find_matches(
            clip_embeddings,
            threshold=threshold,
            min_consecutive=min_consecutive
        )
        
        return matches


def main():
    """Command-line interface for ML-based clip verification."""
    if len(sys.argv) < 2:
        print("Usage: python3.10 verification_ml.py <clip_file> [options]")
        print("\nOptions:")
        print("  --db <path>           Database file (default: video_database_ml.json)")
        print("  --threshold <float>   Similarity threshold 0.0-1.0 (default: 0.75)")
        print("  --min-matches <int>   Min consecutive matches (default: 2)")
        print("\nExamples:")
        print("  python3.10 verification_ml.py clip.mp4")
        print("  python3.10 verification_ml.py clip.mp4 --threshold 0.8")
        print("  python3.10 verification_ml.py clip.mp4 --db custom_db.json --min-matches 3")
        sys.exit(1)
    
    # Parse arguments
    clip_path = sys.argv[1]
    db_path = "video_database_ml.json"
    threshold = 0.75
    min_consecutive = 2
    
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
            min_consecutive = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    # Validate inputs
    if not Path(clip_path).exists():
        print(f"Error: Clip file not found: {clip_path}")
        sys.exit(1)
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        print("Please process some videos first using process_videos_ml.py")
        sys.exit(1)
    
    try:
        # Verify clip
        verifier = MLVideoVerifier(db_path)
        matches = verifier.verify_clip(
            clip_path,
            threshold=threshold,
            min_consecutive=min_consecutive
        )
        
        # Display results
        print(f"\n{'='*70}")
        print("VERIFICATION RESULTS")
        print(f"{'='*70}\n")
        
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
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

