#!/usr/bin/env python3
"""
Test ML-based embeddings to verify they can detect same content across different recordings.
"""

import sys
import json
from pathlib import Path
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase
import numpy as np


def test_cross_video_similarity():
    """Test similarity between different recordings of the same speech."""
    
    print("="*80)
    print("ML EMBEDDING CROSS-VIDEO SIMILARITY TEST")
    print("="*80)
    print("\nThis test checks if ML embeddings can detect the same speech")
    print("content across different recordings (different mics/cameras).\n")
    
    # Load database
    db_path = "video_database_ml.json"
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        print("Please run: python3.10 process_videos_ml.py")
        sys.exit(1)
    
    db = VideoDatabase(db_path)
    all_videos = db.get_all_videos()
    
    if len(all_videos) < 2:
        print("Error: Need at least 2 videos in database")
        sys.exit(1)
    
    print(f"Found {len(all_videos)} videos in database:\n")
    for i, video in enumerate(all_videos, 1):
        print(f"  {i}. {video['title']}")
        print(f"     Embeddings: {len(video['fingerprints'])}")
    
    print(f"\n{'='*80}")
    print("SIMILARITY ANALYSIS")
    print(f"{'='*80}\n")
    
    # Create embedder for similarity calculation
    embedder = AudioEmbedder()
    
    # Sample embeddings from each video (first 10 to keep it fast)
    sample_size = 10
    
    # Compare all pairs
    for i in range(len(all_videos)):
        for j in range(i + 1, len(all_videos)):
            video1 = all_videos[i]
            video2 = all_videos[j]
            
            print(f"{'─'*80}")
            print(f"Comparing: {video1['title']} vs {video2['title']}")
            print(f"{'─'*80}\n")
            
            embs1 = video1['fingerprints'][:sample_size]
            embs2 = video2['fingerprints'][:sample_size]
            
            # Calculate similarities
            similarities = []
            
            for idx, emb1 in enumerate(embs1):
                # Find best match in video2
                best_sim = 0.0
                best_idx = -1
                
                for idx2, emb2 in enumerate(embs2):
                    sim = embedder.calculate_similarity(emb1, emb2)
                    if sim > best_sim:
                        best_sim = sim
                        best_idx = idx2
                
                similarities.append(best_sim)
                
                t1 = emb1['timestamp']
                t2 = embs2[best_idx]['timestamp'] if best_idx >= 0 else 0
                
                print(f"  Video 1 [{int(t1//60):2d}:{int(t1%60):02d}] → "
                      f"Video 2 [{int(t2//60):2d}:{int(t2%60):02d}]: {best_sim:.2%}")
            
            # Calculate average
            avg_sim = np.mean(similarities)
            std_sim = np.std(similarities)
            max_sim = np.max(similarities)
            min_sim = np.min(similarities)
            
            print(f"\n  Statistics:")
            print(f"    Average:   {avg_sim:.2%}")
            print(f"    Std Dev:   {std_sim:.2%}")
            print(f"    Max:       {max_sim:.2%}")
            print(f"    Min:       {min_sim:.2%}")
            
            # Interpretation
            print(f"\n  Result: ", end="")
            if avg_sim >= 0.85:
                print(f"🎯 SAME CONTENT (High confidence)")
            elif avg_sim >= 0.75:
                print(f"✅ LIKELY SAME CONTENT")
            elif avg_sim >= 0.65:
                print(f"⚠️  POSSIBLY SIMILAR CONTENT")
            else:
                print(f"✗  DIFFERENT CONTENT")
            
            print()
    
    print(f"{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}\n")
    
    print("Expected results:")
    print("  • Same speech, different recordings: >75% similarity")
    print("  • Different speeches: <65% similarity")
    print("\nNote: This is much better than chromaprint's ~62% for all pairs!")
    print()


def test_clip_verification():
    """Test verifying a clip from one of the videos."""
    
    print("="*80)
    print("ML EMBEDDING CLIP VERIFICATION TEST")
    print("="*80)
    print("\nCreating a test clip and verifying it...\n")
    
    # Check if we have videos
    db_path = "video_database_ml.json"
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    db = VideoDatabase(db_path)
    all_videos = db.get_all_videos()
    
    if not all_videos:
        print("Error: No videos in database")
        sys.exit(1)
    
    # Get first video
    video = all_videos[0]
    
    # Determine video filename from title
    if "Speech #2" in video['title']:
        video_filename = "fedspeech2.mp4"
    elif "Speech #3" in video['title']:
        video_filename = "fedspeech3.mp4"
    else:
        video_filename = "fedspeech1.mp4"
    
    video_path = Path("download") / video_filename
    
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Create a test clip (20 seconds from 5:00 mark)
    clip_path = "test_ml_clip.mp4"
    
    print(f"Creating test clip from {video['title']}...")
    print(f"  Source: {video_path.name}")
    print(f"  Extracting: 5:00 - 5:20 (20 seconds)")
    
    import subprocess
    
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-ss', '5:00',
        '-t', '20',
        '-c', 'copy',
        '-y',
        clip_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Error creating clip: {result.stderr.decode()}")
        sys.exit(1)
    
    print(f"✓ Created {clip_path}\n")
    
    # Verify the clip
    print(f"{'='*80}")
    print("VERIFYING CLIP")
    print(f"{'='*80}\n")
    
    from verification_ml import MLVideoVerifier
    
    verifier = MLVideoVerifier(db_path)
    matches = verifier.verify_clip(clip_path, threshold=0.75)
    
    # Display results
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}\n")
    
    if matches:
        print(f"✅ VERIFICATION SUCCESSFUL!")
        print(f"Found {len(matches)} match(es):\n")
        for i, match in enumerate(matches, 1):
            print(f"Match #{i}:")
            print(match)
            print()
    else:
        print("❌ VERIFICATION FAILED - No matches found")
    
    # Cleanup
    if Path(clip_path).exists():
        Path(clip_path).unlink()
        print(f"\n✓ Cleaned up {clip_path}")
    
    print()


def main():
    """Run all tests."""
    if len(sys.argv) > 1 and sys.argv[1] == '--clip-test':
        test_clip_verification()
    else:
        test_cross_video_similarity()
        
        print("\nTo test clip verification, run:")
        print("  python3.10 test_ml_embeddings.py --clip-test")


if __name__ == "__main__":
    main()

