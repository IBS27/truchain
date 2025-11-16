#!/usr/bin/env python3
"""
Compare all videos in the database with each other.
This checks if videos contain the same content regardless of timestamp offsets.
"""

from video_processor import VideoDatabase
from verification import VideoVerifier
from itertools import combinations

def compare_videos(video1, video2, verifier):
    """
    Compare two videos by finding the best match for each fingerprint
    across the entire video (ignoring timestamps).
    """
    fps1 = video1['fingerprints']
    fps2 = video2['fingerprints']
    
    if not fps1 or not fps2:
        return 0.0
    
    # For each fingerprint in video1, find the best match in video2
    matches = []
    
    for fp1 in fps1:
        best_similarity = 0
        best_fp2_time = -1
        
        for fp2 in fps2:
            similarity = verifier.calculate_similarity(fp1, fp2)
            if similarity > best_similarity:
                best_similarity = similarity
                best_fp2_time = fp2['timestamp']
        
        matches.append({
            'fp1_time': fp1['timestamp'],
            'best_similarity': best_similarity,
            'fp2_time': best_fp2_time
        })
    
    # Calculate average similarity
    avg_similarity = sum(m['best_similarity'] for m in matches) / len(matches)
    
    # Find potential offset (if high similarity)
    if avg_similarity >= 0.70:
        # Calculate time offset from high-similarity matches
        high_matches = [m for m in matches if m['best_similarity'] >= 0.80]
        if high_matches:
            offsets = [m['fp2_time'] - m['fp1_time'] for m in high_matches]
            avg_offset = sum(offsets) / len(offsets)
        else:
            avg_offset = 0
    else:
        avg_offset = 0
    
    return avg_similarity, avg_offset, matches

def main():
    print("="*80)
    print("CROSS-VIDEO COMPARISON (TIMESTAMP-INDEPENDENT)")
    print("="*80)
    print("\nComparing all videos in the database with each other...")
    print("This ignores timestamps and searches for best matches across entire videos.\n")
    
    # Load database
    db = VideoDatabase("video_database.json")
    all_videos = db.get_all_videos()
    
    if len(all_videos) < 2:
        print("Error: Need at least 2 videos in the database")
        return
    
    print(f"Found {len(all_videos)} videos:\n")
    for i, video in enumerate(all_videos, 1):
        duration_min = int(video['duration'] // 60)
        duration_sec = int(video['duration'] % 60)
        print(f"  {i}. {video['title']}")
        print(f"     Duration: {duration_min}:{duration_sec:02d}, Fingerprints: {len(video['fingerprints'])}")
    
    print("\n" + "="*80)
    print("PAIRWISE COMPARISONS")
    print("="*80)
    
    # Create verifier
    verifier = VideoVerifier("video_database.json")
    
    # Compare all pairs
    comparisons = list(combinations(range(len(all_videos)), 2))
    
    for idx, (i, j) in enumerate(comparisons, 1):
        video1 = all_videos[i]
        video2 = all_videos[j]
        
        print(f"\n{'─'*80}")
        print(f"COMPARISON {idx}/{len(comparisons)}")
        print(f"{'─'*80}")
        print(f"\nVideo A: {video1['title']}")
        print(f"Video B: {video2['title']}\n")
        
        # Compare A -> B
        print(f"Testing Video A fingerprints against Video B...")
        avg_sim_ab, offset_ab, matches_ab = compare_videos(video1, video2, verifier)
        
        # Compare B -> A
        print(f"Testing Video B fingerprints against Video A...")
        avg_sim_ba, offset_ba, matches_ba = compare_videos(video2, video1, verifier)
        
        # Average of both directions
        overall_avg = (avg_sim_ab + avg_sim_ba) / 2
        
        print(f"\n{'─'*80}")
        print(f"RESULTS:")
        print(f"{'─'*80}")
        print(f"  Video A → Video B: {avg_sim_ab:.2%} average similarity")
        if offset_ab != 0:
            print(f"                     Detected offset: {offset_ab:+.1f} seconds")
        
        print(f"  Video B → Video A: {avg_sim_ba:.2%} average similarity")
        if offset_ba != 0:
            print(f"                     Detected offset: {offset_ba:+.1f} seconds")
        
        print(f"\n  Overall Average:   {overall_avg:.2%}")
        print(f"{'─'*80}")
        
        # Interpretation
        if overall_avg >= 0.95:
            status = "🎯 SAME CONTENT - Perfect match (same source)"
            color = "GREEN"
        elif overall_avg >= 0.85:
            status = "✅ SAME CONTENT - Strong match (likely same speech)"
            color = "GREEN"
        elif overall_avg >= 0.75:
            status = "⚠️  SIMILAR CONTENT - Moderate match (possibly same speech, heavy compression)"
            color = "YELLOW"
        elif overall_avg >= 0.65:
            status = "⚠️  SOMEWHAT SIMILAR - Weak match (similar but likely different)"
            color = "YELLOW"
        else:
            status = "✗  DIFFERENT CONTENT - No significant match"
            color = "RED"
        
        print(f"\n  {status}\n")
        
        # Show sample matches for high similarity
        if overall_avg >= 0.70:
            print(f"  Sample high-confidence matches (A → B):")
            high_matches = sorted(
                [m for m in matches_ab if m['best_similarity'] >= 0.80],
                key=lambda x: x['best_similarity'],
                reverse=True
            )[:5]
            
            if high_matches:
                for m in high_matches:
                    a_min = int(m['fp1_time'] // 60)
                    a_sec = int(m['fp1_time'] % 60)
                    b_min = int(m['fp2_time'] // 60)
                    b_sec = int(m['fp2_time'] % 60)
                    print(f"    • Video A [{a_min:2d}:{a_sec:02d}] ↔ Video B [{b_min:2d}:{b_sec:02d}]: {m['best_similarity']:.2%}")
            else:
                print(f"    (No matches above 80%)")
    
    # Summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80 + "\n")
    
    print("Video Pair                                              | Avg Similarity | Status")
    print("─"*80)
    
    for i, j in comparisons:
        video1 = all_videos[i]
        video2 = all_videos[j]
        
        avg_sim_ab, _, _ = compare_videos(video1, video2, verifier)
        avg_sim_ba, _, _ = compare_videos(video2, video1, verifier)
        overall_avg = (avg_sim_ab + avg_sim_ba) / 2
        
        # Truncate titles
        title1 = video1['title'][:20] + "..." if len(video1['title']) > 20 else video1['title']
        title2 = video2['title'][:20] + "..." if len(video2['title']) > 20 else video2['title']
        
        if overall_avg >= 0.85:
            status = "✅ SAME"
        elif overall_avg >= 0.65:
            status = "⚠️  SIMILAR"
        else:
            status = "✗  DIFFERENT"
        
        print(f"{title1:23} vs {title2:23} | {overall_avg:13.2%} | {status}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()

