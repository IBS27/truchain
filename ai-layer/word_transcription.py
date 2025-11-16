#!/usr/bin/env python3
"""
Word-Level Transcription Module
Uses OpenAI Whisper API with word-level timestamps for precise matching.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
import subprocess
import tempfile
import re


class WordTranscriber:
    """
    Transcribes audio with word-level timestamps using OpenAI Whisper API.
    Includes caching to avoid re-transcribing the same videos.
    """
    
    CACHE_DIR = Path("transcription_cache")
    
    def __init__(self, api_key: str = None):
        """
        Initialize transcriber with OpenAI API key.
        
        Args:
            api_key: OpenAI API key (or reads from OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Create cache directory
        self.CACHE_DIR.mkdir(exist_ok=True)
    
    def get_cache_path(self, video_path: str) -> Path:
        """
        Get cache file path for a video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to cache JSON file
        """
        # Create hash of video path for cache filename
        video_hash = hashlib.md5(str(Path(video_path).absolute()).encode()).hexdigest()
        cache_filename = f"{Path(video_path).stem}_{video_hash}.json"
        return self.CACHE_DIR / cache_filename
    
    def load_from_cache(self, video_path: str) -> Optional[Dict]:
        """
        Load transcription from cache if exists.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Cached transcription dict or None if not cached
        """
        cache_path = self.get_cache_path(video_path)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached = json.load(f)
                    print(f"✓ Loaded from cache: {cache_path.name}")
                    return cached
            except Exception as e:
                print(f"⚠️  Cache read error: {e}")
                return None
        
        return None
    
    def save_to_cache(self, video_path: str, transcription: Dict):
        """
        Save transcription to cache.
        
        Args:
            video_path: Path to video file
            transcription: Transcription dict to cache
        """
        cache_path = self.get_cache_path(video_path)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(transcription, f, indent=2)
            print(f"✓ Saved to cache: {cache_path.name}")
        except Exception as e:
            print(f"⚠️  Cache write error: {e}")
    
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video to temporary file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)
        
        # Create temp file
        video_hash = hashlib.md5(str(Path(video_path).absolute()).encode()).hexdigest()[:8]
        output_path = temp_dir / f"audio_{video_hash}.mp3"
        
        # Extract audio using ffmpeg
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-y', str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return str(output_path)
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent matching.
        - Lowercase
        - Remove punctuation (except spaces)
        - Collapse multiple spaces
        
        Args:
            text: Raw text
            
        Returns:
            Normalized text
        """
        # Lowercase
        text = text.lower()
        
        # Remove punctuation except spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing spaces
        text = text.strip()
        
        return text
    
    def transcribe_with_word_timestamps(self, video_path: str, use_cache: bool = True) -> Dict:
        """
        Transcribe video with word-level timestamps.
        
        Args:
            video_path: Path to video file
            use_cache: Whether to use cached transcription if available
            
        Returns:
            {
                'video_path': str,
                'full_text': str,
                'normalized_text': str,
                'words': [
                    {'word': str, 'start': float, 'end': float},
                    ...
                ],
                'duration': float,
                'language': str
            }
        """
        print(f"\nTranscribing: {Path(video_path).name}")
        
        # Check cache first
        if use_cache:
            cached = self.load_from_cache(video_path)
            if cached:
                return cached
        
        # Extract audio
        print("  Extracting audio...")
        audio_path = self.extract_audio(video_path)
        
        try:
            # Transcribe with word-level timestamps
            print("  Calling Whisper API (word-level timestamps)...")
            
            with open(audio_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Extract data
            full_text = response.text
            words = response.words if hasattr(response, 'words') else []
            duration = response.duration if hasattr(response, 'duration') else 0
            language = response.language if hasattr(response, 'language') else 'unknown'
            
            # Normalize text
            normalized_text = self.normalize_text(full_text)
            
            # Create result
            result = {
                'video_path': str(Path(video_path).absolute()),
                'video_name': Path(video_path).name,
                'full_text': full_text,
                'normalized_text': normalized_text,
                'words': [
                    {
                        'word': w.word,
                        'start': w.start,
                        'end': w.end
                    }
                    for w in words
                ],
                'duration': duration,
                'language': language,
                'word_count': len(words)
            }
            
            print(f"  ✓ Transcribed: {len(words)} words, {duration:.1f}s duration")
            
            # Save to cache
            if use_cache:
                self.save_to_cache(video_path, result)
            
            return result
            
        finally:
            # Cleanup temp audio
            try:
                os.remove(audio_path)
            except:
                pass
    
    def transcribe_clip(self, clip_path: str) -> Dict:
        """
        Transcribe a user-submitted clip (no caching for clips).
        
        Args:
            clip_path: Path to clip file
            
        Returns:
            Transcription dict with word-level timestamps
        """
        return self.transcribe_with_word_timestamps(clip_path, use_cache=False)


def main():
    """Test transcription."""
    if len(sys.argv) < 2:
        print("Usage: python word_transcription.py <video_file>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not Path(video_path).exists():
        print(f"Error: Video not found: {video_path}")
        sys.exit(1)
    
    # Transcribe
    transcriber = WordTranscriber()
    result = transcriber.transcribe_with_word_timestamps(video_path)
    
    # Display results
    print("\n" + "="*80)
    print("TRANSCRIPTION RESULTS")
    print("="*80)
    print(f"\nVideo: {result['video_name']}")
    print(f"Duration: {result['duration']:.1f}s")
    print(f"Language: {result['language']}")
    print(f"Word count: {result['word_count']}")
    print(f"\nFull text:\n{result['full_text'][:200]}...")
    print(f"\nNormalized text:\n{result['normalized_text'][:200]}...")
    print(f"\nFirst 10 words:")
    for i, word in enumerate(result['words'][:10]):
        print(f"  {i+1}. [{word['start']:.2f}s - {word['end']:.2f}s] \"{word['word']}\"")
    print()


if __name__ == "__main__":
    main()

