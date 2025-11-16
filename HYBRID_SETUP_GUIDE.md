# 🚀 Quick Setup Guide - Hybrid Verification System

## What You Need

1. ✅ Python 3.10
2. ✅ FFmpeg (already installed)
3. ✅ OpenAI API Key
4. ✅ Your campaign videos

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd /Users/muhammedcikmaz/Projects/truchain
pip3.10 install sentence-transformers
```

(Other dependencies already installed)

### Step 2: Set API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Get your key**: https://platform.openai.com/api-keys

### Step 3: Process Your Videos

```bash
python3.10 process_videos_hybrid.py --directory download
```

This will:
- ✅ Transcribe all videos in `download/`
- ✅ Generate speaker embeddings
- ✅ Store in `video_database_hybrid.json`

**Expected time**: ~5-10 minutes per hour of video
**Cost**: ~$0.36 per hour of video

### Step 4: Verify a Clip

```bash
# Test with an existing video
python3.10 hybrid_verification.py download/fedspeech1.mp4
```

Or create a test clip first:

```bash
# Create 10-second test clip
mkdir -p test_clips
ffmpeg -i download/fedspeech1.mp4 -ss 30 -t 10 -y test_clips/test_clip.mp4

# Verify it
python3.10 hybrid_verification.py test_clips/test_clip.mp4
```

## Expected Output

```
================================================================================
HYBRID VERIFICATION
================================================================================

STAGE 1: Content Analysis (Transcription)
✓ Transcribed clip

STAGE 2: Database Search (Text Matching)
✓ Content match found!
  Video ID: fedspeech1.mp4
  Timestamp: 00:30 - 00:40
  Similarity: 98.5%

STAGE 3: Speaker Verification (Audio Embeddings)
✓ Speaker verified
  Average similarity: 96.8%

================================================================================
FINAL VERDICT
================================================================================

✓ VERIFIED with HIGH confidence.
```

## What Makes This Different?

### ❌ OLD System (Wav2Vec2 Only)
- Compared audio embeddings
- **Problem**: Detected SPEAKER, not CONTENT
- Result: Powell speech 1 matched Powell speech 2 at 98% (WRONG!)

### ✅ NEW System (Hybrid)
- Stage 1: Compare WORDS (transcription)
- Stage 2: Verify SPEAKER (audio embeddings)
- **Solution**: Detects content first, then verifies speaker
- Result: Powell speech 1 vs speech 2 = NO MATCH (CORRECT!)

## Testing Different Scenarios

### Scenario 1: Same Speech, Different Recording
```bash
# Your fedspeech1, fedspeech2, fedspeech3 are same speech
# System will verify them as matching content with speaker verification
```

### Scenario 2: Different Speech, Same Speaker
```bash
# fedspeechdifferent.mp4 vs fedspeech1.mp4
# System will correctly identify as DIFFERENT content
```

### Scenario 3: Deepfake (Future Test)
```bash
# Same transcript, different voice
# Content matches, speaker verification FAILS
# Result: "Possible deepfake detected"
```

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='sk-proj-...'
```

### "Module 'sentence_transformers' not found"
```bash
pip3.10 install sentence-transformers
```

### "Video already in database"
The system skips already-processed videos automatically. This is normal!

### Videos Take Long to Process
- 1 hour video = ~5-10 minutes processing
- Most time spent on transcription (Whisper API)
- Embeddings are faster

### High API Costs
Switch to local Whisper:
```bash
pip3.10 install openai-whisper
# Then modify audio_transcription.py to use local model
```

## Next Steps

1. ✅ **Process all your campaign videos**
   ```bash
   python3.10 process_videos_hybrid.py --directory download
   ```

2. ✅ **Test verification with real clips**
   ```bash
   # Create clip from your video
   ffmpeg -i download/your_video.mp4 -ss 120 -t 30 -y test.mp4
   
   # Verify it
   python3.10 hybrid_verification.py test.mp4
   ```

3. ✅ **Adjust thresholds if needed**
   - Edit `hybrid_verification.py`
   - Change `TEXT_SIMILARITY_THRESHOLD` (default: 0.75)
   - Change `SPEAKER_SIMILARITY_THRESHOLD` (default: 0.90)

4. ✅ **Run test suite**
   ```bash
   python3.10 test_hybrid_system.py
   ```

## Questions?

See the full documentation: [README_HYBRID.md](README_HYBRID.md)

---

**You're ready to go! 🎉**

The hybrid system will correctly:
- ✅ Match clips from same speech
- ✅ Reject clips from different speeches
- ✅ Show exact timestamps in original video
- ✅ Verify speaker identity
- ✅ Detect potential deepfakes

