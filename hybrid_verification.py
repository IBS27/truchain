#!/usr/bin/env python3
"""
Hybrid Verification System

Two-stage verification for political campaign videos:
1. CONTENT MATCHING: Transcribe and match text to find WHAT was said
2. SPEAKER VERIFICATION: Compare audio embeddings to verify WHO said it

This prevents:
- False positives (different speech by same person)
- Deepfakes (same words by different voice)
- Out-of-context clips (shows original context with timestamps)
"""

from pathlib import Path
from typing import Dict, List, Optional
import json

from audio_transcription import AudioTranscriber
from text_matching import TextMatcher, format_timestamp
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase


class HybridVerifier:
    """
    Two-stage video verification: text matching + speaker verification.
    """
    
    # Thresholds for verification
    TEXT_SIMILARITY_THRESHOLD = 0.75  # Minimum text similarity for content match
    SPEAKER_SIMILARITY_THRESHOLD = 0.90  # Minimum audio similarity for speaker match
    MIN_CONSECUTIVE_MATCHES = 2  # Minimum consecutive segments to match
    
    def __init__(self, database_path: str = "video_database_hybrid.json", openai_api_key: str = None):
        """
        Initialize hybrid verifier.
        
        Args:
            database_path: Path to video database
            openai_api_key: OpenAI API key for transcription
        """
        self.database_path = database_path
        
        # Initialize components
        print("Initializing Hybrid Verification System...")
        print("="*80)
        
        self.transcriber = AudioTranscriber(api_key=openai_api_key)
        self.text_matcher = TextMatcher(use_semantic_embeddings=True)
        self.audio_embedder = AudioEmbedder()
        
        # Load database
        self.db = VideoDatabase(database_path)
        
        print("✓ System ready\n")
    
    def verify_clip(self, clip_path: str, verbose: bool = True) -> Dict:
        """
        Verify if a clip is authentic excerpt from database videos.
        
        Args:
            clip_path: Path to user-submitted video clip
            verbose: Print detailed progress information
            
        Returns:
            {
                'verified': True/False,
                'confidence': 'high'/'medium'/'low',
                'matched_video': {
                    'video_id': '...',
                    'title': '...',
                    'ipfs_cid': '...'
                },
                'content_match': {
                    'similarity': 0.92,
                    'start_timestamp': 120.0,
                    'end_timestamp': 180.0,
                    'matched_segments': [...]
                },
                'speaker_match': {
                    'similarity': 0.95,
                    'verified': True
                },
                'explanation': 'Human-readable explanation'
            }
            or
            {
                'verified': False,
                'reason': 'No content match found'
            }
        """
        if verbose:
            print("\n" + "="*80)
            print("HYBRID VERIFICATION")
            print("="*80)
            print(f"\nVerifying clip: {clip_path}\n")
        
        # STAGE 1: Transcribe the clip
        if verbose:
            print("STAGE 1: Content Analysis (Transcription)")
            print("-"*80)
        
        clip_transcripts = self.transcriber.transcribe_video(clip_path)
        
        if not clip_transcripts:
            return {
                'verified': False,
                'reason': 'Failed to transcribe clip'
            }
        
        # STAGE 2: Find matching content in database
        if verbose:
            print("\nSTAGE 2: Database Search (Text Matching)")
            print("-"*80)
        
        # Build database dictionary for text matcher
        db_videos = self.db.get_all_videos()
        text_database = {}
        
        for video in db_videos:
            video_id = video['ipfs_cid']
            if 'transcripts' in video:
                text_database[video_id] = video['transcripts']
        
        if not text_database:
            return {
                'verified': False,
                'reason': 'No transcripts in database. Please process videos first.'
            }
        
        # Find best match
        content_match = self.text_matcher.find_best_match_in_database(
            clip_transcripts,
            text_database,
            threshold=self.TEXT_SIMILARITY_THRESHOLD,
            min_consecutive_matches=self.MIN_CONSECUTIVE_MATCHES
        )
        
        if not content_match:
            if verbose:
                print("\n✗ No content match found")
                print("  The clip's transcript doesn't match any video in the database.\n")
            
            return {
                'verified': False,
                'reason': 'No matching content found in database',
                'stage_failed': 'content_matching'
            }
        
        if verbose:
            print(f"\n✓ Content match found!")
            print(f"  Video ID: {content_match['video_id']}")
            print(f"  Timestamp: {format_timestamp(content_match['start_timestamp'])} - {format_timestamp(content_match['end_timestamp'])}")
            print(f"  Similarity: {content_match['avg_similarity']:.1%}")
            print(f"  Consecutive matches: {content_match['num_matches']}")
        
        # Get matched video details
        matched_video = None
        for video in db_videos:
            if video['ipfs_cid'] == content_match['video_id']:
                matched_video = video
                break
        
        if not matched_video:
            return {
                'verified': False,
                'reason': 'Matched video not found in database'
            }
        
        # STAGE 3: Verify speaker identity
        if verbose:
            print("\nSTAGE 3: Speaker Verification (Audio Embeddings)")
            print("-"*80)
        
        # Extract audio embeddings from clip at matched timestamps
        clip_embeddings = self.audio_embedder.generate_embeddings(clip_path)
        
        # Compare embeddings at matched timestamps
        speaker_similarities = []
        
        for i, match in enumerate(content_match['matches'][:5]):  # Check first 5 matches
            clip_time = match['query_timestamp']
            db_time = match['db_timestamp']
            
            # Find embeddings at these timestamps
            clip_emb = self._find_embedding_at_time(clip_embeddings, clip_time)
            db_emb = self._find_embedding_at_time(matched_video.get('fingerprints', []), db_time)
            
            if clip_emb and db_emb:
                similarity = self.audio_embedder.calculate_similarity(clip_emb, db_emb)
                speaker_similarities.append(similarity)
                
                if verbose and i < 3:  # Show first 3
                    print(f"  Segment {i+1}: {similarity:.1%}")
        
        if not speaker_similarities:
            if verbose:
                print("\n⚠️  Warning: Could not verify speaker (no audio embeddings)")
            
            speaker_verified = False
            speaker_similarity = 0.0
        else:
            import numpy as np
            speaker_similarity = float(np.mean(speaker_similarities))
            speaker_verified = speaker_similarity >= self.SPEAKER_SIMILARITY_THRESHOLD
            
            if verbose:
                print(f"\n  Average speaker similarity: {speaker_similarity:.1%}")
                if speaker_verified:
                    print(f"  ✓ Speaker verified (threshold: {self.SPEAKER_SIMILARITY_THRESHOLD:.1%})")
                else:
                    print(f"  ✗ Speaker NOT verified (threshold: {self.SPEAKER_SIMILARITY_THRESHOLD:.1%})")
                    print(f"    This might be a deepfake or voiceover!")
        
        # FINAL VERDICT
        if verbose:
            print("\n" + "="*80)
            print("FINAL VERDICT")
            print("="*80 + "\n")
        
        # Determine overall confidence
        if speaker_verified and content_match['confidence'] == 'high':
            final_confidence = 'high'
            verified = True
            explanation = f"✓ VERIFIED with HIGH confidence. Content matches at {format_timestamp(content_match['start_timestamp'])} and speaker is verified."
        elif speaker_verified and content_match['confidence'] == 'medium':
            final_confidence = 'medium'
            verified = True
            explanation = f"✓ VERIFIED with MEDIUM confidence. Content matches reasonably well and speaker is verified."
        elif content_match['confidence'] == 'high' and not speaker_verified:
            final_confidence = 'low'
            verified = False
            explanation = f"⚠️  Content matches, but speaker verification failed. Possible deepfake or voiceover."
        else:
            final_confidence = 'low'
            verified = False
            explanation = f"⚠️  Weak match. Content similarity and/or speaker verification below threshold."
        
        if verbose:
            print(f"  {explanation}\n")
        
        return {
            'verified': verified,
            'confidence': final_confidence,
            'matched_video': {
                'video_id': matched_video['ipfs_cid'],
                'title': matched_video.get('title', 'Unknown'),
                'ipfs_cid': matched_video['ipfs_cid']
            },
            'content_match': {
                'similarity': content_match['avg_similarity'],
                'start_timestamp': content_match['start_timestamp'],
                'end_timestamp': content_match['end_timestamp'],
                'num_matches': content_match['num_matches'],
                'matched_segments': content_match['matches']
            },
            'speaker_match': {
                'similarity': speaker_similarity,
                'verified': speaker_verified,
                'threshold': self.SPEAKER_SIMILARITY_THRESHOLD
            },
            'explanation': explanation
        }
    
    def _find_embedding_at_time(self, embeddings: List[Dict], timestamp: float) -> Optional[Dict]:
        """Find embedding closest to given timestamp."""
        if not embeddings:
            return None
        
        closest = min(embeddings, key=lambda e: abs(e.get('timestamp', 0) - timestamp))
        
        # Only return if within 5 seconds
        if abs(closest.get('timestamp', 0) - timestamp) <= 5:
            return closest
        
        return None


def main():
    """Test the hybrid verification system."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hybrid_verification.py <clip_path>")
        print("\nExample:")
        print("  python hybrid_verification.py test_clips/exact_clip_10s.mp4")
        sys.exit(1)
    
    clip_path = sys.argv[1]
    
    if not Path(clip_path).exists():
        print(f"Error: Clip not found: {clip_path}")
        sys.exit(1)
    
    # Initialize verifier
    verifier = HybridVerifier()
    
    # Verify clip
    result = verifier.verify_clip(clip_path, verbose=True)
    
    # Print result summary
    if result['verified']:
        print(f"🎯 RESULT: VERIFIED ({result['confidence']} confidence)")
    else:
        print(f"❌ RESULT: NOT VERIFIED")
        if 'reason' in result:
            print(f"   Reason: {result['reason']}")


if __name__ == "__main__":
    main()

