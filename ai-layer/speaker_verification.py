#!/usr/bin/env python3
"""
Speaker Verification Module
Uses Wav2Vec2 embeddings to verify if the same person is speaking in both videos.

This is used AFTER content matching to prevent deepfakes and voiceovers.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Tuple, Dict
import numpy as np
import torch
import soundfile as sf
from transformers import Wav2Vec2Processor, Wav2Vec2Model


class SpeakerVerifier:
    """
    Verifies if the same speaker is in both video segments using Wav2Vec2 embeddings.
    Embeddings are generated ON-DEMAND (not cached) for the specific timestamps.
    """
    
    SAMPLE_RATE = 16000  # Wav2Vec2 expects 16kHz
    
    def __init__(self, model_name: str = "facebook/wav2vec2-base"):
        """
        Initialize speaker verifier with Wav2Vec2 model.
        
        Args:
            model_name: Hugging Face model name
        """
        print(f"Loading Wav2Vec2 model for speaker verification: {model_name}")
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2Model.from_pretrained(model_name)
        self.model.eval()
        
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"✓ Model loaded on device: {self.device}\n")
    
    def extract_audio_segment(
        self,
        video_path: str,
        start_time: float,
        duration: float
    ) -> str:
        """
        Extract audio segment from video at specific timestamp.
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            Path to extracted audio file
        """
        # Create temp directory
        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)
        
        # Create temp output file
        output_path = temp_dir / f"segment_{hash(f'{video_path}_{start_time}_{duration}')}_{os.getpid()}.wav"
        
        # Extract audio segment with ffmpeg
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-vn',  # No video
            '-acodec', 'pcm_s16le',
            '-ar', str(self.SAMPLE_RATE),
            '-ac', '1',  # Mono
            '-y',
            str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return str(output_path)
    
    def audio_to_embedding(self, audio_path: str) -> np.ndarray:
        """
        Convert audio file to speaker embedding vector using Wav2Vec2.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Normalized embedding vector
        """
        # Load audio
        waveform, sample_rate = sf.read(audio_path)
        
        # Resample if needed
        if sample_rate != self.SAMPLE_RATE:
            # Simple resampling (for production, use librosa.resample)
            import warnings
            warnings.warn(f"Audio sample rate {sample_rate} != {self.SAMPLE_RATE}, using as-is")
        
        # Convert to tensor
        waveform_tensor = torch.FloatTensor(waveform)
        
        # Generate embedding
        with torch.no_grad():
            inputs = self.processor(
                waveform,
                sampling_rate=self.SAMPLE_RATE,
                return_tensors="pt",
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            
            # Use mean pooling over time dimension
            embeddings = outputs.last_hidden_state.mean(dim=1)
            embedding = embeddings.cpu().numpy()[0]
            
            # L2 normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        return embedding
    
    def calculate_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Cosine similarity (embeddings are already normalized)
        similarity = np.dot(embedding1, embedding2)
        
        # Convert from [-1, 1] to [0, 1]
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def verify_speaker(
        self,
        clip_path: str,
        clip_start: float,
        clip_duration: float,
        original_path: str,
        original_start: float,
        original_duration: float,
        threshold: float = 0.85
    ) -> Dict:
        """
        Verify if the same speaker is in both video segments.
        
        This extracts audio segments at the specified timestamps and compares
        their speaker embeddings.
        
        Args:
            clip_path: Path to user's clip
            clip_start: Start time in clip (usually 0)
            clip_duration: Duration to analyze from clip
            original_path: Path to original video
            original_start: Start time in original (from content matching)
            original_duration: Duration to analyze from original
            threshold: Minimum similarity to consider same speaker (0.85 = 85%)
            
        Returns:
            {
                'verified': bool,
                'similarity': float,
                'threshold': float,
                'clip_embedding_dim': int,
                'original_embedding_dim': int
            }
        """
        print(f"\n{'='*70}")
        print("SPEAKER VERIFICATION")
        print(f"{'='*70}\n")
        
        print(f"Clip: {Path(clip_path).name}")
        print(f"  Analyzing: {clip_start:.1f}s for {clip_duration:.1f}s")
        print(f"\nOriginal: {Path(original_path).name}")
        print(f"  Analyzing: {original_start:.1f}s for {original_duration:.1f}s")
        print(f"\nThreshold: {threshold:.1%}\n")
        
        clip_audio_path = None
        original_audio_path = None
        
        try:
            # Extract audio segments
            print("Step 1: Extracting audio segments...")
            clip_audio_path = self.extract_audio_segment(
                clip_path,
                clip_start,
                clip_duration
            )
            print(f"  ✓ Extracted clip audio")
            
            original_audio_path = self.extract_audio_segment(
                original_path,
                original_start,
                original_duration
            )
            print(f"  ✓ Extracted original audio")
            
            # Generate embeddings
            print("\nStep 2: Generating speaker embeddings...")
            clip_embedding = self.audio_to_embedding(clip_audio_path)
            print(f"  ✓ Clip embedding: {len(clip_embedding)} dimensions")
            
            original_embedding = self.audio_to_embedding(original_audio_path)
            print(f"  ✓ Original embedding: {len(original_embedding)} dimensions")
            
            # Calculate similarity
            print("\nStep 3: Comparing embeddings...")
            similarity = self.calculate_similarity(clip_embedding, original_embedding)
            
            verified = similarity >= threshold
            
            print(f"\n{'─'*70}")
            print(f"Similarity: {similarity:.2%}")
            print(f"Threshold:  {threshold:.2%}")
            print(f"{'─'*70}")
            
            if verified:
                print(f"✓ VERIFIED: Same speaker (similarity: {similarity:.2%})")
            else:
                print(f"✗ NOT VERIFIED: Different speaker (similarity: {similarity:.2%})")
                print(f"  Possible deepfake or voiceover!")
            
            print()
            
            return {
                'verified': verified,
                'similarity': similarity,
                'threshold': threshold,
                'clip_embedding_dim': len(clip_embedding),
                'original_embedding_dim': len(original_embedding),
                'message': 'Same speaker' if verified else 'Different speaker - possible deepfake'
            }
            
        finally:
            # Cleanup temp files
            if clip_audio_path and os.path.exists(clip_audio_path):
                os.remove(clip_audio_path)
            if original_audio_path and os.path.exists(original_audio_path):
                os.remove(original_audio_path)


def main():
    """Test speaker verification with example segments."""
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python speaker_verification.py <clip> <clip_start> <original> <original_start>")
        print("\nExample:")
        print("  python speaker_verification.py \\")
        print("    test_clip.mp4 0 \\")
        print("    download/fedspeech1.mp4 120")
        print("\nThis extracts 10 seconds from each video starting at the given times")
        print("and verifies if the same speaker is in both segments.")
        sys.exit(1)
    
    clip_path = sys.argv[1]
    clip_start = float(sys.argv[2])
    original_path = sys.argv[3]
    original_start = float(sys.argv[4])
    
    # Default: analyze 10 seconds from each
    duration = 10.0
    
    if not Path(clip_path).exists():
        print(f"Error: Clip not found: {clip_path}")
        sys.exit(1)
    
    if not Path(original_path).exists():
        print(f"Error: Original not found: {original_path}")
        sys.exit(1)
    
    # Verify speaker
    verifier = SpeakerVerifier()
    result = verifier.verify_speaker(
        clip_path=clip_path,
        clip_start=clip_start,
        clip_duration=duration,
        original_path=original_path,
        original_start=original_start,
        original_duration=duration,
        threshold=0.85
    )
    
    # Exit code
    sys.exit(0 if result['verified'] else 1)


if __name__ == "__main__":
    main()

