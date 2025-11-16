# ML Audio Fingerprinting - Testing Guide

## Quick Start Testing

### Test 1: Cross-Video Similarity (Already Ran Successfully!)

Check if the system detects that all 3 videos are the same speech:

```bash
cd /Users/muhammedcikmaz/Projects/truchain
python3.10 test_ml_embeddings.py
```

**What this does:**
- Compares the first 10 embeddings from each video pair
- Shows similarity scores for each comparison
- Tells you if they're the same content or different

**Expected Output:**
```
Video 1 vs Video 2: 96.36% → SAME CONTENT ✓
Video 1 vs Video 3: 78.51% → SAME CONTENT ✓
Video 2 vs Video 3: 77.43% → SAME CONTENT ✓
```

---

### Test 2: Automatic Clip Verification

Creates a test clip and verifies it automatically:

```bash
python3.10 test_ml_embeddings.py --clip-test
```

**What this does:**
- Creates a 20-second clip from Video 1 at the 5:00 mark
- Generates ML embeddings for the clip
- Searches database to find matches
- Shows confidence scores and timestamps

**Expected Output:**
```
✅ VERIFICATION SUCCESSFUL!
Match found in video 'Federal Reserve Chair Speech'
  Confidence: 99.8%
  Original timestamp: 300.0s (5:00)
```

---

## Custom Testing

### Test 3: Create Your Own Clip

Extract any segment from any video:

```bash
# Create a 30-second clip from Video 2, starting at 10:30
ffmpeg -i download/fedspeech2.mp4 -ss 10:30 -t 30 -c copy my_test_clip.mp4

# Verify it
python3.10 verification_ml.py my_test_clip.mp4
```

**Parameters:**
- `-ss 10:30` = Start time (MM:SS format)
- `-t 30` = Duration in seconds
- `-c copy` = Fast copy (no re-encoding)

---

### Test 4: Test Different Clips

Try clips from different timestamps and videos:

```bash
# Clip from beginning of Video 1
ffmpeg -i download/fedspeech1.mp4 -ss 0:00 -t 15 -c copy clip_start.mp4
python3.10 verification_ml.py clip_start.mp4

# Clip from middle of Video 2
ffmpeg -i download/fedspeech2.mp4 -ss 25:00 -t 20 -c copy clip_middle.mp4
python3.10 verification_ml.py clip_middle.mp4

# Clip from end of Video 3
ffmpeg -i download/fedspeech3.mp4 -ss 50:00 -t 10 -c copy clip_end.mp4
python3.10 verification_ml.py clip_end.mp4
```

**What to expect:**
Since all 3 videos are the same speech, clips from ANY video should match ALL videos with 75%+ similarity!

---

### Test 5: Test with Different Thresholds

Adjust sensitivity:

```bash
# Very strict (95%+ needed)
python3.10 verification_ml.py my_clip.mp4 --threshold 0.95

# Default (75%+)
python3.10 verification_ml.py my_clip.mp4 --threshold 0.75

# Relaxed (65%+)
python3.10 verification_ml.py my_clip.mp4 --threshold 0.65
```

**When to use:**
- **0.95** - Only exact same video matches
- **0.75** - Same speech, different recordings (RECOMMENDED)
- **0.65** - More lenient for heavily degraded quality

---

### Test 6: Test Short vs Long Clips

Test different clip lengths:

```bash
# Very short clip (5 seconds)
ffmpeg -i download/fedspeech1.mp4 -ss 5:00 -t 5 -c copy short_clip.mp4
python3.10 verification_ml.py short_clip.mp4

# Medium clip (30 seconds)
ffmpeg -i download/fedspeech1.mp4 -ss 5:00 -t 30 -c copy medium_clip.mp4
python3.10 verification_ml.py medium_clip.mp4

# Long clip (2 minutes)
ffmpeg -i download/fedspeech1.mp4 -ss 5:00 -t 120 -c copy long_clip.mp4
python3.10 verification_ml.py long_clip.mp4
```

**Performance:**
- **5 seconds**: 1 embedding, faster but less accurate
- **30 seconds**: 6 embeddings, good balance
- **2 minutes**: 24 embeddings, most accurate

---

## Understanding Results

### Similarity Scores Interpretation

| Score Range | Meaning | Example |
|-------------|---------|---------|
| **95-100%** | Same video, exact clip | Clip from Video 1 vs Video 1 |
| **85-95%** | Same speech, very similar recording | Video 1 vs Video 2 |
| **75-85%** | Same speech, different recording | Video 1 vs Video 3 |
| **65-75%** | Possibly similar (use with caution) | Similar topic, different speech |
| **<65%** | Different content | Completely different speeches |

### What Makes a Good Match?

1. **High average similarity** (>75%)
2. **Multiple consecutive segments match** (≥2 segments)
3. **Timestamps align** (sequential progression)

### Example Output Explained

```
✓ Match at 0.0s (confidence: 99.8%)

Match found in video 'Federal Reserve Chair Speech'
  Clip timestamp: 0.0s          ← Where in the clip
  Original timestamp: 300.0s    ← Where in original (5:00)
  Confidence: 99.8%             ← How sure (99.8% = very sure)
  Matching segments: 4          ← How many 5-sec segments matched
```

---

## Edge Case Testing

### Test 7: Test with Re-encoded Video (Quality Degradation)

Simulate lower quality:

```bash
# Re-encode with lower quality
ffmpeg -i download/fedspeech1.mp4 -ss 5:00 -t 20 -b:v 500k -b:a 64k degraded_clip.mp4

# Should still match!
python3.10 verification_ml.py degraded_clip.mp4
```

**Expected:** Should still match with 75%+ confidence despite quality loss!

---

### Test 8: Test Clips from Different Videos (Should ALL Match!)

Since all 3 videos are the same speech:

```bash
# Clip from Video 1 at 10:00
ffmpeg -i download/fedspeech1.mp4 -ss 10:00 -t 15 clip_v1.mp4

# Clip from Video 2 at 10:00  
ffmpeg -i download/fedspeech2.mp4 -ss 10:00 -t 15 clip_v2.mp4

# Clip from Video 3 at 10:00
ffmpeg -i download/fedspeech3.mp4 -ss 10:00 -t 15 clip_v3.mp4

# All three clips should match all three videos!
python3.10 verification_ml.py clip_v1.mp4
python3.10 verification_ml.py clip_v2.mp4
python3.10 verification_ml.py clip_v3.mp4
```

**What to expect:**
- Each clip should find matches in ALL 3 videos
- Confidence scores: 90%+ for same video, 75%+ for other videos

---

## Troubleshooting

### "No matches found"

**Possible causes:**
1. Clip is too short (<5 seconds)
2. Clip is from a different video not in database
3. Audio quality is severely degraded
4. Threshold is too high

**Solutions:**
```bash
# Try lower threshold
python3.10 verification_ml.py clip.mp4 --threshold 0.65

# Try longer clip
ffmpeg -i video.mp4 -ss 5:00 -t 30 longer_clip.mp4
```

---

### "Out of memory" error

**Solution:** Processing is CPU-intensive. Try:
```bash
# Process one video at a time
python3.10 process_videos_ml.py download/fedspeech1.mp4 "Title"

# Or close other applications
```

---

### Slow processing

**Expected times:**
- **Processing video**: ~10-15 seconds per minute of video
- **Verifying clip**: ~5-10 seconds per clip
- **Cross-video comparison**: ~1-2 seconds

**To speed up:**
- Use GPU if available (automatically detected)
- Test with shorter clips
- Reduce number of videos in database

---

## Complete Test Suite

Run all tests in sequence:

```bash
# 1. Test cross-video similarity
python3.10 test_ml_embeddings.py

# 2. Test automatic clip verification
python3.10 test_ml_embeddings.py --clip-test

# 3. Create custom clips
ffmpeg -i download/fedspeech1.mp4 -ss 5:00 -t 20 test1.mp4
ffmpeg -i download/fedspeech2.mp4 -ss 10:00 -t 20 test2.mp4
ffmpeg -i download/fedspeech3.mp4 -ss 15:00 -t 20 test3.mp4

# 4. Verify each clip
python3.10 verification_ml.py test1.mp4
python3.10 verification_ml.py test2.mp4
python3.10 verification_ml.py test3.mp4

# 5. Test with different thresholds
python3.10 verification_ml.py test1.mp4 --threshold 0.95
python3.10 verification_ml.py test1.mp4 --threshold 0.75
python3.10 verification_ml.py test1.mp4 --threshold 0.65

# 6. Clean up
rm test1.mp4 test2.mp4 test3.mp4
```

---

## Quick Reference Commands

```bash
# Test cross-video similarity
python3.10 test_ml_embeddings.py

# Automatic clip test
python3.10 test_ml_embeddings.py --clip-test

# Create clip (SS = start, T = duration)
ffmpeg -i download/fedspeech1.mp4 -ss MM:SS -t SECONDS -c copy clip.mp4

# Verify clip
python3.10 verification_ml.py clip.mp4

# Verify with custom threshold
python3.10 verification_ml.py clip.mp4 --threshold 0.80

# Process new video
python3.10 process_videos_ml.py path/to/video.mp4 "Video Title"
```

---

## Success Criteria

Your system is working correctly if:

1. ✅ Cross-video test shows 75%+ similarity for all pairs
2. ✅ Clips from any video match all 3 videos (since they're same speech)
3. ✅ Exact clips show 95%+ confidence
4. ✅ Different recordings show 75-90% confidence
5. ✅ Verification completes in <10 seconds per clip

---

## Next Steps After Testing

Once testing is complete:

1. **Production Integration**:
   - Integrate with your blockchain system
   - Store embeddings on IPFS
   - Store hashes on-chain

2. **API Development**:
   - Create REST API for verification
   - Add rate limiting
   - Implement caching

3. **Scale Testing**:
   - Test with 100+ videos
   - Benchmark performance
   - Optimize if needed

4. **User Interface**:
   - Build web interface for uploads
   - Show confidence scores
   - Display matched timestamps

---

## Support Files

- **Full Documentation**: `README_ML.md`
- **Technical Analysis**: `AUDIO_FINGERPRINTING_ANALYSIS.md`
- **Legacy System**: `legacy_chromaprint/` folder

Good luck with testing! 🚀

