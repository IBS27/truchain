# Hybrid Verification API Guide

## Overview

The API now uses **HYBRID VERIFICATION** combining:
1. **Content Verification** (word-level text matching) → Finds WHAT was said
2. **Speaker Verification** (audio embeddings) → Verifies WHO said it

## Verification Types

### ✅ Full Verification
```json
{
  "verified": true,
  "verification_type": "full"
}
```
- Content matches ✓
- Speaker matches ✓
- **Result**: Authentic clip

### ⚠️ Content Only
```json
{
  "verified": false,
  "verification_type": "content_only"
}
```
- Content matches ✓
- Speaker doesn't match ✗
- **Result**: Possible voiceover/deepfake

### ❌ Not Verified
```json
{
  "verified": false,
  "verification_type": "not_verified"
}
```
- Content doesn't match ✗
- **Result**: Not from database

## Configuration

```python
TEXT_THRESHOLD = 0.80      # 80% text similarity
SPEAKER_THRESHOLD = 0.85   # 85% speaker similarity
```

## API Response

```json
{
  "verification_id": "abc-123",
  "verified": true,
  "verification_type": "full",
  "clip_name": "user_clip.mp4",
  "best_match": {
    "video_name": "fedspeech1.mp4",
    "start_time": 120.5,
    "end_time": 135.8,
    "similarity": 0.95
  },
  "speaker_verification": {
    "verified": true,
    "similarity": 0.96,
    "threshold": 0.85,
    "message": "Same speaker"
  },
  "clip_info": {
    "word_count": 45,
    "duration": 15.3,
    "text": "The Federal Reserve has decided..."
  },
  "text_threshold": 0.80,
  "speaker_threshold": 0.85
}
```

## Quick Start

### 1. Start Server

```bash
python3.10 api_server.py
```

Output:
```
================================================================================
VIDEO VERIFICATION API V2 - HYBRID VERIFICATION
================================================================================

Text Threshold: 80%
Speaker Threshold: 85%
Video directory: download
Upload directory: uploads

Verification Modes:
  • Full: Content + Speaker match
  • Content Only: Content matches, speaker doesn't (possible deepfake)
  • Not Verified: Content not found

Starting server...
API docs: http://localhost:8000/docs
================================================================================
```

### 2. Verify a Clip

```bash
curl -X POST "http://localhost:8000/verify" \
  -F "file=@test_clips/speaker_test_clip.mp4"
```

### 3. Check Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "text_threshold": 0.80,
  "speaker_threshold": 0.85,
  "video_directory": "download",
  "videos_available": 4
}
```

## Use Cases

### Scenario 1: Authentic Clip
```
User uploads: 15-second clip from fedspeech1.mp4
Result:
  ✓ Content: 95% match
  ✓ Speaker: 96% match
  → verification_type: "full"
  → verified: true
```

### Scenario 2: Voiceover Attack
```
User uploads: Someone else reading the same transcript
Result:
  ✓ Content: 95% match
  ✗ Speaker: 45% match
  → verification_type: "content_only"
  → verified: false (flagged as possible deepfake)
```

### Scenario 3: Deepfake
```
User uploads: AI-generated voice with authentic transcript
Result:
  ✓ Content: 95% match
  ✗ Speaker: 62% match
  → verification_type: "content_only"
  → verified: false (flagged as possible deepfake)
```

### Scenario 4: Different Video
```
User uploads: Clip from a different speech
Result:
  ✗ Content: 45% match
  → verification_type: "not_verified"
  → verified: false
```

## Testing

### Test with cURL

```bash
# Verify a clip
curl -X POST "http://localhost:8000/verify" \
  -F "file=@test_clips/speaker_test_clip.mp4" \
  | python -m json.tool

# Get verification result
curl http://localhost:8000/verify/{verification_id}

# List videos
curl http://localhost:8000/videos

# Add a video
curl -X POST "http://localhost:8000/videos/add" \
  -F "file=@new_video.mp4" \
  -F "title=New Campaign Video"

# Health check
curl http://localhost:8000/health
```

### Test with Python

```python
import requests

# Verify a clip
with open("test_clips/speaker_test_clip.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/verify",
        files={"file": f}
    )
    
result = response.json()
print(f"Verified: {result['verified']}")
print(f"Type: {result['verification_type']}")

if result['speaker_verification']:
    speaker = result['speaker_verification']
    print(f"Speaker Similarity: {speaker['similarity']:.2%}")
```

## Performance

With hybrid verification:
- **Content Matching**: ~3-5 seconds (transcription + text matching)
- **Speaker Verification**: ~1-2 seconds (audio extraction + embedding comparison)
- **Total**: ~4-7 seconds per clip

## Security Features

1. **Content Verification**: Prevents misquoting or fabricated content
2. **Speaker Verification**: Detects voiceovers and deepfakes
3. **Two-factor verification**: Both must pass for full verification
4. **Configurable thresholds**: Adjust sensitivity as needed

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verify` | POST | Upload clip for hybrid verification |
| `/verify/{id}` | GET | Get cached verification result |
| `/videos` | GET | List available videos |
| `/videos/add` | POST | Add new video to database |
| `/videos/{name}` | DELETE | Delete video |
| `/health` | GET | System health check |
| `/preprocess` | POST | Pre-transcribe all videos |
| `/cache/clear` | GET | Clear transcription cache |

## Error Handling

### Content Match, Speaker Verification Fails
```json
{
  "verified": false,
  "verification_type": "content_only",
  "speaker_verification": {
    "verified": false,
    "error": "Failed to extract audio",
    "message": "Speaker verification failed"
  }
}
```

The API gracefully falls back to content-only verification if speaker verification encounters an error.

## Production Deployment

```bash
# Install dependencies
pip3.10 install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"

# Run with production server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## Monitoring

Key metrics to track:
- **Verification Types**: full / content_only / not_verified ratio
- **Speaker Similarity Distribution**: Detect anomalies
- **Processing Time**: Monitor performance
- **False Positive Rate**: Track content_only cases

## Notes

- Transcriptions are cached for faster subsequent verifications
- Speaker verification only runs if content match is found
- Temp files are automatically cleaned up after verification
- Model loads once at startup (~2 seconds)
- Results are cached in memory for quick retrieval

## Ready to Use!

Your API now provides industry-grade deepfake detection through hybrid verification! 🚀

