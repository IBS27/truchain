# Audio Fingerprinting & Verification System

A robust audio fingerprinting system for verifying video clip authenticity. Built to detect if a video clip is an authentic excerpt from original campaign videos, even with quality degradation.

## 🎯 Overview

This system allows you to:
- Generate audio fingerprints from videos at 5-second intervals
- Store fingerprints in a JSON database (ready for blockchain integration)
- Verify if a user-submitted clip matches any stored videos
- Detect clips even with audio degradation (compression, quality reduction)
- Fast verification (< 5 seconds even for hours of video)

## ✅ Test Results

All tests passed successfully:
- ✓ **Process Video**: 659 fingerprints generated for 55-minute video
- ✓ **Exact Clip Detection**: 91.6% confidence, perfect timestamp match
- ✓ **Degraded Quality**: 93.4% confidence with lower bitrate/mono audio
- ✓ **No False Positives**: Correctly rejects modified clips
- ✓ **Performance**: 0.20s verification time

## 📁 Project Structure

```
truchain/
├── audio_fingerprint.py    # Core fingerprinting module
├── video_processor.py       # Process and store videos in database
├── verification.py          # Verify clips against database
├── test_system.py          # Comprehensive test suite
├── requirements.txt        # Python dependencies
├── video_database.json     # JSON database (created after processing videos)
└── download/               # Downloaded videos
```

## 🔧 Installation

### Prerequisites

```bash
# Install system dependencies
brew install chromaprint ffmpeg  # macOS
# or
sudo apt install libchromaprint-tools ffmpeg  # Linux
```

### Python Dependencies

```bash
pip3.10 install -r requirements.txt
```

Dependencies:
- `yt-dlp` - YouTube video downloader
- `pydub` - Audio manipulation
- `pyacoustid` - Chromaprint bindings
- `ffmpeg-python` - Video processing
- `numpy` - Numerical operations

## 🚀 Usage

### 1. Process Campaign Videos

Process a video and add its fingerprints to the database:

```bash
python3.10 video_processor.py path/to/video.mp4 --title "Campaign Speech" --campaign "2024"
```

Options:
- `--db <path>` - Database file path (default: `video_database.json`)
- `--title <title>` - Video title
- `--campaign <name>` - Campaign name
- `--ipfs <cid>` - IPFS Content ID (optional)

**Example:**
```bash
python3.10 video_processor.py download/fedspeech1.mp4 \
  --title "Federal Reserve Speech" \
  --campaign "Fed 2025"
```

### 2. View Database Statistics

```bash
python3.10 video_processor.py --stats
python3.10 video_processor.py --list
```

### 3. Verify a Clip

Check if a clip is from any stored video:

```bash
python3.10 verification.py path/to/clip.mp4
```

Options:
- `--db <path>` - Database file (default: `video_database.json`)
- `--threshold <float>` - Similarity threshold 0.0-1.0 (default: 0.85)
- `--min-matches <int>` - Minimum consecutive matches (default: 2)

**Example:**
```bash
python3.10 verification.py user_clip.mp4 --threshold 0.80
```

**Output:**
```
✓ MATCH FOUND! Found 1 match(es):

Match #1:
Match found in video 'Federal Reserve Speech' (ID: video_a4ed70563dfc95ef)
  Clip timestamp: 0.0s
  Original timestamp: 120.0s
  Confidence: 93.4%
  Matching fingerprints: 4
```

### 4. Generate Fingerprints Only

Generate fingerprints without adding to database:

```bash
python3.10 audio_fingerprint.py video.mp4 output.json
```

### 5. Run Tests

Test the entire system:

```bash
python3.10 test_system.py download/fedspeech1.mp4
```

## 🔬 How It Works

### Audio Fingerprinting

1. **Extract Audio**: Convert video to WAV format (44.1kHz, stereo)
2. **Generate Fingerprints**: Use chromaprint to create fingerprints at 5-second intervals
3. **Store Data**: Save fingerprint arrays + SHA256 hashes for each segment

### Verification Process

1. **Process Clip**: Generate fingerprints from user's clip
2. **Search Database**: Compare clip fingerprints against all stored videos
3. **Matching Algorithm**:
   - Calculate similarity using bit-wise XOR comparison
   - Find consecutive matching segments (default: 2+ consecutive matches)
   - Score based on average similarity across matched segments
4. **Return Results**: Match location, timestamp, and confidence score

### Similarity Calculation

Uses chromaprint's standard comparison method:
- XOR fingerprint integer arrays
- Count differing bits (Hamming distance)
- Calculate similarity: `1.0 - (different_bits / total_bits)`
- Typical scores: 85-95% for authentic clips

## 📊 Database Format

The JSON database structure is designed for easy blockchain migration:

```json
{
  "videos": [
    {
      "id": "video_a4ed70563dfc95ef",
      "ipfs_cid": "Qm43c8ec24106f98316cb921fff39986023eae47588ae8",
      "title": "Campaign Speech",
      "duration": 3297.49,
      "fingerprints": [
        {
          "timestamp": 0.0,
          "hash": "cd77ec9f3bc2c919a5b712ceb6e591de...",
          "fingerprint": [627964279, 627964279, ...]
        },
        ...
      ],
      "metadata": {
        "upload_date": "2025-11-15T...",
        "campaign": "2024",
        "filename": "video.mp4"
      }
    }
  ]
}
```

## 🔗 Blockchain Integration (Future)

The current JSON format maps directly to smart contract storage:

**Mapping:**
- `fingerprints` array → blockchain array storage
- Each `hash` → `bytes32` type in Solidity
- `fingerprint` array → can be compressed or stored off-chain
- `metadata` → contract state variables

**Example Solidity Structure:**
```solidity
struct Video {
    string ipfsCID;
    string title;
    uint256 duration;
    bytes32[] fingerprintHashes;  // 5-second interval hashes
    uint256 uploadDate;
    string campaign;
}

mapping(bytes32 => Video) public videos;  // videoId => Video
```

## ⚙️ Configuration

### Adjusting Fingerprint Interval

Edit `INTERVAL_SECONDS` in `audio_fingerprint.py`:

```python
INTERVAL_SECONDS = 5  # Change to 3, 10, etc.
```

**Trade-offs:**
- Smaller interval (3s): More precise, larger database, slower processing
- Larger interval (10s): Less precise, smaller database, faster processing
- Recommended: 5 seconds (good balance)

### Adjusting Match Threshold

More lenient matching for heavily degraded clips:

```bash
python3.10 verification.py clip.mp4 --threshold 0.75 --min-matches 3
```

**Thresholds:**
- `0.90+`: Very strict (exact copies only)
- `0.85`: Default (handles minor degradation)
- `0.80`: Moderate (handles re-encoding)
- `0.75`: Lenient (handles quality loss)
- `< 0.70`: Too lenient (may have false positives)

## 🎬 Use Cases

### Scenario A: Pure Clip Extraction
Creator downloads campaign video, cuts 20 seconds, posts it.
**Result**: ✅ Perfect detection with timestamp

### Scenario B: Reaction Video (Separate Audio)
Creator plays clip with original audio, then pauses to react.
**Result**: ✅ Detects segments with original audio

### Scenario C: Audio Overlay
Creator talks over the video (mixed audio).
**Result**: ⚠️ May not detect (audio signature altered)

### Scenario D: Screen Recording
User screen-records video playing on YouTube.
**Result**: ✅ Detects if audio quality preserved

## 📈 Performance

Tested with 55-minute video (fedspeech1.mp4):
- **Fingerprint Generation**: 7.08s (659 fingerprints)
- **Clip Verification**: 0.20s (against 1 video)
- **Scalability**: Linear O(n) search through database
- **Memory**: ~1KB per fingerprint in database

**For 100 hours of video:**
- Fingerprints: ~72,000 (at 5-second intervals)
- Database size: ~72MB
- Verification time: < 2 seconds (estimated)

## 🛠️ Troubleshooting

### "fpcalc not found"
```bash
brew install chromaprint  # macOS
sudo apt install libchromaprint-tools  # Linux
```

### "ffmpeg not found"
```bash
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux
```

### Low Match Confidence
- Try lowering threshold: `--threshold 0.80`
- Check if audio is heavily modified
- Ensure clip is from the same source

### No Matches Found
- Verify clip is actually from a stored video
- Try `--threshold 0.75` for degraded clips
- Check database with `--list` to see stored videos

## 🔐 Security Considerations

**For Blockchain Deployment:**
1. **IPFS CID Verification**: Always verify video is accessible via IPFS
2. **Fingerprint Immutability**: Store fingerprints on-chain for tamper-proof verification
3. **Timestamp Proof**: Include block timestamp for upload verification
4. **Access Control**: Consider who can add videos to the system

**Privacy:**
- Fingerprints don't reveal audio content (perceptual hash)
- Safe to store publicly on blockchain
- Original videos should be publicly accessible (campaign requirement)

## 📝 Next Steps

### For Blockchain Integration:
1. Design smart contract schema (see Blockchain Integration section)
2. Integrate Web3.py for contract interaction
3. Add IPFS pinning service integration (Pinata/Web3.Storage)
4. Build web interface for upload and verification
5. Add multi-signature for video additions
6. Implement batch fingerprint storage (gas optimization)

### For Enhanced Features:
1. Support for video fingerprinting (visual + audio)
2. Partial match detection (find 10s clip in 2-hour video)
3. Multi-language metadata support
4. API endpoint for verification service
5. Real-time streaming verification

## 📄 License

Open source - ready for campaign transparency initiatives.

## 🤝 Contributing

This system is designed for political campaign video verification. Suggestions for improvements:
- Submit issues for bugs or feature requests
- Optimize fingerprint storage for blockchain
- Improve matching algorithms
- Add more comprehensive tests

---

**Built for transparency in political campaigns. 🗳️**

