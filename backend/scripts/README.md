# Backend Scripts

## AI Video Backfill Script

### Purpose

This script synchronizes all videos from IPFS storage to the AI service directory and registers them for verification.

### When to Use

- **Initial AI service setup**: When first deploying the AI service
- **After clearing AI directory**: If the `ai-layer/download/` directory gets cleared
- **Recovery**: If the AI service database is corrupted or reset
- **New deployment**: When deploying to a new environment

### Prerequisites

1. AI service must be running:
   ```bash
   cd ai-layer
   ./start_ai_service.sh
   ```

2. Backend must have videos in IPFS storage (`backend/uploads/ipfs-mock/`)

### Usage

```bash
cd backend
npm run backfill-ai
```

### What It Does

1. ✅ Checks AI service health
2. 📁 Ensures AI download directory exists
3. 📹 Scans IPFS storage for all videos
4. 📋 Copies each video to `ai-layer/download/`
5. 🔄 Registers each video with AI service (triggers transcription)
6. 📊 Provides detailed summary

### Output Example

```
═══════════════════════════════════════════════════════
🔄 AI Video Backfill Script
═══════════════════════════════════════════════════════

1️⃣  Checking AI service health...
   ✅ AI service is healthy
   📊 Videos in AI database: 0

2️⃣  Ensuring AI directory exists...
   ✅ AI directory ready: /path/to/ai-layer/download

3️⃣  Scanning IPFS storage...
   📹 Found 3 video(s) in IPFS

4️⃣  Copying videos to AI directory and registering...

📹 [1/3] Processing: video1.mp4
   CID: Qm123...
   Size: 15.23 MB
   ✅ Copied: Qm123.mp4
   🔄 Registering with AI service...
   ✅ Registered and transcribed

...

═══════════════════════════════════════════════════════
📊 Backfill Summary
═══════════════════════════════════════════════════════
✅ Successfully processed: 3
⏭️  Already existed: 0
❌ Errors: 0
📹 Total videos: 3

5️⃣  Final AI service status...
   ✅ Videos now in AI database: 3

✨ Backfill complete!
```

### Notes

- **Idempotent**: Safe to run multiple times - skips already processed videos
- **Transcription**: Videos are automatically transcribed by the AI service (uses OpenAI Whisper)
- **Time**: Processing time depends on video length and count
- **Errors**: If any video fails, the script continues with remaining videos

### Troubleshooting

**AI service not available:**
```
❌ AI service is not available!
Error: connect ECONNREFUSED 127.0.0.1:8000

💡 Make sure the AI service is running:
   cd ai-layer && ./start_ai_service.sh
```

**No videos found:**
```
⚠️  IPFS mock directory not found. No videos to backfill.
```
This means no videos have been uploaded yet. Upload videos through the frontend first.

**Out of memory during transcription:**
If you have many/large videos, the AI service may run out of memory. Process in batches by temporarily moving some videos out of the IPFS directory.
