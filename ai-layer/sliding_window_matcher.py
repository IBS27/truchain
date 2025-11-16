#!/usr/bin/env python3
"""
Sliding Window Text Matcher
Finds clips in videos by sliding through word sequences.
"""

from typing import List, Dict, Optional
from difflib import SequenceMatcher
import re


class SlidingWindowMatcher:
    """
    Matches clip text against video text using sliding window approach.
    Maps matching positions back to word-level timestamps.
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize matcher.
        
        Args:
            similarity_threshold: Minimum similarity (0.0-1.0) to consider a match
        """
        self.similarity_threshold = similarity_threshold
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using SequenceMatcher.
        
        Args:
            text1: First text (normalized)
            text2: Second text (normalized)
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def split_into_words(self, text: str) -> List[str]:
        """
        Split normalized text into word array.
        
        Args:
            text: Normalized text
            
        Returns:
            List of words
        """
        return text.split()
    
    def find_best_match(
        self,
        clip_transcription: Dict,
        video_transcription: Dict
    ) -> Optional[Dict]:
        """
        Find best matching position of clip in video using sliding window.
        
        Args:
            clip_transcription: Clip transcription with normalized_text and words
            video_transcription: Video transcription with normalized_text and words
            
        Returns:
            {
                'video_path': str,
                'video_name': str,
                'start_time': float,
                'end_time': float,
                'similarity': float,
                'start_word_index': int,
                'end_word_index': int,
                'matched_text': str
            }
            or None if no match found
        """
        clip_words = self.split_into_words(clip_transcription['normalized_text'])
        video_words = self.split_into_words(video_transcription['normalized_text'])
        
        clip_word_count = len(clip_words)
        video_word_count = len(video_words)
        
        if clip_word_count == 0 or video_word_count == 0:
            return None
        
        if clip_word_count > video_word_count:
            # Clip is longer than video, can't match
            return None
        
        # Sliding window search
        best_match = None
        best_similarity = 0.0
        best_position = -1
        
        # Slide through video, extracting windows of clip length
        for start_idx in range(video_word_count - clip_word_count + 1):
            end_idx = start_idx + clip_word_count
            
            # Extract window
            window_words = video_words[start_idx:end_idx]
            window_text = ' '.join(window_words)
            clip_text = ' '.join(clip_words)
            
            # Calculate similarity
            similarity = self.calculate_text_similarity(clip_text, window_text)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_position = start_idx
        
        # Check if best match exceeds threshold
        if best_similarity < self.similarity_threshold:
            return None
        
        # Map word position to timestamp
        start_word_index = best_position
        end_word_index = best_position + clip_word_count - 1
        
        # Get timestamps from video's word list
        video_word_list = video_transcription['words']
        
        if start_word_index >= len(video_word_list) or end_word_index >= len(video_word_list):
            return None
        
        start_time = video_word_list[start_word_index]['start']
        end_time = video_word_list[end_word_index]['end']
        
        # Get matched text for display
        matched_words = video_words[start_word_index:end_word_index + 1]
        matched_text = ' '.join(matched_words)
        
        return {
            'video_path': video_transcription['video_path'],
            'video_name': video_transcription['video_name'],
            'start_time': start_time,
            'end_time': end_time,
            'similarity': best_similarity,
            'start_word_index': start_word_index,
            'end_word_index': end_word_index,
            'matched_text': matched_text,
            'clip_word_count': clip_word_count,
            'duration': end_time - start_time
        }
    
    def search_all_videos(
        self,
        clip_transcription: Dict,
        video_transcriptions: List[Dict]
    ) -> List[Dict]:
        """
        Search clip in all videos and return matches sorted by similarity.
        
        Args:
            clip_transcription: Clip transcription
            video_transcriptions: List of video transcriptions
            
        Returns:
            List of matches sorted by similarity (highest first)
        """
        matches = []
        
        print(f"\nSearching clip in {len(video_transcriptions)} videos...")
        print(f"Clip: {len(clip_transcription.get('words', []))} words")
        print()
        
        for i, video_trans in enumerate(video_transcriptions, 1):
            print(f"  [{i}/{len(video_transcriptions)}] Searching in {video_trans['video_name']}...")
            
            match = self.find_best_match(clip_transcription, video_trans)
            
            if match:
                matches.append(match)
                print(f"    ✓ Match found: {match['similarity']:.1%} at {match['start_time']:.1f}s")
            else:
                print(f"    ✗ No match (threshold: {self.similarity_threshold:.1%})")
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches


def format_time(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def main():
    """Test matcher with sample data."""
    # Sample clip
    clip = {
        'normalized_text': 'the federal reserve has decided to maintain interest rates',
        'words': [
            {'word': 'the', 'start': 0.0, 'end': 0.1},
            {'word': 'federal', 'start': 0.15, 'end': 0.5},
            {'word': 'reserve', 'start': 0.55, 'end': 0.9},
            {'word': 'has', 'start': 0.95, 'end': 1.1},
            {'word': 'decided', 'start': 1.15, 'end': 1.6},
            {'word': 'to', 'start': 1.65, 'end': 1.75},
            {'word': 'maintain', 'start': 1.8, 'end': 2.3},
            {'word': 'interest', 'start': 2.35, 'end': 2.8},
            {'word': 'rates', 'start': 2.85, 'end': 3.2}
        ]
    }
    
    # Sample video
    video = {
        'video_path': 'test_video.mp4',
        'video_name': 'test_video.mp4',
        'normalized_text': 'good afternoon my colleagues and i remain focused on our goals the federal reserve has decided to maintain interest rates at their current level we will continue monitoring',
        'words': [
            {'word': 'good', 'start': 0.0, 'end': 0.3},
            {'word': 'afternoon', 'start': 0.35, 'end': 0.8},
            {'word': 'my', 'start': 0.85, 'end': 1.0},
            {'word': 'colleagues', 'start': 1.05, 'end': 1.6},
            {'word': 'and', 'start': 1.65, 'end': 1.8},
            {'word': 'i', 'start': 1.85, 'end': 1.95},
            {'word': 'remain', 'start': 2.0, 'end': 2.4},
            {'word': 'focused', 'start': 2.45, 'end': 2.9},
            {'word': 'on', 'start': 2.95, 'end': 3.1},
            {'word': 'our', 'start': 3.15, 'end': 3.3},
            {'word': 'goals', 'start': 3.35, 'end': 3.7},
            {'word': 'the', 'start': 3.75, 'end': 3.85},
            {'word': 'federal', 'start': 3.9, 'end': 4.3},
            {'word': 'reserve', 'start': 4.35, 'end': 4.7},
            {'word': 'has', 'start': 4.75, 'end': 4.9},
            {'word': 'decided', 'start': 4.95, 'end': 5.4},
            {'word': 'to', 'start': 5.45, 'end': 5.55},
            {'word': 'maintain', 'start': 5.6, 'end': 6.1},
            {'word': 'interest', 'start': 6.15, 'end': 6.6},
            {'word': 'rates', 'start': 6.65, 'end': 7.0},
            {'word': 'at', 'start': 7.05, 'end': 7.15},
            {'word': 'their', 'start': 7.2, 'end': 7.4},
            {'word': 'current', 'start': 7.45, 'end': 7.9},
            {'word': 'level', 'start': 7.95, 'end': 8.3},
            {'word': 'we', 'start': 8.35, 'end': 8.45},
            {'word': 'will', 'start': 8.5, 'end': 8.7},
            {'word': 'continue', 'start': 8.75, 'end': 9.2},
            {'word': 'monitoring', 'start': 9.25, 'end': 9.8}
        ]
    }
    
    # Test matcher
    matcher = SlidingWindowMatcher(similarity_threshold=0.85)
    match = matcher.find_best_match(clip, video)
    
    print("\n" + "="*80)
    print("SLIDING WINDOW MATCHER TEST")
    print("="*80)
    
    if match:
        print(f"\n✓ Match found!")
        print(f"  Video: {match['video_name']}")
        print(f"  Time: {format_time(match['start_time'])} - {format_time(match['end_time'])}")
        print(f"  Similarity: {match['similarity']:.1%}")
        print(f"  Word range: {match['start_word_index']} - {match['end_word_index']}")
        print(f"  Matched text: {match['matched_text'][:80]}...")
    else:
        print("\n✗ No match found")
    print()


if __name__ == "__main__":
    main()

