#!/usr/bin/env python3
"""
Process videos for hybrid verification system.
Generates both transcripts (for content matching) and audio embeddings (for speaker verification).
"""

import sys
import os
from pathlib import Path
from audio_transcription import AudioTranscriber
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase


def process_video_for_hybrid_system(
    video_path: str,
    title: str,
    description: str = "",
    database_path: str = "video_database_hybrid.json",
    openai_api_key: str = None
) -> bool:
    """
    Process a video for hybrid verification.
    
    Args:
        video_path: Path to video file
        title: Video title
        description: Video description
        database_path: Path to database
        openai_api_key: OpenAI API key
        
    Returns:
        True if successful
    """
    print("\n" + "="*80)
    print("PROCESSING VIDEO FOR HYBRID VERIFICATION")
    print("="*80)
    print(f"\nVideo: {video_path}")
    print(f"Title: {title}\n")
    
    if not Path(video_path).exists():
        print(f"Error: Video not found: {video_path}")
        return False
    
    # Initialize components
    transcriber = AudioTranscriber(api_key=openai_api_key)
    embedder = AudioEmbedder()
    db = VideoDatabase(database_path)
    
    # Use filename as IPFS CID for now (in production, upload to IPFS first)
    ipfs_cid = Path(video_path).name
    
    # Check if already processed
    existing_video = db.get_video(ipfs_cid)
    if existing_video:
        print(f"⚠️  Video already in database: {ipfs_cid}")
        print("   Skipping...\n")
        return True
    
    # STEP 1: Generate transcripts
    print("STEP 1: Generating Transcripts")
    print("-"*80)
    
    try:
        transcripts = transcriber.transcribe_video(video_path)
    except Exception as e:
        print(f"\n✗ Error generating transcripts: {e}")
        return False
    
    # STEP 2: Generate audio embeddings for speaker verification
    print("\nSTEP 2: Generating Audio Embeddings")
    print("-"*80)
    
    try:
        embeddings = embedder.generate_embeddings(video_path)
    except Exception as e:
        print(f"\n✗ Error generating embeddings: {e}")
        return False
    
    # STEP 3: Store in database
    print("\nSTEP 3: Storing in Database")
    print("-"*80)
    
    try:
        # Get duration from transcripts
        duration = transcripts[-1]['timestamp'] + transcripts[-1]['duration'] if transcripts else 0
        
        db.add_video(
            ipfs_cid=ipfs_cid,
            title=title,
            description=description,
            fingerprints=embeddings,  # Audio embeddings for speaker verification
            duration=duration,
            transcripts=transcripts  # NEW: Store transcripts for content matching
        )
        
        print(f"✓ Video stored successfully")
        print(f"  IPFS CID: {ipfs_cid}")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Transcripts: {len(transcripts)} segments")
        print(f"  Embeddings: {len(embeddings)} segments")
        
    except Exception as e:
        print(f"\n✗ Error storing in database: {e}")
        return False
    
    # Cleanup
    transcriber.cleanup_temp_files()
    embedder.cleanup_temp_files()
    
    print("\n" + "="*80)
    print("✓ PROCESSING COMPLETE")
    print("="*80 + "\n")
    
    return True


def process_all_videos_in_directory(
    directory: str = "download",
    database_path: str = "video_database_hybrid.json",
    openai_api_key: str = None
):
    """
    Process all videos in a directory.
    
    Args:
        directory: Directory containing videos
        database_path: Path to database
        openai_api_key: OpenAI API key
    """
    video_dir = Path(directory)
    
    if not video_dir.exists():
        print(f"Error: Directory not found: {directory}")
        return
    
    # Find all video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
    
    if not video_files:
        print(f"No video files found in {directory}")
        return
    
    print(f"\nFound {len(video_files)} video(s) to process:\n")
    for i, video in enumerate(video_files, 1):
        print(f"  {i}. {video.name}")
    
    print()
    
    # Process each video
    successful = 0
    failed = 0
    
    for video_path in video_files:
        # Generate title from filename
        title = video_path.stem.replace('_', ' ').title()
        
        success = process_video_for_hybrid_system(
            str(video_path),
            title=title,
            database_path=database_path,
            openai_api_key=openai_api_key
        )
        
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"\n  Total videos: {len(video_files)}")
    print(f"  ✓ Successful: {successful}")
    print(f"  ✗ Failed: {failed}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process videos for hybrid verification system")
    parser.add_argument("--video", help="Process a single video file")
    parser.add_argument("--title", help="Title for the video")
    parser.add_argument("--directory", default="download", help="Process all videos in directory")
    parser.add_argument("--database", default="video_database_hybrid.json", help="Database path")
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set it with:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    if args.video:
        # Process single video
        if not args.title:
            # Generate title from filename
            args.title = Path(args.video).stem.replace('_', ' ').title()
        
        success = process_video_for_hybrid_system(
            args.video,
            title=args.title,
            database_path=args.database,
            openai_api_key=api_key
        )
        
        sys.exit(0 if success else 1)
    else:
        # Process directory
        process_all_videos_in_directory(
            directory=args.directory,
            database_path=args.database,
            openai_api_key=api_key
        )


if __name__ == "__main__":
    main()

