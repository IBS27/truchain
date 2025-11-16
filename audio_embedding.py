#!/usr/bin/env python3
"""
Audio Embedding Module using Wav2Vec 2.0

PURPOSE: SPEAKER VERIFICATION (not content matching)
- Verifies that the same PERSON is speaking in both videos
- Prevents deepfakes, voiceovers, and impersonations
- Should be used AFTER content matching to verify authenticity

WARNING: This module detects voice/speaker characteristics, not semantic content.
For content matching, use text_matching.py instead.
"""

import os
import sys
import numpy as np
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from pathlib import Path
from typing import List, Dict, Tuple
import tempfile
import subprocess
import hashlib
import json

class AudioEmbedder:
    """Generate content-based audio embeddings using Wav2Vec 2.0."""
    
    INTERVAL_SECONDS = 5  # Generate embedding every 5 seconds
    SAMPLE_RATE = 16000   # Wav2Vec2 expects 16kHz
    
    def __init__(self, model_name: str = "facebook/wav2vec2-base"):
        """
        Initialize the embedder with a pre-trained model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        print(f"Loading Wav2Vec2 model: {model_name}")
        print("(This will download ~300MB on first run)")
        
        # Load processor and model
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2Model.from_pretrained(model_name)
        
        # Set to evaluation mode
        self.model.eval()
        
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        print(f"✓ Model loaded on device: {self.device}")
    
    def extract_audio_normalized(self, video_path: str) -> str:
        """
        Extract and normalize audio from video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        # Use local temp directory instead of system /tmp
        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)
        
        temp_fd, output_path = tempfile.mkstemp(suffix='.wav', dir=str(temp_dir))
        os.close(temp_fd)
        
        # Extract audio with normalization for robustness
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',
            '-ar', str(self.SAMPLE_RATE),  # 16kHz for Wav2Vec2
            '-ac', '1',  # Mono
            '-af', 'highpass=f=200,lowpass=f=3000,dynaudnorm',  # Normalize
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    def get_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    
    def audio_to_embedding(self, waveform: torch.Tensor) -> np.ndarray:
        """
        Convert audio waveform to embedding vector.
        
        Args:
            waveform: Audio tensor [1, samples]
            
        Returns:
            Embedding vector as numpy array
        """
        with torch.no_grad():
            # Process audio
            inputs = self.processor(
                waveform.squeeze().numpy(),
                sampling_rate=self.SAMPLE_RATE,
                return_tensors="pt",
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings
            outputs = self.model(**inputs)
            
            # Use mean pooling over time dimension
            # Shape: [batch, time, features] -> [batch, features]
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # Convert to numpy and normalize
            embedding = embeddings.cpu().numpy()[0]
            
            # L2 normalize for cosine similarity
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            
            return embedding
    
    def generate_embeddings(self, video_path: str) -> List[Dict]:
        """
        Generate embeddings for entire video at regular intervals.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of embedding dictionaries
        """
        print(f"\nProcessing video: {Path(video_path).name}")
        
        # Get duration
        duration = self.get_duration(video_path)
        print(f"Duration: {duration:.2f}s")
        
        # Extract audio
        print("Extracting and normalizing audio...")
        audio_path = self.extract_audio_normalized(video_path)
        
        try:
            # Load audio using soundfile backend (more compatible)
            import soundfile as sf
            
            # Read audio file
            data, sample_rate = sf.read(audio_path)
            
            # Convert to torch tensor
            waveform = torch.from_numpy(data).float()
            
            # Add batch dimension if needed
            if waveform.ndim == 1:
                waveform = waveform.unsqueeze(0)
            else:
                # Transpose if (samples, channels) -> (channels, samples)
                waveform = waveform.transpose(0, 1)
            
            # Resample if needed
            if sample_rate != self.SAMPLE_RATE:
                resampler = torchaudio.transforms.Resample(sample_rate, self.SAMPLE_RATE)
                waveform = resampler(waveform)
            
            # Convert to mono if needed
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Generate embeddings at intervals
            embeddings = []
            samples_per_chunk = self.SAMPLE_RATE * self.INTERVAL_SECONDS
            total_samples = waveform.shape[1]
            
            print(f"Generating embeddings at {self.INTERVAL_SECONDS}s intervals...")
            
            for start_sample in range(0, total_samples, samples_per_chunk):
                timestamp = start_sample / self.SAMPLE_RATE
                end_sample = min(start_sample + samples_per_chunk, total_samples)
                
                # Extract chunk
                chunk = waveform[:, start_sample:end_sample]
                
                # Skip if chunk too short
                if chunk.shape[1] < self.SAMPLE_RATE:  # At least 1 second
                    break
                
                # Generate embedding
                embedding = self.audio_to_embedding(chunk)
                
                # Create hash for blockchain storage
                embedding_bytes = embedding.tobytes()
                hash_obj = hashlib.sha256(embedding_bytes)
                embedding_hash = hash_obj.hexdigest()[:64]
                
                embeddings.append({
                    'timestamp': timestamp,
                    'embedding': embedding.tolist(),  # Convert to list for JSON
                    'hash': embedding_hash,
                    'embedding_dim': len(embedding)
                })
                
                if len(embeddings) % 50 == 0:
                    print(f"  Generated {len(embeddings)} embeddings...")
            
            print(f"✓ Generated {len(embeddings)} embeddings")
            return embeddings
            
        finally:
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)
    
    def calculate_similarity(self, emb1: Dict, emb2: Dict) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding dict
            emb2: Second embedding dict
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        vec1 = np.array(emb1['embedding'])
        vec2 = np.array(emb2['embedding'])
        
        # Cosine similarity (already normalized, so just dot product)
        similarity = np.dot(vec1, vec2)
        
        # Convert from [-1, 1] to [0, 1]
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def cleanup_temp_files(self):
        """Remove temporary audio files."""
        temp_dir = Path("temp_audio")
        if temp_dir.exists():
            for file in temp_dir.glob("*.wav"):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Warning: Could not delete {file}: {e}")


def main():
    """Test the embedding system."""
    if len(sys.argv) < 2:
        print("Usage: python3.10 audio_embedding.py <video_file> [output_json]")
        print("\nGenerates ML-based audio embeddings from video file.")
        print("These embeddings are robust to different recording conditions.\n")
        print("Examples:")
        print("  python3.10 audio_embedding.py video.mp4")
        print("  python3.10 audio_embedding.py video.mp4 embeddings.json")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Create embedder
        embedder = AudioEmbedder()
        
        # Generate embeddings
        embeddings = embedder.generate_embeddings(video_path)
        
        # Save if requested
        if output_json:
            with open(output_json, 'w') as f:
                json.dump({
                    'video': Path(video_path).name,
                    'embeddings': embeddings,
                    'model': 'wav2vec2-base',
                    'interval_seconds': embedder.INTERVAL_SECONDS
                }, f, indent=2)
            print(f"\n✓ Saved to {output_json}")
        else:
            # Show preview
            print(f"\nFirst embedding preview:")
            print(f"  Timestamp: {embeddings[0]['timestamp']}s")
            print(f"  Dimension: {embeddings[0]['embedding_dim']}")
            print(f"  Hash: {embeddings[0]['hash'][:32]}...")
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Video: {Path(video_path).name}")
        print(f"  Duration: {embedder.get_duration(video_path):.2f}s")
        print(f"  Embeddings: {len(embeddings)}")
        print(f"  Embedding dimension: {embeddings[0]['embedding_dim']}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

