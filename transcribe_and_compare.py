#!/usr/bin/env python3
"""
Transcribe videos using OpenAI Whisper API and compare their text content.
"""

import os
import sys
import json
from pathlib import Path
import subprocess
from openai import OpenAI
from difflib import SequenceMatcher

def extract_audio_segment(video_path, output_path, start_time=0, duration=300):
    """
    Extract a segment of audio from video for transcription.
    OpenAI API has a 25MB file size limit, so we extract 5-minute segments.
    """
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-vn',  # No video
        '-acodec', 'libmp3lame',
        '-ar', '16000',  # 16kHz for speech
        '-ac', '1',  # Mono
        '-b:a', '64k',  # Low bitrate to keep file small
        '-y',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr}")
    
    return output_path

def get_video_duration(video_path):
    """Get video duration in seconds."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def transcribe_video(video_path, client, segments_to_transcribe=3):
    """
    Transcribe video using OpenAI Whisper API.
    Transcribes multiple segments across the video.
    """
    print(f"\n{'─'*80}")
    print(f"Transcribing: {Path(video_path).name}")
    print(f"{'─'*80}")
    
    duration = get_video_duration(video_path)
    print(f"Video duration: {int(duration//60)}:{int(duration%60):02d}")
    
    # Create temp directory for audio segments
    temp_dir = Path("temp_audio_segments")
    temp_dir.mkdir(exist_ok=True)
    
    transcriptions = []
    segment_duration = 300  # 5 minutes per segment
    
    # Calculate evenly spaced segments across the video
    if duration <= segment_duration:
        segments = [0]
    else:
        step = (duration - segment_duration) / (segments_to_transcribe - 1)
        segments = [int(i * step) for i in range(segments_to_transcribe)]
    
    print(f"\nTranscribing {len(segments)} segments across the video...\n")
    
    for idx, start_time in enumerate(segments, 1):
        try:
            # Extract audio segment
            audio_file = temp_dir / f"segment_{idx}.mp3"
            print(f"  Segment {idx}: Extracting audio from {int(start_time//60)}:{int(start_time%60):02d}...")
            
            actual_duration = min(segment_duration, duration - start_time)
            extract_audio_segment(video_path, str(audio_file), start_time, actual_duration)
            
            # Check file size
            file_size_mb = audio_file.stat().st_size / (1024 * 1024)
            print(f"             Audio file size: {file_size_mb:.2f} MB")
            
            if file_size_mb > 25:
                print(f"             ⚠️  Warning: File too large, skipping...")
                continue
            
            # Transcribe with OpenAI
            print(f"             Transcribing with OpenAI Whisper...")
            with open(audio_file, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            transcriptions.append({
                'start_time': start_time,
                'duration': actual_duration,
                'text': transcript.text,
                'segments': transcript.segments if hasattr(transcript, 'segments') else []
            })
            
            # Show preview
            preview = transcript.text[:200] + "..." if len(transcript.text) > 200 else transcript.text
            print(f"             ✓ Transcribed {len(transcript.text)} characters")
            print(f"             Preview: \"{preview}\"")
            
            # Clean up
            audio_file.unlink()
            
        except Exception as e:
            print(f"             ✗ Error: {e}")
            continue
    
    # Combine all transcriptions
    full_text = " ".join(t['text'] for t in transcriptions)
    
    print(f"\n{'─'*80}")
    print(f"Total transcribed text: {len(full_text)} characters")
    print(f"{'─'*80}\n")
    
    return {
        'video_path': video_path,
        'full_text': full_text,
        'segments': transcriptions,
        'duration': duration
    }

def calculate_text_similarity(text1, text2):
    """Calculate similarity between two texts using SequenceMatcher."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_common_phrases(text1, text2, min_length=50):
    """Find common phrases between two texts."""
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    
    common_phrases = []
    
    for i in range(len(words1) - 10):
        phrase = ' '.join(words1[i:i+10])
        if phrase in ' '.join(words2):
            common_phrases.append(phrase)
    
    return common_phrases[:10]  # Return first 10

def main():
    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("="*80)
        print("OpenAI API Key Required")
        print("="*80)
        print("\nPlease set your OpenAI API key:")
        print("\n  export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr run:")
        print(f"\n  OPENAI_API_KEY='your-key' python3.10 {sys.argv[0]}")
        print("\n" + "="*80 + "\n")
        sys.exit(1)
    
    print("="*80)
    print("VIDEO TRANSCRIPTION AND COMPARISON")
    print("="*80)
    print("\nUsing OpenAI Whisper API to transcribe videos...")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}\n")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Find all videos
    video_dir = Path("download")
    videos = sorted(video_dir.glob("fedspeech*.mp4"))
    
    if not videos:
        print("Error: No videos found in download/ directory")
        sys.exit(1)
    
    print(f"Found {len(videos)} videos:\n")
    for i, video in enumerate(videos, 1):
        print(f"  {i}. {video.name}")
    
    # Transcribe all videos
    transcriptions = []
    for video in videos:
        try:
            result = transcribe_video(str(video), client, segments_to_transcribe=3)
            transcriptions.append(result)
            
            # Save individual transcription
            output_file = Path(f"transcription_{video.stem}.txt")
            with open(output_file, 'w') as f:
                f.write(f"Video: {video.name}\n")
                f.write(f"Duration: {int(result['duration']//60)}:{int(result['duration']%60):02d}\n")
                f.write(f"\n{'='*80}\n\n")
                f.write(result['full_text'])
            print(f"✓ Saved transcription to {output_file}")
            
        except Exception as e:
            print(f"✗ Failed to transcribe {video.name}: {e}")
    
    if len(transcriptions) < 2:
        print("\nError: Need at least 2 successful transcriptions to compare")
        sys.exit(1)
    
    # Compare transcriptions
    print("\n" + "="*80)
    print("TRANSCRIPTION COMPARISON")
    print("="*80 + "\n")
    
    for i in range(len(transcriptions)):
        for j in range(i + 1, len(transcriptions)):
            t1 = transcriptions[i]
            t2 = transcriptions[j]
            
            print(f"{'─'*80}")
            print(f"Comparing: {Path(t1['video_path']).name} vs {Path(t2['video_path']).name}")
            print(f"{'─'*80}\n")
            
            # Calculate similarity
            similarity = calculate_text_similarity(t1['full_text'], t2['full_text'])
            
            print(f"Text Similarity: {similarity:.2%}\n")
            
            if similarity >= 0.80:
                print("✅ SAME CONTENT - High text similarity (>80%)")
            elif similarity >= 0.60:
                print("⚠️  SIMILAR CONTENT - Moderate text similarity (60-80%)")
            else:
                print("✗  DIFFERENT CONTENT - Low text similarity (<60%)")
            
            # Find common phrases
            print(f"\nSample common phrases:")
            common = find_common_phrases(t1['full_text'], t2['full_text'])
            if common:
                for phrase in common[:5]:
                    print(f"  • \"{phrase}...\"")
            else:
                print("  (No significant common phrases found)")
            
            print()
    
    # Save comparison results
    comparison_file = Path("transcription_comparison.json")
    with open(comparison_file, 'w') as f:
        json.dump({
            'transcriptions': [
                {
                    'video': Path(t['video_path']).name,
                    'text_length': len(t['full_text']),
                    'text_preview': t['full_text'][:500]
                }
                for t in transcriptions
            ]
        }, f, indent=2)
    
    print(f"{'='*80}")
    print(f"✓ Comparison saved to {comparison_file}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()

