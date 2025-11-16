#!/usr/bin/env python3
"""
Process videos and store ML-based embeddings in database.
"""

import sys
import uuid
from pathlib import Path
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase


def process_video(video_path: str, title: str, embedder: AudioEmbedder, db: VideoDatabase):
    """
    Process a video and add it to the ML database.
    
    Args:
        video_path: Path to video file
        title: Title for the video
        embedder: AudioEmbedder instance
        db: VideoDatabase instance
    """
    print(f"\n{'='*70}")
    print(f"Processing: {title}")
    print(f"{'='*70}")
    
    # Generate embeddings
    embeddings = embedder.generate_embeddings(video_path)
    
    # Get duration
    duration = embedder.get_duration(video_path)
    
    # Add to database using proper signature
    metadata = {
        'title': title,
        'embedding_model': 'wav2vec2-base',
        'interval_seconds': embedder.INTERVAL_SECONDS
    }
    
    video_id = db.add_video(
        video_path=video_path,
        fingerprints=embeddings,  # ML embeddings stored as fingerprints
        ipfs_cid='placeholder_cid',
        metadata=metadata
    )
    
    print(f"\n✓ Added to database:")
    print(f"  ID: {video_id}")
    print(f"  Title: {title}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Embeddings: {len(embeddings)}")


def main():
    """Process all videos in download directory."""
    if len(sys.argv) > 1:
        # Process specific video
        video_path = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else Path(video_path).stem
        
        if not Path(video_path).exists():
            print(f"Error: Video not found: {video_path}")
            sys.exit(1)
        
        videos = [(video_path, title)]
    else:
        # Process all videos in download directory
        download_dir = Path("download")
        
        if not download_dir.exists():
            print("Error: download/ directory not found")
            sys.exit(1)
        
        video_files = sorted(download_dir.glob("*.mp4"))
        
        if not video_files:
            print("Error: No video files found in download/ directory")
            sys.exit(1)
        
        # Create titles from filenames
        videos = []
        for video_file in video_files:
            # Extract meaningful title from filename
            name = video_file.stem
            if 'fedspeech1' in name.lower():
                title = "Federal Reserve Chair Speech"
            elif 'fedspeech2' in name.lower():
                title = "Federal Reserve Speech #2"
            elif 'fedspeech3' in name.lower():
                title = "Federal Reserve Speech #3"
            else:
                title = name.replace('_', ' ').title()
            
            videos.append((str(video_file), title))
    
    print(f"{'='*70}")
    print(f"ML-Based Video Processing")
    print(f"{'='*70}")
    print(f"\nFound {len(videos)} video(s) to process:\n")
    for path, title in videos:
        print(f"  • {title} ({Path(path).name})")
    
    # Initialize
    print(f"\n{'='*70}")
    print("Initializing ML model...")
    print(f"{'='*70}")
    
    embedder = AudioEmbedder()
    db = VideoDatabase("video_database_ml.json")
    
    # Process each video
    for video_path, title in videos:
        try:
            process_video(video_path, title, embedder, db)
        except Exception as e:
            print(f"\n✗ Error processing {title}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Summary
    all_videos = db.get_all_videos()
    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"\nDatabase: video_database_ml.json")
    print(f"Total videos: {len(all_videos)}\n")
    
    for video in all_videos:
        print(f"  • {video['title']}")
        print(f"    Duration: {video['duration']:.2f}s")
        print(f"    Embeddings: {len(video['fingerprints'])}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()

