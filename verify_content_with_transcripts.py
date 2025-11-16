#!/usr/bin/env python3
"""
Verify if videos are actually the same content by transcribing them.
This will definitively prove if the videos contain the same speech or not.
"""

import sys
import subprocess
import tempfile
from pathlib import Path
from openai import OpenAI
import os
from video_processor import VideoDatabase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib


def format_time(seconds):
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:2d}:{secs:02d}"


def extract_audio_segment(video_path: str, start_time: float, duration: float) -> Path:
    """Extract audio segment from video."""
    temp_dir = Path("temp_audio")
    temp_dir.mkdir(exist_ok=True)
    
    # Create unique filename
    hash_str = hashlib.md5(f"{video_path}_{start_time}_{duration}".encode()).hexdigest()[:8]
    output_path = temp_dir / f"segment_{hash_str}.mp3"
    
    # Skip if already extracted
    if output_path.exists():
        return output_path
    
    cmd = [
        'ffmpeg', '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-vn', '-acodec', 'libmp3lame',
        '-ar', '16000', '-ac', '1',
        '-y', str(output_path)
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def transcribe_audio(client: OpenAI, audio_path: Path) -> str:
    """Transcribe audio using OpenAI Whisper."""
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text


def main():
    print("="*80)
    print("CONTENT VERIFICATION VIA TRANSCRIPTION")
    print("="*80)
    print("\nTranscribing videos to verify if they contain the same speech.\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set it with:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Load database
    db_path = "video_database_ml.json"
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    db = VideoDatabase(db_path)
    all_videos = db.get_all_videos()
    
    print(f"Found {len(all_videos)} videos:\n")
    for i, video in enumerate(all_videos, 1):
        print(f"  {i}. {video['title']}")
    print()
    
    # Extract and transcribe 3 segments from each video
    # We'll sample from beginning, middle, and end
    segment_duration = 30  # 30 seconds each
    
    video_transcripts = {}
    
    for video in all_videos:
        video_path = f"download/{video['ipfs_cid']}"
        
        if not Path(video_path).exists():
            print(f"Warning: Video file not found: {video_path}")
            continue
        
        print(f"\n{'='*80}")
        print(f"Processing: {video['title']}")
        print(f"{'='*80}\n")
        
        duration = video['duration']
        
        # Sample 3 segments: start (skip first 30s for intro), middle, end
        segments = [
            ("Start", 30),
            ("Middle", duration / 2),
            ("End", duration - 60)  # 60s before end
        ]
        
        transcripts = []
        
        for label, start_time in segments:
            print(f"  Extracting {label} segment at {format_time(start_time)}...")
            
            try:
                audio_path = extract_audio_segment(video_path, start_time, segment_duration)
                
                print(f"  Transcribing {label} segment...")
                transcript = transcribe_audio(client, audio_path)
                
                transcripts.append({
                    'label': label,
                    'time': start_time,
                    'text': transcript
                })
                
                print(f"  ✓ {label}: \"{transcript[:100]}...\"")
                
            except Exception as e:
                print(f"  ✗ Error processing {label} segment: {e}")
        
        video_transcripts[video['title']] = {
            'path': video_path,
            'segments': transcripts
        }
    
    # Now compare transcripts
    print(f"\n\n{'='*80}")
    print("TRANSCRIPT COMPARISON")
    print(f"{'='*80}\n")
    
    video_names = list(video_transcripts.keys())
    
    for i in range(len(video_names)):
        for j in range(i+1, len(video_names)):
            video1_name = video_names[i]
            video2_name = video_names[j]
            
            print(f"\n{'─'*80}")
            print(f"Comparing: {video1_name}")
            print(f"     vs    {video2_name}")
            print(f"{'─'*80}\n")
            
            segments1 = video_transcripts[video1_name]['segments']
            segments2 = video_transcripts[video2_name]['segments']
            
            similarities = []
            
            for seg1, seg2 in zip(segments1, segments2):
                text1 = seg1['text']
                text2 = seg2['text']
                
                # Calculate text similarity
                vectorizer = TfidfVectorizer()
                try:
                    tfidf = vectorizer.fit_transform([text1, text2])
                    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
                except:
                    similarity = 0.0
                
                similarities.append(similarity)
                
                print(f"  {seg1['label']:6s} segment:")
                print(f"    Video 1: \"{text1[:80]}...\"")
                print(f"    Video 2: \"{text2[:80]}...\"")
                print(f"    Similarity: {similarity:.1%}")
                print()
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            
            print(f"  {'─'*76}")
            print(f"  Average text similarity: {avg_similarity:.1%}")
            
            if avg_similarity > 0.8:
                print(f"  → ✅ Videos contain the SAME CONTENT")
            elif avg_similarity > 0.5:
                print(f"  → ⚠️  Videos contain SIMILAR topics but different speeches")
            else:
                print(f"  → ❌ Videos contain DIFFERENT CONTENT")
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    print("What this tells us:\n")
    print("• If transcripts are >80% similar → Same speech, ML system is correct")
    print("• If transcripts are <50% similar → Different speeches, ML system is WRONG")
    print("\nThis will reveal if Wav2Vec2 is detecting speaker identity instead of content!")
    print()


if __name__ == "__main__":
    main()

