#!/usr/bin/env python3
"""
Video Processor
Process campaign videos and store fingerprints in JSON database (simulating blockchain).
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import hashlib

from audio_fingerprint import AudioFingerprinter


class VideoDatabase:
    """Manages video fingerprints database (simulates blockchain storage)."""
    
    def __init__(self, db_path: str = "video_database.json"):
        """
        Initialize database.
        
        Args:
            db_path: Path to JSON database file
        """
        self.db_path = Path(db_path)
        self.data = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load existing database or create new one."""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        else:
            return {'videos': []}
    
    def save(self):
        """Save database to file."""
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_video_id(self, video_path: str) -> str:
        """
        Generate unique ID for video based on file path and name.
        
        Args:
            video_path: Path to video file
        
        Returns:
            Unique video ID
        """
        video_name = Path(video_path).name
        hash_obj = hashlib.md5(video_name.encode())
        return f"video_{hash_obj.hexdigest()[:16]}"
    
    def video_exists(self, video_id: str) -> bool:
        """
        Check if video already exists in database.
        
        Args:
            video_id: Video ID to check
        
        Returns:
            True if video exists
        """
        for video in self.data['videos']:
            if video['id'] == video_id:
                return True
        return False
    
    def add_video(
        self,
        video_path: str,
        fingerprints: list,
        ipfs_cid: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add video fingerprints to database.
        
        Args:
            video_path: Path to video file
            fingerprints: List of fingerprint dictionaries
            ipfs_cid: Optional IPFS content identifier
            metadata: Optional additional metadata
        
        Returns:
            Video ID
        """
        video_id = self.generate_video_id(video_path)
        
        # Check if already exists
        if self.video_exists(video_id):
            raise ValueError(f"Video already exists in database: {video_id}")
        
        # Get video info
        fingerprinter = AudioFingerprinter(video_path)
        duration = fingerprinter.get_duration()
        
        # Generate mock IPFS CID if not provided
        if ipfs_cid is None:
            # In real implementation, this would be actual IPFS CID
            ipfs_cid = f"Qm{hashlib.sha256(Path(video_path).name.encode()).hexdigest()[:44]}"
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'upload_date': datetime.now().isoformat(),
            'filename': Path(video_path).name
        })
        
        # Create video entry
        video_entry = {
            'id': video_id,
            'ipfs_cid': ipfs_cid,
            'title': metadata.get('title', Path(video_path).stem),
            'duration': duration,
            'fingerprints': fingerprints,
            'metadata': metadata
        }
        
        # Add to database
        self.data['videos'].append(video_entry)
        self.save()
        
        print(f"Added video to database:")
        print(f"  ID: {video_id}")
        print(f"  IPFS CID: {ipfs_cid}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Fingerprints: {len(fingerprints)}")
        
        return video_id
    
    def get_video(self, video_id: str) -> Optional[Dict]:
        """
        Get video entry by ID.
        
        Args:
            video_id: Video ID
        
        Returns:
            Video entry or None if not found
        """
        for video in self.data['videos']:
            if video['id'] == video_id:
                return video
        return None
    
    def get_all_videos(self) -> list:
        """
        Get all videos in database.
        
        Returns:
            List of all video entries
        """
        return self.data['videos']
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with stats
        """
        total_videos = len(self.data['videos'])
        total_fingerprints = sum(
            len(video['fingerprints']) 
            for video in self.data['videos']
        )
        total_duration = sum(
            video['duration']
            for video in self.data['videos']
        )
        
        return {
            'total_videos': total_videos,
            'total_fingerprints': total_fingerprints,
            'total_duration': total_duration,
            'avg_fingerprints_per_video': (
                total_fingerprints / total_videos if total_videos > 0 else 0
            )
        }


def process_video(
    video_path: str,
    db_path: str = "video_database.json",
    title: Optional[str] = None,
    campaign: Optional[str] = None,
    ipfs_cid: Optional[str] = None
) -> str:
    """
    Process a video and add to database.
    
    Args:
        video_path: Path to video file
        db_path: Path to database file
        title: Optional video title
        campaign: Optional campaign name
        ipfs_cid: Optional IPFS CID
    
    Returns:
        Video ID
    """
    # Generate fingerprints
    print(f"\n{'='*60}")
    print(f"Processing Video: {Path(video_path).name}")
    print(f"{'='*60}\n")
    
    fingerprinter = AudioFingerprinter(video_path)
    fingerprints = fingerprinter.generate_fingerprints()
    
    # Prepare metadata
    metadata = {}
    if title:
        metadata['title'] = title
    if campaign:
        metadata['campaign'] = campaign
    
    # Add to database
    print(f"\n{'='*60}")
    print("Adding to Database")
    print(f"{'='*60}\n")
    
    db = VideoDatabase(db_path)
    video_id = db.add_video(video_path, fingerprints, ipfs_cid, metadata)
    
    return video_id


def main():
    """Command-line interface for video processing."""
    if len(sys.argv) < 2:
        print("Usage: python video_processor.py <video_file> [options]")
        print("\nOptions:")
        print("  --db <path>         Database file path (default: video_database.json)")
        print("  --title <title>     Video title")
        print("  --campaign <name>   Campaign name")
        print("  --ipfs <cid>        IPFS Content ID")
        print("  --stats             Show database statistics")
        print("  --list              List all videos in database")
        print("\nExamples:")
        print("  python video_processor.py video.mp4")
        print("  python video_processor.py video.mp4 --title \"Campaign Speech\" --campaign \"2024\"")
        print("  python video_processor.py --stats")
        print("  python video_processor.py --list")
        sys.exit(1)
    
    # Parse arguments
    video_path = None
    db_path = "video_database.json"
    title = None
    campaign = None
    ipfs_cid = None
    show_stats = False
    show_list = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--db' and i + 1 < len(sys.argv):
            db_path = sys.argv[i + 1]
            i += 2
        elif arg == '--title' and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
            i += 2
        elif arg == '--campaign' and i + 1 < len(sys.argv):
            campaign = sys.argv[i + 1]
            i += 2
        elif arg == '--ipfs' and i + 1 < len(sys.argv):
            ipfs_cid = sys.argv[i + 1]
            i += 2
        elif arg == '--stats':
            show_stats = True
            i += 1
        elif arg == '--list':
            show_list = True
            i += 1
        else:
            if video_path is None and not arg.startswith('--'):
                video_path = arg
            i += 1
    
    try:
        db = VideoDatabase(db_path)
        
        # Show stats
        if show_stats:
            stats = db.get_stats()
            print("\n" + "="*60)
            print("Database Statistics")
            print("="*60)
            print(f"Database file: {db_path}")
            print(f"Total videos: {stats['total_videos']}")
            print(f"Total fingerprints: {stats['total_fingerprints']}")
            print(f"Total duration: {stats['total_duration']:.2f}s ({stats['total_duration']/60:.2f} minutes)")
            print(f"Avg fingerprints/video: {stats['avg_fingerprints_per_video']:.1f}")
            return
        
        # List videos
        if show_list:
            videos = db.get_all_videos()
            print("\n" + "="*60)
            print(f"Videos in Database ({len(videos)} total)")
            print("="*60)
            for video in videos:
                print(f"\nID: {video['id']}")
                print(f"  Title: {video['title']}")
                print(f"  Duration: {video['duration']:.2f}s")
                print(f"  Fingerprints: {len(video['fingerprints'])}")
                print(f"  IPFS CID: {video['ipfs_cid']}")
                if 'campaign' in video['metadata']:
                    print(f"  Campaign: {video['metadata']['campaign']}")
            return
        
        # Process video
        if video_path is None:
            print("Error: No video file specified")
            sys.exit(1)
        
        if not Path(video_path).exists():
            print(f"Error: Video file not found: {video_path}")
            sys.exit(1)
        
        video_id = process_video(video_path, db_path, title, campaign, ipfs_cid)
        
        print(f"\n{'='*60}")
        print("SUCCESS!")
        print(f"{'='*60}")
        print(f"Video ID: {video_id}")
        print(f"Database: {db_path}")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

