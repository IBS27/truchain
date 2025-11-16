#!/usr/bin/env python3
"""
Compare the new "different" video against all existing videos.
This tests if the ML system can distinguish DIFFERENT speeches.
"""

import sys
from pathlib import Path
from audio_embedding import AudioEmbedder
from video_processor import VideoDatabase
import numpy as np


def main():
    print("="*80)
    print("TESTING DIFFERENT SPEECH DETECTION")
    print("="*80)
    print("\nComparing the NEW video against the 3 EXISTING videos")
    print("Expected: NEW video should have LOW similarity with existing ones\n")
    
    # Load database
    db_path = "video_database_ml.json"
    
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    db = VideoDatabase(db_path)
    all_videos = db.get_all_videos()
    
    if len(all_videos) < 4:
        print(f"Error: Expected 4 videos, found {len(all_videos)}")
        sys.exit(1)
    
    print(f"Database contains {len(all_videos)} videos:\n")
    
    # Identify the new video
    new_video = None
    old_videos = []
    
    for video in all_videos:
        print(f"  • {video['title']}")
        if "Different" in video['title']:
            new_video = video
        else:
            old_videos.append(video)
    
    if not new_video:
        print("\nError: Could not find 'Different' video")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print("COMPARISON ANALYSIS")
    print(f"{'='*80}\n")
    
    # Create embedder
    embedder = AudioEmbedder()
    
    # Compare new video against each old video
    results = []
    
    for old_video in old_videos:
        print(f"{'─'*80}")
        print(f"Comparing: {new_video['title']} vs {old_video['title']}")
        print(f"{'─'*80}\n")
        
        # Sample 20 embeddings from each video for comparison
        sample_size = min(20, len(new_video['fingerprints']), len(old_video['fingerprints']))
        
        # Get evenly spaced samples
        new_indices = np.linspace(0, len(new_video['fingerprints'])-1, sample_size, dtype=int)
        old_indices = np.linspace(0, len(old_video['fingerprints'])-1, sample_size, dtype=int)
        
        new_samples = [new_video['fingerprints'][i] for i in new_indices]
        old_samples = [old_video['fingerprints'][i] for i in old_indices]
        
        # Calculate similarities
        similarities = []
        
        for new_emb in new_samples:
            best_sim = 0
            for old_emb in old_samples:
                sim = embedder.calculate_similarity(new_emb, old_emb)
                if sim > best_sim:
                    best_sim = sim
            similarities.append(best_sim)
        
        # Statistics
        avg_sim = np.mean(similarities)
        max_sim = np.max(similarities)
        min_sim = np.min(similarities)
        std_sim = np.std(similarities)
        
        print(f"  Sampled {sample_size} embeddings from each video")
        print(f"\n  Top 5 best matches:")
        sorted_sims = sorted(similarities, reverse=True)[:5]
        for idx, sim in enumerate(sorted_sims, 1):
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
            color = "🟢"
        elif avg_sim >= 0.75:
            result = "✅ SAME CONTENT (Good confidence)"
            status = "SAME"
            color = "🟢"
        elif avg_sim >= 0.65:
            result = "⚠️  POSSIBLY SIMILAR CONTENT"
            status = "SIMILAR"
            color = "🟡"
        else:
            result = "✗  DIFFERENT CONTENT"
            status = "DIFFERENT"
            color = "🔴"
        
        print(result)
        print()
        
        results.append({
            'comparison': f"NEW vs {old_video['title']}",
            'avg_sim': avg_sim,
            'max_sim': max_sim,
            'status': status,
            'color': color
        })
    
    # Summary
    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    print("Comparison of NEW video against EXISTING videos:\n")
    for result in results:
        print(f"{result['color']} {result['comparison']}")
        print(f"   Average: {result['avg_sim']:.2%} | Max: {result['max_sim']:.2%} | Status: {result['status']}")
        print()
    
    # Overall conclusion
    print(f"{'='*80}")
    print("CONCLUSION")
    print(f"{'='*80}\n")
    
    all_different = all(r['status'] == 'DIFFERENT' for r in results)
    all_same = all(r['status'] == 'SAME' for r in results)
    
    if all_different:
        print("✅ CORRECT: New video is DIFFERENT from all existing videos!")
        print("   The ML system successfully distinguished different speech content.\n")
        print("   Similarity scores <65% indicate different speeches.")
    elif all_same:
        print("⚠️  UNEXPECTED: New video shows as SAME as existing videos!")
        print("   Similarity scores >75% suggest this might be the same speech.\n")
        print("   Please verify if 'fedspeechdifferent.mp4' is truly different.")
    else:
        print("⚠️  MIXED RESULTS: Some similarities are borderline.")
        print("   This suggests the speeches might have overlapping content.\n")
    
    print(f"{'='*80}\n")
    
    print("Threshold Guide:")
    print("  • >85%: Same speech, high confidence")
    print("  • 75-85%: Same speech, good confidence")
    print("  • 65-75%: Possibly similar")
    print("  • <65%: Different speeches ← Expected for this test")
    print()


if __name__ == "__main__":
    main()


