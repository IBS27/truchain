# Hybrid Video Verification System

## 🎯 Overview

This system verifies if a video clip is an authentic excerpt from official campaign videos using a **two-stage verification process**:

1. **CONTENT MATCHING** (Transcription + Text Similarity)
   - Transcribes the clip using OpenAI Whisper
   - Compares text semantically against database transcripts
   - Finds WHAT was said and WHERE in the original video

2. **SPEAKER VERIFICATION** (Audio Embeddings)
   - Compares voice characteristics using Wav2Vec2 embeddings
   - Verifies WHO is speaking
   - Prevents deepfakes and voiceovers

## 🔒 What This Prevents

✅ **False Positives**: Different speeches by same person (e.g., two different Fed speeches by Powell)
✅ **Deepfakes**: Same words spoken by different voice (AI-generated speech)
✅ **Voiceovers**: Actor reading the same transcript
✅ **Out-of-Context Clips**: Shows exact timestamp in original video for context

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip3.10 install -r requirements.txt
```

### 2. Set OpenAI API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Verify FFmpeg Installation

```bash
ffmpeg -version
```

## 🚀 Quick Start

### Step 1: Process Original Videos

Process all videos in the `download/` directory:

```bash
python3.10 process_videos_hybrid.py --directory download
```

Or process a single video:

```bash
python3.10 process_videos_hybrid.py \
  --video download/fedspeech1.mp4 \
  --title "Federal Reserve Chair Speech"
```

This will:
- Transcribe the entire video (30-second segments)
- Generate audio embeddings for speaker verification
- Store everything in `video_database_hybrid.json`

**Cost**: Approximately $0.36 per hour of video (Whisper API)

### Step 2: Verify a Clip

```bash
python3.10 hybrid_verification.py test_clips/user_clip.mp4
```

Example output:

```
================================================================================
HYBRID VERIFICATION
================================================================================

Verifying clip: test_clips/user_clip.mp4

STAGE 1: Content Analysis (Transcription)
--------------------------------------------------------------------------------
Transcribing video: test_clips/user_clip.mp4
...

STAGE 2: Database Search (Text Matching)
--------------------------------------------------------------------------------
✓ Content match found!
  Video ID: fedspeech1.mp4
  Timestamp: 02:00 - 02:30
  Similarity: 94.2%
  Consecutive matches: 3

STAGE 3: Speaker Verification (Audio Embeddings)
--------------------------------------------------------------------------------
  Segment 1: 96.3%
  Segment 2: 95.8%
  Segment 3: 96.1%

  Average speaker similarity: 96.1%
  ✓ Speaker verified (threshold: 90.0%)

================================================================================
FINAL VERDICT
================================================================================

  ✓ VERIFIED with HIGH confidence. Content matches at 02:00 and speaker is verified.
```

## 📊 Understanding Results

### Verification Levels

| Confidence | Meaning |
|------------|---------|
| **HIGH** | Content similarity ≥85% AND speaker verified ≥90% AND ≥3 consecutive matches |
| **MEDIUM** | Content similarity ≥75% AND speaker verified ≥90% AND ≥2 consecutive matches |
| **LOW** | Content matches but speaker verification failed (possible deepfake) |
| **NOT VERIFIED** | Content doesn't match any video in database |

### Key Metrics

- **Content Similarity**: How well the text matches (0-100%)
- **Speaker Similarity**: How well the voice matches (0-100%)
- **Consecutive Matches**: Number of 30-second segments that match in sequence
- **Timestamp Range**: Where in the original video the clip appears

## 🧪 Testing

### Run Test Suite

```bash
python3.10 test_hybrid_system.py
```

Tests include:
1. ✅ Exact clip verification (should pass with HIGH confidence)
2. ✅ Different video rejection (should be rejected)
3. ✅ Timestamp accuracy (within 30 seconds)
4. ⚠️ Deepfake detection (conceptual - requires test video)

### Create Test Clips

```bash
# Create a 10-second exact clip from an original video
ffmpeg -i download/fedspeech1.mp4 -ss 30 -t 10 -y test_clips/exact_clip_10s.mp4

# Create a degraded quality clip
ffmpeg -i download/fedspeech1.mp4 -ss 60 -t 15 -b:a 32k -ar 16000 -y test_clips/degraded_clip.mp4
```

## 🏗️ System Architecture

```
User Clip
    ↓
┌──────────────────────────────────────────────────┐
│  STAGE 1: CONTENT MATCHING                       │
├──────────────────────────────────────────────────┤
│  1. Transcribe clip (Whisper API)               │
│  2. Compare text vs database transcripts         │
│  3. Find matching segments & timestamps          │
└──────────────────────────────────────────────────┘
    ↓ (If content matches)
┌──────────────────────────────────────────────────┐
│  STAGE 2: SPEAKER VERIFICATION                   │
├──────────────────────────────────────────────────┤
│  1. Extract audio embeddings (Wav2Vec2)          │
│  2. Compare voice characteristics                │
│  3. Verify same speaker                          │
└──────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────┐
│  VERDICT                                         │
├──────────────────────────────────────────────────┤
│  ✓ HIGH: Both content & speaker match           │
│  ⚠ MEDIUM: Good content match, speaker verified  │
│  ⚠ LOW: Content matches but speaker doesn't     │
│  ✗ NOT VERIFIED: Content doesn't match          │
└──────────────────────────────────────────────────┘
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `audio_transcription.py` | Transcribes videos using Whisper API |
| `text_matching.py` | Semantic text comparison using sentence-transformers |
| `audio_embedding.py` | Speaker verification using Wav2Vec2 |
| `hybrid_verification.py` | Main verification pipeline |
| `process_videos_hybrid.py` | Process videos for database |
| `video_database_hybrid.json` | Database with transcripts + embeddings |
| `test_hybrid_system.py` | Test suite |

## 🔧 Configuration

### Adjust Thresholds

Edit `hybrid_verification.py`:

```python
class HybridVerifier:
    TEXT_SIMILARITY_THRESHOLD = 0.75      # Content match threshold (75%)
    SPEAKER_SIMILARITY_THRESHOLD = 0.90    # Speaker match threshold (90%)
    MIN_CONSECUTIVE_MATCHES = 2            # Minimum segments to match
```

### Use Local Whisper (No API Cost)

Replace `audio_transcription.py` to use `whisper` library instead of OpenAI API:

```bash
pip3.10 install openai-whisper
```

Then modify the transcription code to use local model (slower but free).

## 📈 Performance

| Operation | Time | Cost |
|-----------|------|------|
| Process 1 hour video | ~5-10 min | $0.36 (Whisper API) |
| Verify 30-second clip | ~3-8 seconds | $0.018 (Whisper API) |
| Verify with local Whisper | ~10-30 seconds | Free |

## 🎓 How It Works

### Content Matching (Text-Based)

1. **Transcription**: Converts audio to text using state-of-the-art Whisper model
2. **Semantic Similarity**: Uses sentence-transformers to compare meaning (not just exact words)
   - "The Fed decided to keep rates unchanged" ≈ "Federal Reserve maintains current interest rates"
   - Similarity: ~85%
3. **Sequential Matching**: Finds consecutive matching segments for accuracy
4. **Timestamp Detection**: Returns exact position in original video

### Speaker Verification (Voice-Based)

1. **Audio Embeddings**: Wav2Vec2 extracts voice characteristics
   - Pitch, tone, speaking style, acoustic patterns
2. **Cosine Similarity**: Compares embedding vectors
3. **Threshold Check**: Verifies similarity ≥90%

### Why Both Are Needed

| Attack Type | Content Match | Speaker Match | Result |
|-------------|---------------|---------------|---------|
| Different speech (same person) | ❌ Low | ✅ High | Rejected |
| Deepfake (same words, AI voice) | ✅ High | ❌ Low | Rejected |
| Authentic clip | ✅ High | ✅ High | ✅ Verified |
| Different person, different content | ❌ Low | ❌ Low | Rejected |

## 🚨 Limitations

1. **Heavy Editing**: Clips heavily edited with music/effects may fail speaker verification
2. **Very Short Clips**: < 10 seconds may not have enough consecutive matches
3. **Background Noise**: Very noisy audio may reduce transcription accuracy
4. **Cost**: Using OpenAI API costs ~$0.018 per 30-second clip verification

## 🔮 Future Improvements

1. **Local Whisper**: Use local model to eliminate API costs
2. **Blockchain Integration**: Store hashes on actual blockchain (Ethereum, Polygon)
3. **IPFS Integration**: Upload and retrieve videos from IPFS
4. **Video Fingerprinting**: Add visual fingerprinting for additional verification
5. **Web Interface**: Build user-friendly web app for verification

## 📄 License

MIT License

## 🤝 Contributing

This is a proof-of-concept for political campaign video verification. Contributions welcome!

---

**Built with:** OpenAI Whisper, Wav2Vec2, Sentence-Transformers, PyTorch

