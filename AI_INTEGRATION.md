# AI Layer Integration Guide

This document explains how the Python AI verification service integrates with the Node.js backend and React frontend.

## Architecture Overview

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │ ───> │    Node.js   │ ───> │   Python AI  │
│    React     │      │   Backend    │      │   Service    │
└──────────────┘      └──────────────┘      └──────────────┘
                            │                      │
                            ↓                      ↓
                      ┌──────────────┐      ┌──────────────┐
                      │     IPFS     │      │   OpenAI     │
                      │   Storage    │      │   Whisper    │
                      └──────────────┘      └──────────────┘
                            ↓
                      ┌──────────────┐
                      │    Solana    │
                      │  Blockchain  │
                      └──────────────┘
```

## Services Overview

### 1. Python AI Service (Port 8000)
**Location**: `/ai-layer/`

**Purpose**: Hybrid video verification (content + speaker)

**Key Features**:
- **Content Verification**: Word-level text matching using OpenAI Whisper
- **Speaker Verification**: Voice authentication using Wav2Vec2 embeddings
- **Caching**: Transcriptions cached for faster verification

**Endpoints**:
- `POST /verify` - Verify a clip
- `POST /videos/add` - Register official video
- `GET /videos` - List all videos
- `GET /health` - Health check

### 2. Node.js Backend (Port 3001)
**Location**: `/backend/`

**Purpose**: API orchestration and business logic

**Key Features**:
- IPFS upload/download integration
- AI service communication
- Social features (flags, comments)
- Future: Solana blockchain integration

**New Endpoints**:
- `POST /api/verification/verify-clip` - Verify clip via AI service
- `GET /api/verification/health` - Check AI service status
- `GET /api/verification/videos` - List videos in AI database
- `POST /api/ipfs/upload?registerWithAI=true` - Upload & register with AI

### 3. React Frontend (Port 5173)
**Location**: `/frontend/`

**Purpose**: User interface

**New Service**: `/frontend/src/services/verification.service.ts`
- Frontend API client for verification
- Helper functions for formatting results
- Type-safe TypeScript interfaces

---

## Integration Flow

### Flow 1: Official Uploads Video (Portal)

**User**: Official or their media team

```
1. Frontend: User uploads video file
   ↓
2. Backend: POST /api/ipfs/upload?registerWithAI=true
   - Save video temporarily
   - Compute hash
   - Upload to IPFS → get CID
   - Copy video to ai-layer/download/
   ↓
3. Backend calls Python AI: POST /videos/add
   - Python transcribes video (Whisper API)
   - Caches transcription
   ↓
4. Backend calls Solana: register_video(hash, cid)
   - Store video metadata on-chain
   ↓
5. Return success to frontend
```

**Result**: Video is registered in IPFS, AI database, and blockchain

---

### Flow 2: User Verifies Clip (Feed)

**User**: Regular user browsing social media

```
1. Frontend: User uploads clip to verify
   ↓
2. Backend: POST /api/verification/verify-clip
   - Save clip temporarily
   ↓
3. Backend calls Python AI: POST /verify
   - Transcribe clip (Whisper)
   - Match content (sliding window text matching)
   - Verify speaker (Wav2Vec2 embeddings)
   - Return verification result
   ↓
4. Backend queries Solana
   - Get on-chain status of matched video
   - Combine AI result + blockchain status
   ↓
5. Backend saves to database
   - Cache verification result
   - Track verification history
   ↓
6. Frontend displays result:
   - Verification type (full/content_only/not_verified)
   - Matched video & timestamp
   - On-chain status
   - Speaker verification
```

**Result**: User sees comprehensive verification with provenance

---

## Verification Types

The AI service returns one of three verification types:

### 1. `full` ✅
**What it means**: Both content AND speaker verified

**Technical**:
- Content similarity ≥ 80%
- Speaker similarity ≥ 85%

**User-facing**:
- "Verified - Authentic Clip"
- Green badge
- High confidence this is a real, unaltered clip

---

### 2. `content_only` ⚠️
**What it means**: Content matches but speaker doesn't

**Technical**:
- Content similarity ≥ 80%
- Speaker similarity < 85%

**User-facing**:
- "Content Only - Possible Deepfake"
- Orange badge
- **Warning**: Could be AI-generated voice or voiceover

**Use cases this catches**:
- Deepfakes (AI-generated voice)
- Someone else reading the official's words
- Voice manipulation

---

### 3. `not_verified` ❌
**What it means**: Content not found in database

**Technical**:
- Content similarity < 80%

**User-facing**:
- "Not Verified"
- Red badge
- Clip doesn't match any official video

---

## File Structure

### New Backend Files

```
backend/
├── src/
│   ├── services/
│   │   └── ai-verification.service.ts  # NEW: AI service client
│   ├── routes/
│   │   ├── verification.ts             # NEW: Verification endpoints
│   │   └── ipfs.ts                     # UPDATED: AI integration
│   ├── config.ts                       # UPDATED: AI service URL
│   └── index.ts                        # UPDATED: Import routes
```

### New Frontend Files

```
frontend/
├── src/
│   └── services/
│       └── verification.service.ts     # NEW: Verification API client
```

### Shared Directory

```
ai-layer/
├── download/                           # Shared video directory
│   └── (official videos stored here)
├── transcription_cache/                # Cached transcriptions
├── uploads/                            # Temporary clip uploads
└── temp_audio/                         # Temporary audio files
```

---

## Setup Instructions

### 1. Install AI Service Dependencies

```bash
cd ai-layer
pip3.10 install -r requirements.txt
```

**Requirements**:
- Python 3.10+
- OpenAI API key
- ffmpeg

### 2. Set Environment Variables

**Backend `.env`**:
```env
PORT=3001
AI_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=sk-your-key-here
```

**AI Service**:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Start Services

**Terminal 1 - Python AI Service**:
```bash
cd ai-layer
python3.10 api_server.py
```

**Terminal 2 - Node.js Backend**:
```bash
cd backend
npm run dev
```

**Terminal 3 - React Frontend**:
```bash
cd frontend
npm run dev
```

### 4. Verify Setup

**Check AI service**:
```bash
curl http://localhost:8000/health
```

**Check backend integration**:
```bash
curl http://localhost:3001/api/verification/health
```

---

## Usage Examples

### Frontend: Verify a Clip

```typescript
import { verifyClip, getVerificationTypeBadge } from '@/services/verification.service';

async function handleVerify(clipFile: File) {
  try {
    const result = await verifyClip(clipFile);

    console.log('Verification type:', result.verification_type);

    if (result.best_match) {
      console.log('Matched video:', result.best_match.video_name);
      console.log('Timestamp:', result.best_match.start_time);
    }

    if (result.speaker_verification) {
      console.log('Speaker verified:', result.speaker_verification.verified);
    }

    // Get badge styling
    const badge = getVerificationTypeBadge(result.verification_type);
    console.log('Badge:', badge.label, badge.color);

  } catch (error) {
    console.error('Verification failed:', error);
  }
}
```

### Frontend: Upload Official Video

```typescript
async function handleOfficialUpload(videoFile: File, title: string) {
  const formData = new FormData();
  formData.append('video', videoFile);

  const response = await fetch(
    'http://localhost:3001/api/ipfs/upload?registerWithAI=true&title=' + encodeURIComponent(title),
    {
      method: 'POST',
      body: formData,
    }
  );

  const result = await response.json();
  console.log('Uploaded to IPFS:', result.cid);
  console.log('Registered with AI:', result.aiRegistered);
}
```

---

## API Reference

### Backend: Verification Endpoints

#### POST `/api/verification/verify-clip`
Verify a video clip

**Request**:
```
Content-Type: multipart/form-data
Body: { clip: File }
```

**Response**:
```json
{
  "success": true,
  "verification": {
    "verification_id": "uuid",
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
      "similarity": 0.96
    }
  }
}
```

#### GET `/api/verification/health`
Check AI service health

**Response**:
```json
{
  "success": true,
  "aiService": {
    "status": "healthy",
    "videos_available": 5
  },
  "backend": {
    "status": "healthy"
  }
}
```

#### GET `/api/verification/videos`
List all videos in AI database

**Response**:
```json
{
  "success": true,
  "videos": [
    {
      "video_name": "speech.mp4",
      "duration": 120.5,
      "word_count": 234,
      "cached": true
    }
  ],
  "count": 1
}
```

---

## Troubleshooting

### Issue: "AI service unavailable"

**Solution**:
```bash
# Check if Python service is running
curl http://localhost:8000/health

# If not, start it
cd ai-layer
python3.10 api_server.py
```

### Issue: "OpenAI API key required"

**Solution**:
```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> backend/.env
```

### Issue: "Video not found in AI database"

**Solution**:
```bash
# List videos in AI database
curl http://localhost:3001/api/verification/videos

# Videos should be in ai-layer/download/ directory
ls -la ai-layer/download/
```

### Issue: Verification taking too long

**Solution**:
```bash
# Preprocess videos to cache transcriptions
curl -X POST http://localhost:3001/api/verification/preprocess
```

---

## Performance Optimization

### 1. Pre-process Videos
Transcribe all official videos upfront:
```bash
curl -X POST http://localhost:3001/api/verification/preprocess
```

### 2. Monitor Cache
Cached transcriptions stored in `ai-layer/transcription_cache/`

### 3. Clear Cache (if needed)
```bash
curl -X DELETE http://localhost:3001/api/verification/cache
```

---

## Security Considerations

1. **API Key Protection**: Never expose OpenAI API key in frontend
2. **File Validation**: Backend validates file types and sizes
3. **Rate Limiting**: Consider adding rate limits to verification endpoint
4. **CORS**: Configure CORS properly for production
5. **Temp File Cleanup**: Backend automatically cleans up temporary files

---

## Next Steps

1. **Solana Integration**: Query on-chain video status after AI verification
2. **Database Schema**: Add verification_results table to cache results
3. **UI Components**: Build verification modal component
4. **Error Handling**: Add retry logic and better error messages
5. **Analytics**: Track verification success rates

---

## Support

For issues or questions:
1. Check AI service logs: Look at Python console output
2. Check backend logs: Look at Node.js console output
3. Check API docs: http://localhost:8000/docs (Python FastAPI auto-docs)

---

**Generated with Claude Code** 🤖
