# 🚀 V2 System - Quick Start Guide

## The Problem We Solved

**V1 Issue**: Fixed 30-second segments caused boundary alignment problems
**V2 Solution**: Word-level timestamps + sliding window = perfect matching

---

## Setup (30 seconds)

```bash
cd /Users/muhammedcikmaz/Projects/truchain

# Set API key
export OPENAI_API_KEY='your-key-here'

# That's it! No database to build.
```

---

## Test It Now (2 minutes)

### Step 1: Create a test clip

```bash
# Create a 15-second clip from 2:00 mark
ffmpeg -i download/fedspeech1.mp4 -ss 120 -t 15 -y test_clip.mp4
```

### Step 2: Verify it

```bash
python3.10 verification_v2.py test_clip.mp4
```

### Expected Output

```
✓ VERIFIED: Clip found in fedspeech1.mp4
  Timestamp: 02:00 - 02:15
  Similarity: 96.8%
```

---

## How It Works (Simple)

1. **Transcribe your clip** with word timestamps
2. **Slide through each video** comparing word sequences
3. **Find best match** and map to exact timestamp
4. **Return result** with sub-second accuracy

---

## Key Features

✅ **No boundary issues** - clips can start at ANY time
✅ **Any clip length** - 5s, 10s, 30s, whatever
✅ **Sub-second accuracy** - exact timestamps
✅ **Auto-caching** - videos transcribed once, used forever
✅ **Fast** - 3-8 seconds per verification (after cache)

---

## Files You Need to Know

| File | What It Does |
|------|-------------|
| `verification_v2.py` | Main script - verify clips |
| `word_transcription.py` | Handles Whisper API + caching |
| `sliding_window_matcher.py` | Finds clips in videos |
| `process_videos_v2.py` | Optional: pre-process all videos |

---

## Common Commands

### Verify a clip (basic)
```bash
python3.10 verification_v2.py my_clip.mp4
```

### Verify with custom threshold
```bash
# More strict (90% similarity required)
python3.10 verification_v2.py my_clip.mp4 --threshold 0.90

# More lenient (75% similarity required)
python3.10 verification_v2.py my_clip.mp4 --threshold 0.75
```

### Verify against different video directory
```bash
python3.10 verification_v2.py my_clip.mp4 --videos /path/to/videos
```

### Pre-process all videos (optional, speeds up first run)
```bash
python3.10 process_videos_v2.py --directory download
```

---

## Testing Different Scenarios

### Test 1: Exact clip from known position
```bash
# Extract from 2:00, duration 20s
ffmpeg -i download/fedspeech1.mp4 -ss 120 -t 20 -y test_exact.mp4
python3.10 verification_v2.py test_exact.mp4

# Expected: ~95%+ similarity at 02:00
```

### Test 2: Short clip (10 seconds)
```bash
# Extract from 5:00, duration 10s
ffmpeg -i download/fedspeech1.mp4 -ss 300 -t 10 -y test_short.mp4
python3.10 verification_v2.py test_short.mp4

# Expected: Still works! (no 30s minimum)
```

### Test 3: Clip from middle (boundary test)
```bash
# Extract from 2:15 (not aligned to 30s boundaries)
ffmpeg -i download/fedspeech1.mp4 -ss 135 -t 15 -y test_boundary.mp4
python3.10 verification_v2.py test_boundary.mp4

# Expected: No boundary issues! ✅
```

### Test 4: Degraded quality
```bash
# Extract with lower quality
ffmpeg -i download/fedspeech1.mp4 -ss 180 -t 20 -b:a 32k -ar 16000 -y test_degraded.mp4
python3.10 verification_v2.py test_degraded.mp4

# Expected: Still matches (transcription is robust)
```

---

## Troubleshooting

### No matches found?

1. **Check transcription quality**:
   ```bash
   python3.10 word_transcription.py your_clip.mp4
   ```
   Look at the `full_text` - is it accurate?

2. **Lower threshold**:
   ```bash
   python3.10 verification_v2.py your_clip.mp4 --threshold 0.70
   ```

3. **Check audio quality**: Make sure there's not too much background noise/music

### Slow on first run?

**This is normal!** First run transcribes all videos (~5-10 min per hour of video).

Speed it up:
```bash
# Pre-process all videos
python3.10 process_videos_v2.py --directory download
```

After caching, verification is fast (~3-8 seconds).

### API errors?

Make sure your API key is set:
```bash
echo $OPENAI_API_KEY  # Should show your key
```

If not:
```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
```

---

## Cache Management

### Where are transcriptions cached?

```
transcription_cache/
├── fedspeech1_abc123.json
├── fedspeech2_def456.json
└── ...
```

### Clear cache (to re-transcribe)

```bash
rm -rf transcription_cache/
```

### View cached transcription

```bash
cat transcription_cache/fedspeech1_*.json | head -50
```

---

## Cost Tracking

**Per transcription**: $0.006/minute
**Per clip verification**: ~$0.01-0.02

### Example costs:

```
Process 4 videos (1 hour each) = $1.44 (one-time)
Verify 100 clips = $1.00-2.00
Total for testing = ~$3.50
```

Videos are cached, so you only pay once per video!

---

## What's Next?

1. ✅ Test with your own clips
2. ✅ Verify results are accurate
3. ✅ Adjust threshold if needed
4. Later: Add speaker verification (optional)
5. Later: Integrate with blockchain

---

## Legacy Systems

You still have the old systems (for reference):

- `video_database.json` - Chromaprint (legacy)
- `video_database_ml.json` - ML embeddings only (V1 attempt)
- `video_database_hybrid.json` - Hybrid system (V1)
- All `*_ml.py` files - Previous implementation

**These are NOT used by V2.** V2 uses:
- `transcription_cache/` - Cached word-level transcriptions
- No database needed!

---

## Why V2 Is Better

| Feature | V1 | V2 |
|---------|----|----|
| Boundary issues | ❌ Yes | ✅ No |
| Min clip length | 30s | Any length |
| Timestamp accuracy | ~30s | Sub-second |
| Database size | 2M+ lines | Small cache files |
| Setup complexity | High | Low |
| Speed (cached) | Slow | Fast |

---

## You're Ready! 🎉

Just run:

```bash
export OPENAI_API_KEY='your-key'
python3.10 verification_v2.py your_clip.mp4
```

That's it! The system handles everything else automatically. 🚀

