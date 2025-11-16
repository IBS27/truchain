#!/usr/bin/env python3
"""
Audio Fingerprinting Module
Extracts audio from video files and generates chromaprint fingerprints at 5-second intervals.
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import tempfile

try:
    import acoustid
    from pydub import AudioSegment
except ImportError as e:
    print(f"Error: Required library not installed: {e}")
    print("Please install required packages: pip install pyacoustid pydub")
    sys.exit(1)


class AudioFingerprinter:
    """Generate audio fingerprints from video files."""
    
    INTERVAL_SECONDS = 5  # Generate fingerprint every 5 seconds
    
    def __init__(self, video_path: str):
        """
        Initialize the fingerprinter with a video file.
        
        Args:
            video_path: Path to the video file
        """
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
    
    def extract_audio(self, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video using ffmpeg.
        
        Args:
            output_path: Optional output path for audio file. If None, creates temp file.
        
        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
        
        # Use ffmpeg to extract audio as WAV
        cmd = [
            'ffmpeg',
            '-i', str(self.video_path),
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM 16-bit
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-y',  # Overwrite output
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio: {e.stderr.decode()}")
    
    def get_duration(self) -> float:
        """
        Get video duration in seconds.
        
        Returns:
            Duration in seconds
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(self.video_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            raise RuntimeError(f"Failed to get video duration: {e}")
    
    def generate_all_fingerprints_at_once(self, audio_path: str, duration: float) -> List[Dict[str, any]]:
        """
        Generate all fingerprints for audio file using chunking.
        
        Args:
            audio_path: Path to audio file
            duration: Duration of audio in seconds
        
        Returns:
            List of fingerprint dictionaries with timestamp and hash
        """
        # Use fpcalc with chunking to process entire file at once
        # Note: fpcalc default length limit is 120s, so we must specify full duration
        # Don't use -ts flag as it outputs UNIX timestamps instead of file positions
        cmd = [
            'fpcalc',
            '-raw',
            '-length', str(int(duration) + 10),  # Add buffer to ensure we get everything
            '-chunk', str(self.INTERVAL_SECONDS),
            '-overlap',
            '-json',
            audio_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            
            # Parse JSON output - fpcalc outputs one JSON object per line for chunks
            import json as json_lib
            fingerprints = []
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        chunk_data = json_lib.loads(line)
                        
                        # Get timestamp and fingerprint from chunk
                        timestamp = chunk_data.get('timestamp', len(fingerprints) * self.INTERVAL_SECONDS)
                        fingerprint_array = chunk_data.get('fingerprint', [])
                        
                        # Store the actual fingerprint array for proper matching
                        # Also generate a hash for blockchain storage
                        fingerprint_str = ','.join(str(x) for x in fingerprint_array)
                        hash_obj = hashlib.sha256(fingerprint_str.encode())
                        fp_hash = hash_obj.hexdigest()[:64]  # 32 bytes = 64 hex chars
                        
                        fingerprints.append({
                            'timestamp': timestamp,
                            'hash': fp_hash,
                            'fingerprint': fingerprint_array  # Keep raw fingerprint for comparison
                        })
                    except json_lib.JSONDecodeError:
                        continue
            
            return fingerprints
            
        except subprocess.CalledProcessError as e:
            stderr_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode()
            raise RuntimeError(f"Failed to generate fingerprints: {stderr_msg}")
    
    def generate_fingerprints(self, cleanup_audio: bool = True) -> List[Dict[str, any]]:
        """
        Generate fingerprints for entire video at 5-second intervals.
        
        Args:
            cleanup_audio: If True, delete extracted audio file after processing
        
        Returns:
            List of fingerprint dictionaries with timestamp and hash
        """
        print(f"Processing video: {self.video_path.name}")
        
        # Get video duration
        duration = self.get_duration()
        print(f"Video duration: {duration:.2f} seconds")
        
        # Extract audio
        print("Extracting audio...")
        audio_path = self.extract_audio()
        
        try:
            # Generate fingerprints using chunking
            print(f"Generating fingerprints at {self.INTERVAL_SECONDS}-second intervals...")
            fingerprints = self.generate_all_fingerprints_at_once(audio_path, duration)
            
            print(f"Generated {len(fingerprints)} fingerprints")
            return fingerprints
            
        finally:
            # Cleanup
            if cleanup_audio and os.path.exists(audio_path):
                os.remove(audio_path)
    
    def to_blockchain_format(self, fingerprints: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Convert fingerprints to blockchain-ready format.
        
        Args:
            fingerprints: List of fingerprint dictionaries
        
        Returns:
            Dictionary in blockchain storage format
        """
        duration = self.get_duration()
        
        return {
            'video_file': self.video_path.name,
            'duration': duration,
            'interval_seconds': self.INTERVAL_SECONDS,
            'fingerprints': fingerprints,
            'total_fingerprints': len(fingerprints)
        }


def main():
    """Command-line interface for audio fingerprinting."""
    if len(sys.argv) < 2:
        print("Usage: python audio_fingerprint.py <video_file> [output_json]")
        print("\nGenerates audio fingerprints from video file.")
        print("\nExample:")
        print("  python audio_fingerprint.py video.mp4 fingerprints.json")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Generate fingerprints
        fingerprinter = AudioFingerprinter(video_path)
        fingerprints = fingerprinter.generate_fingerprints()
        
        # Convert to blockchain format
        result = fingerprinter.to_blockchain_format(fingerprints)
        
        # Output results
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nFingerprints saved to: {output_json}")
        else:
            print("\nFingerprints (first 3):")
            for fp in fingerprints[:3]:
                print(f"  Time {fp['timestamp']}s: {fp['hash'][:16]}...")
        
        print(f"\nSummary:")
        print(f"  Video: {result['video_file']}")
        print(f"  Duration: {result['duration']:.2f}s")
        print(f"  Total fingerprints: {result['total_fingerprints']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

