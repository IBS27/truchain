#!/usr/bin/env python3
"""
Video Verification System V2
Uses word-level timestamps and sliding window matching.
"""

import sys
from pathlib import Path
from typing import List, Dict
from word_transcription import WordTranscriber
from sliding_window_matcher import SlidingWindowMatcher, format_time


class VideoVerifierV2:
    """
    Verifies video clips using word-level timestamp matching.
    """
    
    def __init__(self, similarity_threshold: float = 0.85, api_key: str = None):
        """
        Initialize verifier.
        
        Args:
            similarity_threshold: Minimum similarity for a match (0.0-1.0)
            api_key: OpenAI API key
        """
        self.transcriber = WordTranscriber(api_key=api_key)
        self.matcher = SlidingWindowMatcher(similarity_threshold=similarity_threshold)
        self.similarity_threshold = similarity_threshold
    
    def verify_clip(self, clip_path: str, video_directory: str = "download") -> Dict:
        """
        Verify a clip against all videos in a directory.
        
        Args:
            clip_path: Path to clip file
            video_directory: Directory containing original videos
            
        Returns:
            {
                'verified': bool,
                'clip_path': str,
                'matches': [
                    {
                        'video_name': str,
                        'start_time': float,
                        'end_time': float,
                        'similarity': float,
                        ...
                    },
                    ...
                ],
                'best_match': {...} or None
            }
        """
        print("\n" + "="*80)
        print("VIDEO VERIFICATION V2 - WORD-LEVEL TIMESTAMPS")
        print("="*80)
        print(f"\nClip: {Path(clip_path).name}")
        print(f"Video directory: {video_directory}")
        print(f"Similarity threshold: {self.similarity_threshold:.1%}\n")
        
        # Step 1: Transcribe clip
        print("STEP 1: Transcribing Clip")
        print("-"*80)
        
        try:
            clip_transcription = self.transcriber.transcribe_clip(clip_path)
        except Exception as e:
            return {
                'verified': False,
                'clip_path': clip_path,
                'error': f"Failed to transcribe clip: {e}",
                'matches': [],
                'best_match': None
            }
        
        # Step 2: Get all videos in directory
        print("\nSTEP 2: Loading Video Transcriptions")
        print("-"*80)
        
        video_dir = Path(video_directory)
        if not video_dir.exists():
            return {
                'verified': False,
                'clip_path': clip_path,
                'error': f"Video directory not found: {video_directory}",
                'matches': [],
                'best_match': None
            }
        
        # Find all video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        video_files = []
        for ext in video_extensions:
            video_files.extend(video_dir.glob(f"*{ext}"))
        
        if not video_files:
            return {
                'verified': False,
                'clip_path': clip_path,
                'error': f"No video files found in {video_directory}",
                'matches': [],
                'best_match': None
            }
        
        print(f"Found {len(video_files)} video(s) to search\n")
        
        # Transcribe all videos (with caching)
        video_transcriptions = []
        for i, video_path in enumerate(video_files, 1):
            print(f"[{i}/{len(video_files)}] Processing {video_path.name}...")
            try:
                transcription = self.transcriber.transcribe_with_word_timestamps(str(video_path))
                video_transcriptions.append(transcription)
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
        
        if not video_transcriptions:
            return {
                'verified': False,
                'clip_path': clip_path,
                'error': "Failed to transcribe any videos",
                'matches': [],
                'best_match': None
            }
        
        # Step 3: Search for matches
        print("\nSTEP 3: Sliding Window Search")
        print("-"*80)
        
        matches = self.matcher.search_all_videos(clip_transcription, video_transcriptions)
        
        # Step 4: Display results
        print("\nSTEP 4: Results")
        print("-"*80)
        
        if not matches:
            print(f"\n✗ No matches found (threshold: {self.similarity_threshold:.1%})")
            return {
                'verified': False,
                'clip_path': clip_path,
                'matches': [],
                'best_match': None,
                'clip_info': {
                    'word_count': clip_transcription['word_count'],
                    'duration': clip_transcription['duration'],
                    'text': clip_transcription['full_text']
                }
            }
        
        print(f"\n✓ Found {len(matches)} match(es):\n")
        
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['video_name']}")
            print(f"   Time: {format_time(match['start_time'])} - {format_time(match['end_time'])}")
            print(f"   Similarity: {match['similarity']:.2%}")
            print(f"   Duration: {match['duration']:.1f}s")
            print()
        
        best_match = matches[0]
        
        print("="*80)
        print("BEST MATCH")
        print("="*80)
        print(f"\n✓ VERIFIED: Clip found in {best_match['video_name']}")
        print(f"  Timestamp: {format_time(best_match['start_time'])} - {format_time(best_match['end_time'])}")
        print(f"  Similarity: {best_match['similarity']:.2%}")
        print(f"  Matched text: {best_match['matched_text'][:100]}...")
        print()
        
        return {
            'verified': True,
            'clip_path': clip_path,
            'matches': matches,
            'best_match': best_match,
            'clip_info': {
                'word_count': clip_transcription['word_count'],
                'duration': clip_transcription['duration'],
                'text': clip_transcription['full_text']
            }
        }


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify video clip using word-level timestamps")
    parser.add_argument("clip", help="Path to clip file")
    parser.add_argument("--videos", default="download", help="Directory containing original videos")
    parser.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold (0.0-1.0)")
    
    args = parser.parse_args()
    
    # Check clip exists
    if not Path(args.clip).exists():
        print(f"Error: Clip not found: {args.clip}")
        sys.exit(1)
    
    # Verify
    verifier = VideoVerifierV2(similarity_threshold=args.threshold)
    result = verifier.verify_clip(args.clip, args.videos)
    
    # Exit code
    sys.exit(0 if result['verified'] else 1)


if __name__ == "__main__":
    main()

