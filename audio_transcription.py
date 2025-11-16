#!/usr/bin/env python3
"""
Audio Transcription Module
Transcribes video audio into text segments with timestamps.
Uses OpenAI Whisper API for accurate speech-to-text.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Dict
import hashlib
from openai import OpenAI


class AudioTranscriber:
    """
    Transcribes video audio into text segments.
    """
    
    SEGMENT_DURATION = 30  # 30-second segments for granular matching
    
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
        
        # Create temp directory
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    
    def extract_audio_segment(self, video_path: str, start_time: float, duration: float) -> Path:
        """
        Extract audio segment from video.
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            Path to extracted audio file
        """
        # Create unique filename
        hash_str = hashlib.md5(f"{video_path}_{start_time}_{duration}".encode()).hexdigest()[:8]
        output_path = self.temp_dir / f"segment_{hash_str}.mp3"
        
        # Skip if already extracted
        if output_path.exists():
            return output_path
        
        cmd = [
            'ffmpeg', '-i', video_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-vn', '-acodec', 'libmp3lame',
            '-ar', '16000', '-ac', '1',
            '-y', str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    def transcribe_audio_file(self, audio_path: Path) -> str:
        """
        Transcribe audio file using OpenAI Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript.strip()
    
    def transcribe_video(self, video_path: str, progress_callback=None) -> List[Dict]:
        """
        Transcribe entire video into segments.
        
        Args:
            video_path: Path to video file
            progress_callback: Optional callback function(current, total) for progress
            
        Returns:
            List of transcript segments with timestamps:
            [
                {
                    'timestamp': 0.0,
                    'duration': 30.0,
                    'text': 'Transcribed text...',
                    'hash': 'sha256_hash_of_text'
                },
                ...
            ]
        """
        print(f"\nTranscribing video: {video_path}")
        
        # Get video duration
        video_duration = self.get_video_duration(video_path)
        print(f"Video duration: {video_duration:.1f} seconds")
        
        # Calculate number of segments
        num_segments = int(video_duration / self.SEGMENT_DURATION) + 1
        print(f"Processing {num_segments} segments...\n")
        
        transcripts = []
        
        for i in range(num_segments):
            start_time = i * self.SEGMENT_DURATION
            
            # Don't exceed video duration
            if start_time >= video_duration:
                break
            
            # Adjust duration for last segment
            duration = min(self.SEGMENT_DURATION, video_duration - start_time)
            
            if progress_callback:
                progress_callback(i + 1, num_segments)
            
            print(f"  Segment {i+1}/{num_segments}: {start_time:.1f}s - {start_time+duration:.1f}s")
            
            try:
                # Extract audio segment
                audio_path = self.extract_audio_segment(video_path, start_time, duration)
                
                # Transcribe
                text = self.transcribe_audio_file(audio_path)
                
                # Create hash of text for blockchain storage
                text_hash = hashlib.sha256(text.encode()).hexdigest()
                
                transcripts.append({
                    'timestamp': start_time,
                    'duration': duration,
                    'text': text,
                    'hash': text_hash
                })
                
                print(f"    ✓ \"{text[:80]}...\"")
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                # Store empty transcript for this segment
                transcripts.append({
                    'timestamp': start_time,
                    'duration': duration,
                    'text': '',
                    'hash': ''
                })
        
        print(f"\n✓ Transcription complete: {len(transcripts)} segments")
        return transcripts
    
    def cleanup_temp_files(self):
        """Remove temporary audio files."""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("segment_*.mp3"):
                try:
                    file.unlink()
                except:
                    pass


# Convenience function for quick transcription
def transcribe_video(video_path: str, api_key: str = None) -> List[Dict]:
    """
    Convenience function to transcribe a video.
    
    Args:
        video_path: Path to video file
        api_key: OpenAI API key (optional)
        
    Returns:
        List of transcript segments
    """
    transcriber = AudioTranscriber(api_key=api_key)
    return transcriber.transcribe_video(video_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_transcription.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not Path(video_path).exists():
        print(f"Error: Video not found: {video_path}")
        sys.exit(1)
    
    transcripts = transcribe_video(video_path)
    
    print("\n" + "="*80)
    print("TRANSCRIPTION RESULTS")
    print("="*80 + "\n")
    
    for segment in transcripts:
        mins = int(segment['timestamp'] // 60)
        secs = int(segment['timestamp'] % 60)
        print(f"{mins:02d}:{secs:02d} - {segment['text']}")

