# 🚀 API Quick Start Guide

## FastAPI Backend - Ready in 3 Steps!

---

## ⚡ Start the Server

```bash
# 1. Set your API key
export OPENAI_API_KEY='your-key-here'

# 2. Start the server
cd /Users/muhammedcikmaz/Projects/truchain
python3.10 api_server.py
```

**Server running at**: http://localhost:8000

**Interactive docs**: http://localhost:8000/docs

---

## 🧪 Test It Immediately

### Option 1: Using the Web Interface

1. Open http://localhost:8000/docs
2. Click on **POST /verify**
3. Click **"Try it out"**
4. Click **"Choose File"** and select your clip
5. Click **"Execute"**
6. See results below!

### Option 2: Using cURL

```bash
# Create a test clip
ffmpeg -i download/fedspeech1.mp4 -ss 120 -t 15 -y test_clip.mp4

# Verify it
curl -X POST "http://localhost:8000/verify" \
  -F "file=@test_clip.mp4" | jq
```

### Option 3: Using Python

```python
import requests

url = "http://localhost:8000/verify"
files = {"file": open("test_clip.mp4", "rb")}
response = requests.post(url, files=files)
result = response.json()

if result['verified']:
    print(f"✓ Found in {result['best_match']['video_name']}")
    print(f"  At {result['best_match']['start_time']:.1f}s")
    print(f"  Similarity: {result['best_match']['similarity']:.1%}")
else:
    print("✗ Not verified")
```

---

## 📡 Main Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/docs` | GET | Interactive API documentation |
| `/health` | GET | Check if server is running |
| `/verify` | POST | **Main endpoint** - verify a clip |
| `/videos` | GET | List available videos |
| `/preprocess` | POST | Pre-cache all videos (optional) |

---

## ✅ Expected Response

When you verify a clip, you'll get:

```json
{
  "verified": true,
  "best_match": {
    "video_name": "fedspeech1.mp4",
    "start_time": 120.3,
    "end_time": 135.7,
    "similarity": 0.968
  }
}
```

- **verified**: `true` if found, `false` if not
- **start_time**: Exact second where clip starts
- **similarity**: 0.80 to 1.0 (threshold is 0.80 = 80%)

---

## ⚙️ Configuration

**Threshold**: 80% (0.80)
**Video directory**: `download/`
**Upload directory**: `uploads/`

To change threshold, edit line 38 in `api_server.py`:
```python
THRESHOLD = 0.80  # Change this value
```

---

## 💡 Pro Tips

### 1. Pre-process Videos (Faster Verification)

```bash
# Pre-transcribe all videos once
curl -X POST "http://localhost:8000/preprocess"
```

This transcribes all videos and caches them. Future verifications will be **much faster** (~3-6 seconds instead of ~20 seconds).

### 2. Check What Videos Are Available

```bash
curl "http://localhost:8000/videos" | jq
```

Shows which videos are in the database and which are cached.

### 3. Clear Cache (If Videos Updated)

```bash
curl "http://localhost:8000/cache/clear"
```

---

## 🌐 Frontend Example (HTML)

Create `test_frontend.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Video Verifier</title>
</head>
<body>
    <h1>Video Clip Verification</h1>
    
    <input type="file" id="fileInput" accept="video/*">
    <button onclick="verify()">Verify</button>
    
    <div id="result"></div>
    
    <script>
        async function verify() {
            const file = document.getElementById('fileInput').files[0];
            if (!file) return alert('Please select a file');
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('result').innerHTML = 'Verifying...';
            
            const response = await fetch('http://localhost:8000/verify', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.verified) {
                document.getElementById('result').innerHTML = `
                    <h2 style="color: green;">✓ Verified!</h2>
                    <p>Found in: ${result.best_match.video_name}</p>
                    <p>Timestamp: ${result.best_match.start_time.toFixed(1)}s - ${result.best_match.end_time.toFixed(1)}s</p>
                    <p>Similarity: ${(result.best_match.similarity * 100).toFixed(1)}%</p>
                `;
            } else {
                document.getElementById('result').innerHTML = `
                    <h2 style="color: red;">✗ Not Verified</h2>
                    <p>This clip does not match any video in the database.</p>
                `;
            }
        }
    </script>
</body>
</html>
```

---

## 🐛 Troubleshooting

### "Connection refused"
→ Make sure server is running: `python3.10 api_server.py`

### "OPENAI_API_KEY not set"
→ Set it: `export OPENAI_API_KEY='your-key'`

### Slow first verification
→ This is normal! First time transcribes all videos (~20 min for 4 hours of video)
→ Use `/preprocess` to do this in background once

### No videos found
→ Make sure videos are in `download/` directory

---

## 📊 Performance

**First verification** (no cache): ~20-30 seconds
**After caching**: ~3-8 seconds
**With preprocessing**: ~3-6 seconds

---

## 🎉 You're Ready!

Server is running at: **http://localhost:8000**

Try the interactive docs: **http://localhost:8000/docs**

Upload a clip and see it verified in real-time! 🚀

---

## 📖 Full Documentation

See `API_DOCUMENTATION.md` for complete API reference, examples, and deployment guide.

