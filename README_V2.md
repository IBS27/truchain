# Video Verification System V2 🎯

## Word-Level Timestamp Matching

This is the **new and improved** verification system that solves the boundary alignment problem using word-level timestamps.

---

## ✨ Key Improvements Over V1

| Feature | V1 (Hybrid) | V2 (Word-Level) |
|---------|-------------|-----------------|
| **Segmentation** | Fixed 30s segments | Word-level timestamps |
| **Boundary Issue** | ❌ Clips split across segments | ✅ No boundary issues |
| **Timestamp Accuracy** | ~30s accuracy | ✅ Sub-second accuracy |
| **Database Size** | Large (multiple segments) | Smaller (one transcription per video) |
| **Cost** | $0.36/hour | **Same** $0.36/hour |
| **Search Method** | Segment comparison | ✅ Sliding window |
| **Clip Length** | Must be ≥30s | ✅ Any length (even 5s) |

---

## 🚀 Quick Start

### 1. Set Your API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 2. Verify a Clip

```bash
# Create a test clip
ffmpeg -i download/fedspeech1.mp4 -ss 120 -t 20 -y test_clips/test_clip.mp4

# Verify it!
python3.10 verification_v2.py test_clips/test_clip.mp4
```

That's it! The system will:
- ✅ Transcribe your clip (word-level timestamps)
- ✅ Transcribe all videos in `download/` (cached automatically)
- ✅ Search for your clip using sliding window
- ✅ Return exact timestamp where it was found

---

## 📖 How It Works

### Step 1: Word-Level Transcription

```python
# Clip transcription
{
  "words": [
    {"word": "The", "start": 0.0, "end": 0.15},
    {"word": "Federal", "start": 0.2, "end": 0.55},
    {"word": "Reserve", "start": 0.6, "end": 0.95},
    ...
  ],
  "normalized_text": "the federal reserve..."
}
```

### Step 2: Sliding Window Search

```
Clip words:     ["the", "federal", "reserve", "has", "decided"]
                 ↓
Video words:    ["good", "afternoon", "my", "colleagues", "and", "i", 
                 "remain", "focused", "on", "our", "goals", "the", 
                 "federal", "reserve", "has", "decided", "to", ...]
                                                         ↑
                                                    MATCH FOUND!
```

### Step 3: Map to Timestamp

```
Match at word index: 11-15
Word 11 start time: 3.75s
Word 15 end time: 5.40s
→ Clip found at 3.75s - 5.40s
```

---

## 🎯 No More Boundary Issues!

### OLD System (V1) - Boundary Problem:

```
Database: [0----30s][30----60s][60----90s]
Clip:           [15s-------45s]
              ↑         ↑
        Split across segments!
        Lower similarity scores ❌
```

### NEW System (V2) - No Boundaries:

```
Database: [word][word][word][word][word]... (continuous)
Clip:                 [matches here]
                            ↓
                    Exact position found! ✅
```

---

## 📂 Files Created (V2 System)

| File | Purpose |
|------|---------|
| `word_transcription.py` | Transcribes videos with word-level timestamps |
| `sliding_window_matcher.py` | Finds clips using sliding window search |
| `verification_v2.py` | Main verification system |
| `process_videos_v2.py` | Optional: Pre-process all videos |
| `transcription_cache/` | Auto-generated cache directory |

---

## 🔧 Usage Examples

### Basic Verification

```bash
python3.10 verification_v2.py test_clips/my_clip.mp4
```

### Custom Video Directory

```bash
python3.10 verification_v2.py my_clip.mp4 --videos /path/to/videos
```

### Adjust Similarity Threshold

```bash
# More strict (default is 0.85 = 85%)
python3.10 verification_v2.py my_clip.mp4 --threshold 0.90

# More lenient
python3.10 verification_v2.py my_clip.mp4 --threshold 0.75
```

### Pre-process All Videos (Optional)

```bash
# Pre-transcribe all videos to speed up future verifications
python3.10 process_videos_v2.py --directory download
```

Once processed, videos are cached in `transcription_cache/` and never need to be transcribed again!

---

## 💰 Cost Breakdown

**Transcription Cost**: $0.006 per minute
**Word-level timestamps**: FREE (same price as regular transcription)

### Example Costs:

| Video Length | Transcription Cost | Cache Status |
|--------------|-------------------|--------------|
| 30 minutes | $0.18 | Once only |
| 1 hour | $0.36 | Once only |
| 2 hours | $0.72 | Once only |

**Clip verification**: Approximately $0.01-0.02 per clip (only transcribes the short clip)

---

## 🎨 Sample Output

```
================================================================================
VIDEO VERIFICATION V2 - WORD-LEVEL TIMESTAMPS
================================================================================

Clip: test_clip.mp4
Video directory: download
Similarity threshold: 85.0%

STEP 1: Transcribing Clip
--------------------------------------------------------------------------------
Transcribing: test_clip.mp4
  Extracting audio...
  Calling Whisper API (word-level timestamps)...
  ✓ Transcribed: 47 words, 20.5s duration

STEP 2: Loading Video Transcriptions
--------------------------------------------------------------------------------
Found 4 video(s) to search

[1/4] Processing fedspeech1.mp4...
✓ Loaded from cache: fedspeech1_abc123.json

STEP 3: Sliding Window Search
--------------------------------------------------------------------------------
Searching clip in 4 videos...
Clip: 47 words

  [1/4] Searching in fedspeech1.mp4...
    ✓ Match found: 96.8% at 120.3s
  [2/4] Searching in fedspeech2.mp4...
    ✗ No match (threshold: 85.0%)

STEP 4: Results
--------------------------------------------------------------------------------

✓ Found 1 match(es):

1. fedspeech1.mp4
   Time: 02:00 - 02:20
   Similarity: 96.8%
   Duration: 20.5s

================================================================================
BEST MATCH
================================================================================

✓ VERIFIED: Clip found in fedspeech1.mp4
  Timestamp: 02:00 - 02:20
  Similarity: 96.8%
  Matched text: the federal reserve has decided to maintain interest rates...
```

---

## 🔬 Technical Details

### Text Normalization

Both clip and video texts are normalized identically:
1. Convert to lowercase
2. Remove punctuation
3. Collapse multiple spaces
4. Strip leading/trailing spaces

Example:
```
Original:  "Good afternoon! My colleagues and I..."
Normalized: "good afternoon my colleagues and i"
```

### Similarity Calculation

Uses Python's `SequenceMatcher` (similar to Levenshtein distance):
- Compares character-level sequences
- Returns ratio from 0.0 (no match) to 1.0 (perfect match)
- Default threshold: 0.85 (85%)

### Caching Strategy

```
transcription_cache/
├── fedspeech1_abc123.json
├── fedspeech2_def456.json
└── fedspeech3_ghi789.json
```

Cache key: `{video_name}_{md5_hash_of_path}.json`

Cached data includes:
- Full text
- Normalized text
- Word array with timestamps
- Duration, language, word count

---

## 🆚 When to Use V1 vs V2

### Use V2 (This System) When:
- ✅ You want sub-second timestamp accuracy
- ✅ Clips can be any length (even 5 seconds)
- ✅ You need to avoid boundary alignment issues
- ✅ Text-based matching is sufficient

### Use V1 (Hybrid) When:
- You need speaker verification (deepfake detection)
- You want both content AND voice matching
- You're concerned about voiceovers

**Recommendation**: Use **V2 for now**, add speaker verification later if needed.

---

## 🐛 Troubleshooting

### "No matches found"

1. **Lower threshold**: Try `--threshold 0.75` or `0.70`
2. **Check transcription**: Run `python3.10 word_transcription.py your_clip.mp4` to see what Whisper heard
3. **Audio quality**: Ensure audio is clear (no heavy music/noise)

### "API key not set"

```bash
export OPENAI_API_KEY='sk-proj-...'
```

### "No video files found"

Make sure videos are in `download/` directory or specify `--videos /path/to/videos`

### Slow verification

**First run is slow** (transcribing all videos). Subsequent runs are **fast** (uses cache).

To pre-process:
```bash
python3.10 process_videos_v2.py --directory download
```

---

## 📊 Performance

| Operation | First Run | With Cache |
|-----------|-----------|------------|
| Process 1 hour video | ~5 min | Instant |
| Verify 20s clip | ~8 sec | ~3 sec |
| Verify 5s clip | ~5 sec | ~2 sec |

---

## 🎉 Success Criteria

A clip is **verified** if:
1. ✅ Similarity ≥ threshold (default 85%)
2. ✅ Match found in at least one video
3. ✅ Exact timestamp position returned

---

## 📝 Next Steps

1. ✅ **Test with your clips** (create clips from known positions and verify)
2. Add speaker verification later if needed (optional)
3. Integrate with blockchain/IPFS (future)
4. Build web interface (future)

---

## 🤝 Need Help?

The system is ready to use! Just:

```bash
export OPENAI_API_KEY='your-key'
python3.10 verification_v2.py your_clip.mp4
```

**That's it!** No database setup, no preprocessing required (happens automatically with caching). 🚀

