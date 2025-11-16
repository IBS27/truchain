#!/usr/bin/env python3
"""
Compare ENTIRE videos against each other to see overall similarity patterns.
This shows what happens when comparing every single 5-second segment.
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


def compare_full_videos(video1, video2, embedder):
    """
    Compare every segment of video1 against every segment of video2.
    Returns statistics about the full comparison.
    """
    
    print(f"\n{'='*80}")
    print(f"Comparing: {video1['title']}")
    print(f"   vs")
    print(f"          {video2['title']}")
    print(f"{'='*80}\n")
    
    print(f"Video 1: {len(video1['fingerprints'])} segments ({format_time(video1['duration'])})")
    print(f"Video 2: {len(video2['fingerprints'])} segments ({format_time(video2['duration'])})\n")
    
    # For each segment in video1, find its best match in video2
    matches = []
    
    total_segments = len(video1['fingerprints'])
    print(f"Comparing {total_segments} segments from Video 1 against all segments in Video 2...")
    print("(This may take a minute...)\n")
    
    for i, emb1 in enumerate(video1['fingerprints']):
        if i % 50 == 0:
            print(f"  Processing segment {i}/{total_segments}...")
        
        best_sim = 0
        best_match_time = 0
        
        # Find best match in video2
        for emb2 in video2['fingerprints']:
            sim = embedder.calculate_similarity(emb1, emb2)
            if sim > best_sim:
                best_sim = sim
                best_match_time = emb2['timestamp']
        
        matches.append({
            'video1_time': emb1['timestamp'],
            'video2_time': best_match_time,
            'similarity': best_sim
        })
    
    print(f"  Completed!\n")
    
    # Calculate statistics
    similarities = [m['similarity'] for m in matches]
    avg_sim = np.mean(similarities)
    median_sim = np.median(similarities)
    max_sim = np.max(similarities)
    min_sim = np.min(similarities)
    
    # Count segments by similarity level
    excellent = sum(1 for s in similarities if s >= 0.95)
    very_good = sum(1 for s in similarities if 0.85 <= s < 0.95)
    good = sum(1 for s in similarities if 0.75 <= s < 0.85)
    moderate = sum(1 for s in similarities if 0.65 <= s < 0.75)
    low = sum(1 for s in similarities if s < 0.65)
    
    # Results
    print(f"{'─'*80}")
    print(f"OVERALL SIMILARITY STATISTICS")
    print(f"{'─'*80}\n")
    
    print(f"  Average similarity:  {avg_sim:.1%}")
    print(f"  Median similarity:   {median_sim:.1%}")
    print(f"  Maximum similarity:  {max_sim:.1%}")
    print(f"  Minimum similarity:  {min_sim:.1%}\n")
    
    print(f"{'─'*80}")
    print(f"SEGMENT BREAKDOWN")
    print(f"{'─'*80}\n")
    
    total = len(similarities)
    print(f"  🎯 Excellent (95-100%): {excellent:4d} segments ({excellent/total*100:5.1f}%)")
    print(f"  ✅ Very Good (85-95%):  {very_good:4d} segments ({very_good/total*100:5.1f}%)")
    print(f"  ⚠️  Good (75-85%):      {good:4d} segments ({good/total*100:5.1f}%)")
    print(f"  ⚡ Moderate (65-75%):   {moderate:4d} segments ({moderate/total*100:5.1f}%)")
    print(f"  ❌ Low (<65%):          {low:4d} segments ({low/total*100:5.1f}%)\n")
    
    # Timeline visualization
    print(f"{'─'*80}")
    print(f"TIMELINE VISUALIZATION")
    print(f"{'─'*80}\n")
    
    print("Each character = ~30 seconds of Video 1:")
    print("🎯=95%+  ✅=85-95%  ⚠️=75-85%  ⚡=65-75%  ❌=<65%\n")
    
    # Group into 30-second chunks for visualization
    chunk_size = 6  # 6 segments = 30 seconds
    timeline = []
    
    for i in range(0, len(matches), chunk_size):
        chunk_matches = matches[i:i+chunk_size]
        avg_chunk_sim = np.mean([m['similarity'] for m in chunk_matches])
        
        if avg_chunk_sim >= 0.95:
            timeline.append('🎯')
        elif avg_chunk_sim >= 0.85:
            timeline.append('✅')
        elif avg_chunk_sim >= 0.75:
            timeline.append('⚠️ ')
        elif avg_chunk_sim >= 0.65:
            timeline.append('⚡')
        else:
            timeline.append('❌')
    
    # Print timeline in rows of 40 chars
    chars_per_row = 40
    for i in range(0, len(timeline), chars_per_row):
        row_start_time = format_time(i * 30)
        row = ''.join(timeline[i:i+chars_per_row])
        print(f"  {row_start_time:>6} │ {row}")
    
    print()
    
    # Check for patterns
    print(f"{'─'*80}")
    print(f"PATTERN ANALYSIS")
    print(f"{'─'*80}\n")
    
    high_matches = [m for m in matches if m['similarity'] >= 0.90]
    
    if len(high_matches) > total * 0.8:
        print(f"  ✅ {len(high_matches)} / {total} segments are high-confidence matches (>90%)")
        print(f"  → These videos contain the SAME SPEECH CONTENT\n")
        
        # Check time offset
        offsets = [m['video2_time'] - m['video1_time'] for m in high_matches[:100]]  # Sample
        avg_offset = np.mean(offsets)
        offset_std = np.std(offsets)
        
        if offset_std < 10:
            print(f"  ⏱️  Consistent time offset: {avg_offset:+.1f} seconds")
            print(f"  → Videos are SYNCHRONIZED (same edit, different recordings)\n")
        else:
            print(f"  🔀 Time offsets vary widely (std: {offset_std/60:.1f} minutes)")
            print(f"  → Videos are REARRANGED (same content, different editing)\n")
    
    elif len(high_matches) > total * 0.3:
        print(f"  ⚠️  {len(high_matches)} / {total} segments match well (>90%)")
        print(f"  → Videos contain SOME OVERLAPPING CONTENT\n")
    
    else:
        print(f"  ❌ Only {len(high_matches)} / {total} segments match well (>90%)")
        print(f"  → Videos contain DIFFERENT CONTENT\n")
    
    return {
        'avg_similarity': avg_sim,
        'median_similarity': median_sim,
        'max_similarity': max_sim,
        'high_match_count': len(high_matches),
        'total_segments': total
    }


def main():
    print("="*80)
    print("FULL VIDEO COMPARISON ANALYSIS")
    print("="*80)
    print("\nComparing EVERY segment of EVERY video pair.\n")
    
    # Load database
    db_path = "video_database_ml.json"
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    db = VideoDatabase(db_path)
    all_videos = db.get_all_videos()
    
    print(f"Found {len(all_videos)} videos in database:\n")
    for i, video in enumerate(all_videos, 1):
        print(f"  {i}. {video['title']} ({format_time(video['duration'])})")
    print()
    
    # Create embedder
    embedder = AudioEmbedder()
    
    # Compare all pairs
    results = []
    
    for i in range(len(all_videos)):
        for j in range(i+1, len(all_videos)):
            result = compare_full_videos(all_videos[i], all_videos[j], embedder)
            results.append({
                'video1': all_videos[i]['title'],
                'video2': all_videos[j]['title'],
                **result
            })
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY OF ALL COMPARISONS")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['video1']}")
        print(f"  vs")
        print(f"{result['video2']}")
        print(f"  → Average: {result['avg_similarity']:.1%} | " + 
              f"Median: {result['median_similarity']:.1%} | " +
              f"Max: {result['max_similarity']:.1%} | " +
              f"High matches: {result['high_match_count']}/{result['total_segments']}")
        print()


if __name__ == "__main__":
    main()

