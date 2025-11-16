#!/usr/bin/env python3
"""
Show detailed timestamp matches between the NEW video and existing videos.
This helps verify if the same content appears at specific times.
"""

import sys
from pathlib import Path
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase
import numpy as np


def format_time(seconds):
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:2d}:{secs:02d}"


def main():
    print("="*80)
    print("DETAILED TIMESTAMP MATCHING ANALYSIS")
    print("="*80)
    print("\nShowing WHERE in each video the matching segments were found.\n")
    
    # Load database
    db_path = "video_database_ml.json"
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    db = VideoDatabase(db_path)
    all_videos = db.get_all_videos()
    
    # Identify the new video
    new_video = None
    old_videos = []
    
    for video in all_videos:
        if "Different" in video['title']:
            new_video = video
        else:
            old_videos.append(video)
    
    if not new_video:
        print("Error: Could not find 'Different' video")
        sys.exit(1)
    
    print(f"Analyzing: {new_video['title']}")
    print(f"Duration: {format_time(new_video['duration'])}")
    print(f"Total embeddings: {len(new_video['fingerprints'])}\n")
    
    # Create embedder
    embedder = AudioEmbedder()
    
    # For each old video, show detailed matches
    for old_video in old_videos:
        print(f"{'='*80}")
        print(f"Comparing against: {old_video['title']}")
        print(f"Duration: {format_time(old_video['duration'])}")
        print(f"{'='*80}\n")
        
        # Sample every 30 seconds from the new video (more detailed than before)
        sample_interval = 30  # seconds
        num_samples = min(20, int(new_video['duration'] / sample_interval))
        
        # Get evenly spaced samples across the entire video
        sample_indices = np.linspace(0, len(new_video['fingerprints'])-1, num_samples, dtype=int)
        
        matches = []
        
        for idx in sample_indices:
            new_emb = new_video['fingerprints'][idx]
            new_timestamp = new_emb['timestamp']
            
            # Find best match in old video
            best_sim = 0
            best_old_timestamp = 0
            
            for old_emb in old_video['fingerprints']:
                sim = embedder.calculate_similarity(new_emb, old_emb)
                if sim > best_sim:
                    best_sim = sim
                    best_old_timestamp = old_emb['timestamp']
            
            matches.append({
                'new_time': new_timestamp,
                'old_time': best_old_timestamp,
                'similarity': best_sim
            })
        
        # Sort by similarity for top matches
        top_matches = sorted(matches, key=lambda x: x['similarity'], reverse=True)
        
        print(f"Top 10 Matching Segments:\n")
        print(f"  {'NEW Video':<15} {'→':<3} {'OLD Video':<15} {'Similarity':>12}")
        print(f"  {'-'*15} {'-'*3} {'-'*15} {'-'*12}")
        
        for i, match in enumerate(top_matches[:10], 1):
            new_time_str = format_time(match['new_time'])
            old_time_str = format_time(match['old_time'])
            sim_str = f"{match['similarity']:.1%}"
            
            # Color code by similarity
            if match['similarity'] >= 0.95:
                icon = "🎯"
            elif match['similarity'] >= 0.85:
                icon = "✅"
            elif match['similarity'] >= 0.75:
                icon = "⚠️ "
            else:
                icon = "  "
            
            print(f"{i:2d}. {new_time_str:<15} → {old_time_str:<15} {sim_str:>12} {icon}")
        
        # Statistics
        avg_sim = np.mean([m['similarity'] for m in matches])
        max_sim = max([m['similarity'] for m in matches])
        
        print(f"\n  Average similarity across all samples: {avg_sim:.1%}")
        print(f"  Maximum similarity found: {max_sim:.1%}")
        
        # Check if there's a pattern in timestamps (offset)
        high_matches = [m for m in matches if m['similarity'] >= 0.90]
        if len(high_matches) >= 3:
            offsets = [m['old_time'] - m['new_time'] for m in high_matches]
            avg_offset = np.mean(offsets)
            offset_std = np.std(offsets)
            
            print(f"\n  🔍 Pattern Analysis:")
            print(f"     Found {len(high_matches)} high-confidence matches (>90%)")
            
            if offset_std < 10:  # Consistent offset
                print(f"     Average time offset: {avg_offset:+.1f} seconds")
                print(f"     → Videos likely START at different times but contain same content")
            else:
                print(f"     Time offsets vary significantly (std: {offset_std:.1f}s)")
                print(f"     → Content might be rearranged or from different parts of speech")
        
        print()
    
    # Summary
    print(f"{'='*80}")
    print("INTERPRETATION GUIDE")
    print(f"{'='*80}\n")
    
    print("How to use these timestamps:\n")
    print("1. Pick a high-confidence match (🎯 >95% or ✅ >85%)")
    print("2. Watch the NEW video at that timestamp")
    print("3. Watch the OLD video at the corresponding timestamp")
    print("4. Compare - are they saying the same thing?\n")
    
    print("Similarity levels:")
    print("  🎯 95-100%: Almost certainly the same speech segment")
    print("  ✅ 85-95%:  Very likely the same speech, different recording")
    print("  ⚠️  75-85%:  Possibly same speech or similar topic")
    print("     <75%:    Likely different content\n")
    
    print("Example verification command:")
    print(f"  # Watch NEW video at a matching timestamp (e.g., 5:00)")
    print(f"  ffplay -ss 5:00 download/fedspeechdifferent.mp4")
    print(f"  # Watch OLD video at corresponding timestamp (e.g., 7:30)")
    print(f"  ffplay -ss 7:30 download/fedspeech1.mp4")
    print()


if __name__ == "__main__":
    main()


