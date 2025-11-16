# TruChain - Video Verification API

Hybrid verification system for authenticating video clips using content matching and speaker verification.

## Quick Start

### 1. Install Dependencies
```bash
pip3.10 install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### 3. Start Server
```bash
python3.10 api_server.py
```

Server will start at: http://localhost:8000

API Docs: http://localhost:8000/docs

## How It Works

### Two-Stage Hybrid Verification

**Stage 1: Content Verification**
- Transcribes clip using OpenAI Whisper
- Word-level timestamp matching
- Finds WHAT was said and WHERE

**Stage 2: Speaker Verification**
- Extracts audio at matched timestamp
- Generates Wav2Vec2 embeddings
- Verifies WHO said it

### Verification Types

| Type | Content | Speaker | Result |
|------|---------|---------|--------|
| `full` | ✓ Match | ✓ Match | Authentic clip |
| `content_only` | ✓ Match | ✗ No match | Possible deepfake/voiceover |
| `not_verified` | ✗ No match | - | Not from database |

## API Usage

### Verify a Clip

```bash
curl -X POST "http://localhost:8000/verify" \
  -F "file=@your_clip.mp4"
```

### Response

```json
{
  "verified": true,
  "verification_type": "full",
  "best_match": {
    "video_name": "campaign_video.mp4",
    "start_time": 120.5,
    "end_time": 135.8,
    "similarity": 0.95
  },
  "speaker_verification": {
    "verified": true,
    "similarity": 0.96,
    "message": "Same speaker"
  }
}
```

### Other Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List videos
curl http://localhost:8000/videos

# Add video to database
curl -X POST "http://localhost:8000/videos/add" \
  -F "file=@new_video.mp4"
```

## Configuration

Edit `api_server.py`:

```python
TEXT_THRESHOLD = 0.80      # 80% text similarity required
SPEAKER_THRESHOLD = 0.85   # 85% speaker similarity required
```

## Project Structure

```
truchain/
├── api_server.py              # FastAPI server (main)
├── word_transcription.py      # OpenAI Whisper transcription
├── sliding_window_matcher.py  # Text matching
├── speaker_verification.py    # Speaker verification (Wav2Vec2)
├── requirements.txt           # Dependencies
├── README.md                  # This file
│
├── download/                  # Original videos (database)
├── transcription_cache/       # Cached transcriptions
├── uploads/                   # Temporary uploaded clips
├── temp_audio/                # Temporary audio files
│
├── cli_tools/                 # Command-line tools
├── testing/                   # Test scripts and samples
├── documentation/             # Additional documentation
├── utilities/                 # Helper scripts
│
└── archived/                  # Previous implementations
    ├── legacy_chromaprint/    # V0: Chromaprint fingerprinting
    ├── v1_ml_embeddings/      # V1a: ML audio embeddings
    └── v1_hybrid/             # V1b: Hybrid with segments
```

## Core Files

| File | Purpose |
|------|---------|
| `api_server.py` | FastAPI REST API server |
| `word_transcription.py` | Transcribe videos with word-level timestamps |
| `sliding_window_matcher.py` | Find clips in videos using text matching |
| `speaker_verification.py` | Verify speaker identity using audio embeddings |

## Requirements

- Python 3.10+
- OpenAI API key
- ffmpeg (for audio extraction)
- ~2GB RAM for Wav2Vec2 model

## Performance

- **Content Matching**: ~3-5 seconds
- **Speaker Verification**: ~1-2 seconds
- **Total**: ~4-7 seconds per clip

## Use Cases

✅ **Verify authentic clips** from campaign videos  
✅ **Detect deepfakes** (AI-generated voices)  
✅ **Detect voiceovers** (different person reading)  
✅ **Prevent misquoting** (fabricated content)

## Security Features

- Content verification prevents misquoting
- Speaker verification detects voice manipulation
- Word-level precision prevents splicing
- Configurable sensitivity thresholds

## Production Deployment

```bash
# Install dependencies
pip3.10 install -r requirements.txt

# Set environment
export OPENAI_API_KEY="your-key"

# Run with multiple workers
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

See `testing/` directory for test scripts:

```bash
# Test speaker verification only
cd testing
python3.10 test_speaker_only.py

# Test full hybrid verification
python3.10 test_hybrid_verification.py test_clips/speaker_test_clip.mp4
```

## Documentation

Additional documentation in `documentation/` folder:
- API Documentation
- Implementation guides
- Quick start guides
- Speaker verification details

## CLI Tools

Command-line tools in `cli_tools/` folder:
- `verification_v2.py` - CLI verification
- `process_videos_v2.py` - Batch video processing
- Supporting modules for offline processing

## Troubleshooting

### "OpenAI API key required"
```bash
export OPENAI_API_KEY="sk-..."
```

### Videos not found
Add videos to `download/` directory:
```bash
cp your_video.mp4 download/
```

### Port already in use
Change port in `api_server.py` or:
```bash
uvicorn api_server:app --port 8001
```

## Support

For issues or questions:
1. Check `documentation/` folder
2. Review test examples in `testing/`
3. Consult API docs at http://localhost:8000/docs

## Version

Current: **V2 - Hybrid Verification**

- V0: Chromaprint fingerprinting (archived)
- V1a: ML audio embeddings (archived)
- V1b: Hybrid with segments (archived)
- V2: Word-level timestamps + speaker verification (current)

## License

[Your License Here]

## Contact

[Your Contact Information]

---

**Ready to verify videos! 🚀**

Run `python3.10 api_server.py` and visit http://localhost:8000/docs to get started.
