# 🚀 Video Verification API V2 - Documentation

## FastAPI Backend with 80% Threshold

A REST API for verifying video clips using word-level timestamp matching.

---

## 🎯 Quick Start

### 1. Install Dependencies

```bash
pip3.10 install fastapi uvicorn python-multipart
```

### 2. Set API Key

```bash
export OPENAI_API_KEY='your-openai-key-here'
```

### 3. Start Server

```bash
python3.10 api_server.py
```

Server starts at: **http://localhost:8000**

### 4. View Interactive Docs

Open in browser: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### **GET** `/`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Video Verification API V2",
  "version": "2.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### **GET** `/health`
Health check and system status.

**Response:**
```json
{
  "status": "healthy",
  "threshold": 0.80,
  "video_directory": "download",
  "videos_available": 4
}
```

---

### **GET** `/videos`
List all available videos and their cache status.

**Response:**
```json
[
  {
    "video_name": "fedspeech1.mp4",
    "duration": 3297.5,
    "word_count": 5842,
    "cached": true
  },
  {
    "video_name": "fedspeech2.mp4",
    "duration": 3290.2,
    "word_count": 5801,
    "cached": true
  }
]
```

---

### **POST** `/verify`
**Main endpoint**: Verify a video clip.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file`: Video clip file (mp4, avi, mov, etc.)

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/verify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_clip.mp4"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/verify"
files = {"file": open("test_clip.mp4", "rb")}
response = requests.post(url, files=files)
result = response.json()

if result['verified']:
    print(f"✓ Verified in {result['best_match']['video_name']}")
    print(f"  Timestamp: {result['best_match']['start_time']:.1f}s")
    print(f"  Similarity: {result['best_match']['similarity']:.1%}")
else:
    print("✗ Not verified")
```

**Response (Success):**
```json
{
  "verification_id": "550e8400-e29b-41d4-a716-446655440000",
  "verified": true,
  "clip_name": "test_clip.mp4",
  "matches": [
    {
      "video_path": "/path/to/fedspeech1.mp4",
      "video_name": "fedspeech1.mp4",
      "start_time": 120.3,
      "end_time": 135.7,
      "similarity": 0.968,
      "start_word_index": 1234,
      "end_word_index": 1258,
      "matched_text": "the federal reserve has decided...",
      "clip_word_count": 47,
      "duration": 15.4
    }
  ],
  "best_match": {
    "video_name": "fedspeech1.mp4",
    "start_time": 120.3,
    "end_time": 135.7,
    "similarity": 0.968,
    "duration": 15.4
  },
  "clip_info": {
    "word_count": 47,
    "duration": 20.5,
    "text": "The Federal Reserve has decided to maintain..."
  },
  "timestamp": "2024-01-15T10:30:45.123456",
  "threshold": 0.80
}
```

**Response (No Match):**
```json
{
  "verification_id": "550e8400-e29b-41d4-a716-446655440000",
  "verified": false,
  "clip_name": "test_clip.mp4",
  "matches": [],
  "best_match": null,
  "clip_info": {
    "word_count": 47,
    "duration": 20.5,
    "text": "Some completely different content..."
  },
  "timestamp": "2024-01-15T10:30:45.123456",
  "threshold": 0.80
}
```

---

### **GET** `/verify/{verification_id}`
Get cached verification result by ID.

**Parameters:**
- `verification_id`: UUID from previous verify request

**Response:**
Same as `/verify` POST response.

---

### **POST** `/preprocess`
Pre-process all videos (transcribe and cache).

**Use case**: Run this once when adding new videos to speed up future verifications.

**Response:**
```json
{
  "status": "started",
  "message": "Pre-processing 4 videos in background",
  "videos": [
    "fedspeech1.mp4",
    "fedspeech2.mp4",
    "fedspeech3.mp4",
    "fedspeechdifferent.mp4"
  ]
}
```

---

### **GET** `/cache/clear`
Clear all cached transcriptions.

**Response:**
```json
{
  "status": "success",
  "message": "Cleared 4 cached transcription(s)",
  "cleared": 4
}
```

---

## 🔧 Configuration

Edit `api_server.py` to change settings:

```python
THRESHOLD = 0.80  # 80% similarity threshold
VIDEO_DIRECTORY = "download"  # Directory with original videos
UPLOAD_DIRECTORY = "uploads"  # Temporary upload directory
```

---

## 📊 Response Fields Explained

### `verified` (boolean)
- `true`: Clip matches at least one video above threshold
- `false`: No matches found

### `similarity` (float)
- Range: 0.0 to 1.0 (0% to 100%)
- Threshold: 0.80 (80%)
- Example: `0.968` = 96.8% match

### `start_time` / `end_time` (float)
- Exact timestamp in seconds where clip was found
- Sub-second accuracy
- Example: `120.3` = 2 minutes 0.3 seconds

### `matched_text` (string)
- The actual text that matched from the original video
- Normalized (lowercase, no punctuation)

---

## 🧪 Testing the API

### Test 1: Using cURL

```bash
# Create a test clip
ffmpeg -i download/fedspeech1.mp4 -ss 120 -t 15 -y test_clip.mp4

# Verify it
curl -X POST "http://localhost:8000/verify" \
  -F "file=@test_clip.mp4"
```

### Test 2: Using Python

```python
import requests

# Verify clip
url = "http://localhost:8000/verify"
with open("test_clip.mp4", "rb") as f:
    response = requests.post(url, files={"file": f})

result = response.json()
print(f"Verified: {result['verified']}")
if result['verified']:
    match = result['best_match']
    print(f"Found in: {match['video_name']}")
    print(f"At: {match['start_time']:.1f}s - {match['end_time']:.1f}s")
    print(f"Similarity: {match['similarity']:.1%}")
```

### Test 3: Using httpie

```bash
# Install httpie
pip install httpie

# Verify clip
http -f POST http://localhost:8000/verify file@test_clip.mp4
```

---

## 🌐 Frontend Integration

### JavaScript/Fetch Example

```javascript
async function verifyClip(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/verify', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.verified) {
    console.log(`✓ Verified in ${result.best_match.video_name}`);
    console.log(`  At ${result.best_match.start_time}s`);
    console.log(`  Similarity: ${(result.best_match.similarity * 100).toFixed(1)}%`);
  } else {
    console.log('✗ Not verified');
  }
  
  return result;
}

// Usage
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const result = await verifyClip(file);
});
```

### React Example

```jsx
import { useState } from 'react';

function VideoVerifier() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/verify', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <input type="file" onChange={handleVerify} accept="video/*" />
      
      {loading && <p>Verifying...</p>}
      
      {result && result.verified && (
        <div className="success">
          <h3>✓ Verified!</h3>
          <p>Found in: {result.best_match.video_name}</p>
          <p>Timestamp: {result.best_match.start_time}s - {result.best_match.end_time}s</p>
          <p>Similarity: {(result.best_match.similarity * 100).toFixed(1)}%</p>
        </div>
      )}
      
      {result && !result.verified && (
        <div className="error">
          <h3>✗ Not Verified</h3>
          <p>This clip does not match any video in the database.</p>
        </div>
      )}
    </div>
  );
}
```

---

## ⚡ Performance

### First Verification (No Cache)
```
1. Upload clip (20 seconds)       → ~1 second
2. Transcribe clip                → ~3 seconds
3. Load/transcribe videos (×4)    → ~15 seconds (first time only)
4. Search                         → ~2 seconds
Total: ~21 seconds
```

### Subsequent Verifications (With Cache)
```
1. Upload clip (20 seconds)       → ~1 second
2. Transcribe clip                → ~3 seconds
3. Load cached videos (×4)        → Instant
4. Search                         → ~2 seconds
Total: ~6 seconds
```

**Tip**: Use `/preprocess` endpoint to pre-cache all videos!

---

## 🔒 Security Considerations

### Current Setup (Development)
- ✅ CORS enabled for all origins
- ✅ File upload size limited by server config
- ⚠️ No authentication
- ⚠️ No rate limiting

### Production Recommendations

1. **Add Authentication:**
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/verify")
async def verify_clip(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    file: UploadFile = File(...)
):
    # Verify token
    # ...
```

2. **Add Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/verify")
@limiter.limit("5/minute")
async def verify_clip(...):
    # ...
```

3. **Restrict CORS:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

4. **Add File Size Limits:**
```python
from fastapi import File, UploadFile
from fastapi.exceptions import RequestValidationError

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

@app.post("/verify")
async def verify_clip(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    # ...
```

---

## 🐛 Error Handling

### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Failed to transcribe clip: Invalid audio format"
}
```

**404 Not Found:**
```json
{
  "detail": "No videos found in download"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Verification failed: Connection error"
}
```

---

## 📝 Environment Variables

```bash
# Required
export OPENAI_API_KEY='sk-proj-...'

# Optional (defaults shown)
export VIDEO_DIRECTORY='download'
export UPLOAD_DIRECTORY='uploads'
export API_THRESHOLD='0.80'
```

---

## 🚀 Deployment

### Development Server

```bash
python3.10 api_server.py
```

### Production Server (Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=""

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 💡 Tips & Best Practices

1. **Pre-process videos**: Run `/preprocess` once when starting the server
2. **Monitor uploads**: Set up file size limits to prevent abuse
3. **Cache management**: Clear cache when videos are updated
4. **Error logging**: Monitor logs for transcription failures
5. **Health checks**: Use `/health` endpoint for monitoring

---

## 📊 Metrics & Monitoring

Track these metrics:
- Verification count
- Average verification time
- Success rate (verified vs not verified)
- Cache hit rate
- API response times

Example logging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/verify")
async def verify_clip(...):
    logger.info(f"Verification request: {file.filename}")
    # ... verification logic
    logger.info(f"Result: verified={result['verified']}, time={elapsed}s")
```

---

## 🎉 Ready to Use!

Your API is ready at **http://localhost:8000**

**Interactive docs**: http://localhost:8000/docs
**Alternative docs**: http://localhost:8000/redoc

Test it now:
```bash
curl -X POST "http://localhost:8000/verify" -F "file=@test_clip.mp4"
```

