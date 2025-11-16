# Speaker Verification Guide

## Overview

This system now includes **two-stage verification**:

1. **Stage 1 (Content)**: Word-level text matching → finds WHAT was said
2. **Stage 2 (Speaker)**: Audio embeddings → verifies WHO said it

This prevents:
- ❌ Deepfakes (AI-generated voice)
- ❌ Voiceovers (different person reading the same text)
- ❌ Audio splicing (mixing different speakers)

## Quick Test

### Test Standalone Speaker Verification

```bash
python speaker_verification.py \
    test_clip.mp4 0 \
    download/fedspeech1.mp4 120
```

This extracts 10 seconds from each video and compares the speakers.

### Test Full Hybrid Verification

```bash
python test_hybrid_verification.py test_clips/exact_clip.mp4
```

This runs both stages:
1. Finds content match using text
2. Verifies speaker using audio embeddings

## Results

### ✅ Fully Verified
```
✓ Content Match: 95%
✓ Speaker Match: 91%
```
Same content + same speaker = **authentic**

### ⚠️ Partial Verification
```
✓ Content Match: 95%
✗ Speaker Match: 45%
```
Same content + different speaker = **possible deepfake/voiceover**

### ❌ Not Verified
```
✗ Content Match: 45%
```
Different content = **not from this video**

## How It Works

### On-Demand Embedding

**Unlike V1**, we don't pre-cache speaker embeddings. Instead:

1. User uploads clip
2. V2 finds content match → gets timestamp (e.g., 2:30-2:50)
3. Extract audio segments:
   - Clip: 0-10 seconds
   - Original: 2:30-2:40 (10 seconds)
4. Generate embeddings on-demand
5. Compare embeddings
6. Cleanup temp files

**Why on-demand?**
- Only embed when needed (after content match)
- Always use exact matching segments
- No storage overhead
- Fast enough (< 2 seconds per clip)

### Speaker Verification Flow

```
User Clip (10s)
    ↓
[Extract Audio] → WAV @ 16kHz
    ↓
[Wav2Vec2 Model] → 768-dim embedding
    ↓
[Normalize] → L2 normalized vector
    ↓
[Cosine Similarity] ← Compare → Original embedding
    ↓
Similarity Score (0.0 - 1.0)
    ↓
Threshold: 0.85 (85%)
    ↓
Same Speaker? ✓/✗
```

## Thresholds

### Text Similarity (Content)
- **0.80 (80%)**: Default, recommended
- Higher = stricter matching
- Lower = more permissive

### Speaker Similarity (Voice)
- **0.85 (85%)**: Default, recommended
- Higher = must be very similar voice
- Lower = allows more voice variation

## Testing Scenarios

### 1. Authentic Clip
```bash
# Create a 20-second clip from original
ffmpeg -i download/fedspeech1.mp4 -ss 120 -t 20 -c copy authentic_clip.mp4

# Test it
python test_hybrid_verification.py authentic_clip.mp4
```

**Expected**: ✅ Fully Verified (content + speaker match)

### 2. Voiceover Attack
```bash
# Record yourself reading the same transcript
python test_hybrid_verification.py my_voiceover.mp4
```

**Expected**: ⚠️ Partial (content matches, speaker doesn't)

### 3. Deepfake Test
```bash
# Use AI voice generator with same transcript
python test_hybrid_verification.py deepfake.mp4
```

**Expected**: ⚠️ Partial (content matches, speaker doesn't)

### 4. Different Video
```bash
# Use clip from completely different video
python test_hybrid_verification.py random_clip.mp4
```

**Expected**: ❌ Not Verified (content doesn't match)

## API Integration (Next Step)

Add to `api_server.py`:

```python
from speaker_verification import SpeakerVerifier

# In verify endpoint:
if content_verified:
    speaker_verifier = SpeakerVerifier()
    speaker_result = speaker_verifier.verify_speaker(
        clip_path=clip_path,
        clip_start=0,
        clip_duration=duration,
        original_path=matched_video_path,
        original_start=matched_timestamp,
        original_duration=duration,
        threshold=0.85
    )
    
    return {
        'verified': content_verified and speaker_result['verified'],
        'content_match': content_result,
        'speaker_match': speaker_result
    }
```

## Performance

- **Content Matching**: 3-5 seconds (text transcription + matching)
- **Speaker Verification**: 1-2 seconds (embedding extraction + comparison)
- **Total**: 4-7 seconds per clip

## Technical Details

### Model
- **Wav2Vec2-base**: 768-dimensional embeddings
- Trained on speaker characteristics
- Robust to audio quality

### Audio Processing
- Extract segment at exact timestamp
- Convert to 16kHz mono WAV
- No filtering (preserves speaker characteristics)
- Temporary files auto-cleaned

### Similarity Calculation
- Cosine similarity between embeddings
- Scaled to 0.0-1.0 range
- 0.85+ = same speaker
- < 0.85 = different speaker

## Troubleshooting

### "Different speaker detected" for same video
- Lower speaker threshold: `0.75` instead of `0.85`
- Check audio quality of both videos
- Verify timestamps are correct

### Slow performance
- Check GPU availability: `torch.cuda.is_available()`
- Use smaller model: `facebook/wav2vec2-base-960h`

### High memory usage
- Verify temp files are cleaned up
- Check `temp_audio/` directory

## Next Steps

1. ✅ Test standalone speaker verification
2. ✅ Test full hybrid verification
3. ⬜ Integrate into FastAPI (if tests pass)
4. ⬜ Create frontend UI
5. ⬜ Deploy to production

