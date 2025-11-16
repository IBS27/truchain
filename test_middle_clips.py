#!/usr/bin/env python3
"""
Test ML embeddings by comparing 10-second clips from the middle of each video.
"""

import sys
import subprocess
from pathlib import Path
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase
import numpy as np


def create_middle_clip(video_path: str, duration: float, clip_duration: int = 10) -> str:
    """
    Create a clip from the middle of a video.
    
    Args:
        video_path: Path to video file
        duration: Total duration of video in seconds
        clip_duration: Length of clip to extract in seconds
        
    Returns:
        Path to created clip
    """
    # Calculate middle point
    middle_point = duration / 2
    
    # Create output filename
    video_name = Path(video_path).stem
    output_path = f"middle_clip_{video_name}.mp4"
    
    print(f"  Extracting {clip_duration}s from middle ({int(middle_point//60)}:{int(middle_point%60):02d})...")
    
    # Extract clip
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(middle_point),
        '-t', str(clip_duration),
        '-c', 'copy',
        '-y',
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def main():
    print("="*80)
    print("ML EMBEDDING - MIDDLE CLIP COMPARISON TEST")
    print("="*80)
    print("\nThis test extracts 10-second clips from the MIDDLE of each video")
    print("and compares them to see if they're the same speech content.\n")
    
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
        duration_min = int(all_videos[i-1]['duration'] // 60)
        duration_sec = int(all_videos[i-1]['duration'] % 60)
        print(f"  {i}. {video['title']}")
        print(f"     Duration: {duration_min}:{duration_sec:02d}")
    
    # Determine video filenames
    video_files = []
    for video in all_videos:
        if "Speech #2" in video['title']:
            filename = "fedspeech2.mp4"
        elif "Speech #3" in video['title']:
            filename = "fedspeech3.mp4"
        else:
            filename = "fedspeech1.mp4"
        
        video_path = Path("download") / filename
        if not video_path.exists():
            print(f"Error: Video file not found: {video_path}")
            sys.exit(1)
        
        video_files.append((str(video_path), video))
    
    print(f"\n{'='*80}")
    print("STEP 1: EXTRACTING MIDDLE CLIPS")
    print(f"{'='*80}\n")
    
    # Create middle clips
    clips = []
    for video_path, video_info in video_files:
        print(f"Processing: {video_info['title']}")
        clip_path = create_middle_clip(video_path, video_info['duration'])
        clips.append((clip_path, video_info['title']))
        print(f"  ✓ Created: {clip_path}\n")
    
    print(f"{'='*80}")
    print("STEP 2: GENERATING EMBEDDINGS FOR CLIPS")
    print(f"{'='*80}\n")
    
    # Initialize embedder
    embedder = AudioEmbedder()
    
    # Generate embeddings for each clip
    clip_embeddings = []
    for clip_path, title in clips:
        print(f"Processing clip: {title}")
        embeddings = embedder.generate_embeddings(clip_path)
        clip_embeddings.append((embeddings, title))
        print()
    
    print(f"{'='*80}")
    print("STEP 3: COMPARING CLIPS")
    print(f"{'='*80}\n")
    
    # Compare all pairs
    results = []
    
    for i in range(len(clip_embeddings)):
        for j in range(i + 1, len(clip_embeddings)):
            embs1, title1 = clip_embeddings[i]
            embs2, title2 = clip_embeddings[j]
            
            print(f"{'─'*80}")
            print(f"Comparing: {title1} vs {title2}")
            print(f"{'─'*80}\n")
            
            # Calculate similarities for all embedding pairs
            all_similarities = []
            
            for emb1 in embs1:
                for emb2 in embs2:
                    sim = embedder.calculate_similarity(emb1, emb2)
                    all_similarities.append(sim)
            
            # Statistics
            avg_sim = np.mean(all_similarities)
            max_sim = np.max(all_similarities)
            min_sim = np.min(all_similarities)
            std_sim = np.std(all_similarities)
            
            # Show best matches
            sorted_sims = sorted(all_similarities, reverse=True)
            top_5 = sorted_sims[:5]
            
            print(f"  Top 5 similarities:")
            for idx, sim in enumerate(top_5, 1):
                print(f"    {idx}. {sim:.2%}")
            
            print(f"\n  Statistics:")
            print(f"    Average:   {avg_sim:.2%}")
            print(f"    Max:       {max_sim:.2%}")
            print(f"    Min:       {min_sim:.2%}")
            print(f"    Std Dev:   {std_sim:.2%}")
            
            # Interpretation
            print(f"\n  Result: ", end="")
            if avg_sim >= 0.85:
                result = "🎯 SAME CONTENT (High confidence)"
                status = "SAME"
            elif avg_sim >= 0.75:
                result = "✅ SAME CONTENT (Good confidence)"
                status = "SAME"
            elif avg_sim >= 0.65:
                result = "⚠️  POSSIBLY SIMILAR CONTENT"
                status = "SIMILAR"
            else:
                result = "✗  DIFFERENT CONTENT"
                status = "DIFFERENT"
            
            print(result)
            print()
            
            results.append({
                'pair': f"{title1} vs {title2}",
                'avg_sim': avg_sim,
                'max_sim': max_sim,
                'status': status
            })
    
    # Summary
    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    print("Middle Clip Comparison Results:\n")
    for result in results:
        status_icon = "✅" if result['status'] == "SAME" else "⚠️" if result['status'] == "SIMILAR" else "✗"
        print(f"{status_icon} {result['pair']}")
        print(f"   Average: {result['avg_sim']:.2%} | Max: {result['max_sim']:.2%} | Status: {result['status']}")
        print()
    
    # Cleanup
    print(f"{'='*80}")
    print("CLEANUP")
    print(f"{'='*80}\n")
    
    for clip_path, _ in clips:
        if Path(clip_path).exists():
            Path(clip_path).unlink()
            print(f"✓ Removed {clip_path}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}\n")
    
    print("Interpretation:")
    print("  • Average >85% = Same content, high confidence")
    print("  • Average 75-85% = Same content, good confidence")
    print("  • Average 65-75% = Possibly similar")
    print("  • Average <65% = Different content")
    print()


if __name__ == "__main__":
    main()

