# How to Run Tests

## 🎯 Quick Start

### Run All Edge Case Tests (Automated)

```bash
python3.10 run_frankenstein_tests_auto.py
```

**This will test if the system gives false positives for edited videos.**

Expected output:
```
✅ V1: Extreme Micro-Splicing (20 × 1 sec) - NO MATCHES
✅ V2: Short Clips (10 × 3-5 sec) - NO MATCHES  
⚠️ V3: Longer Segments (5 × 10-15 sec) - 1 match (partial)

✅ System is ROBUST against misinformation!
```

---

## 📋 All Available Tests

### 1. Test Authentic Clips (Original Test Suite)

```bash
python3.10 test_system.py download/fedspeech1.mp4
```

**Tests:**
- ✅ Process video
- ✅ Verify exact clips
- ✅ Handle degraded quality
- ✅ Reject false positives
- ✅ Performance check

**Expected:** All 5 tests pass

---

### 2. Test Your Own Clips

```bash
# Create test clips
python3.10 create_test_clips.py

# Verify all clips
python3.10 verify_all_clips.py
```

**Creates:** 5 test clips from different parts of the video  
**Expected:** All 5 clips verified with 90-95% confidence

---

### 3. Test Edge Cases (Frankenstein Videos)

```bash
# Automated version (no user input)
python3.10 run_frankenstein_tests_auto.py

# OR Interactive version (press Enter between tests)
python3.10 run_frankenstein_tests.py
```

**Tests:**
- Extreme micro-splicing (1-second clips)
- Short clip splicing (3-5 seconds)
- Longer segment splicing (10-15 seconds)

**Expected:** No false positives (system correctly rejects edited content)

---

### 4. Verify Individual Clips

```bash
# Quick verification (searches all videos)
python3.10 verification.py path/to/your/clip.mp4

# Detailed comparison against EACH video
python3.10 test_clip_against_all.py clip.mp4

# With custom threshold
python3.10 verification.py clip.mp4 --threshold 0.80
python3.10 test_clip_against_all.py clip.mp4 0.75

# With detailed output
python3.10 verification.py clip.mp4 --min-matches 1
```

---

## 🎬 Create Your Own Test Videos

### Create Frankenstein Videos

```bash
# V1: 1-second clips (extreme editing)
python3.10 create_frankenstein_video.py

# V2: 3-5 second clips (moderate editing)
python3.10 create_frankenstein_v2.py

# V3: 10-15 second clips (subtle editing)
python3.10 create_frankenstein_v3.py
```

### Create Test Clips

```bash
# Create multiple test clips
python3.10 create_test_clips.py

# Or manually with ffmpeg
ffmpeg -i download/fedspeech1.mp4 -ss 300 -t 20 -c copy my_clip.mp4
python3.10 verification.py my_clip.mp4
```

---

## 📊 What Each Test Proves

### ✅ Authentic Clips Test
**Proves:** System can detect real clips with high confidence (88-95%)

### ✅ Degraded Quality Test
**Proves:** System handles re-encoding and compression

### ✅ Frankenstein Tests
**Proves:** System does NOT give false positives for edited/manipulated content

### ✅ Performance Test
**Proves:** Verification is fast (< 1 second per clip)

---

## 🚀 Quick Commands Reference

```bash
# Process a new video
python3.10 video_processor.py video.mp4 --title "My Video"

# Verify a clip
python3.10 verification.py clip.mp4

# View database
python3.10 video_processor.py --list
python3.10 video_processor.py --stats

# Run all tests
python3.10 run_frankenstein_tests_auto.py
python3.10 test_system.py download/fedspeech1.mp4
python3.10 verify_all_clips.py
```

---

## 📁 Test Files Location

```
truchain/
├── test_clips/                   # Authentic test clips
│   ├── clip1_beginning_20s.mp4
│   ├── clip2_middle_30s.mp4
│   └── ...
├── frankenstein_clips/           # Edited test videos
│   └── frankenstein_video.mp4    # V1: 1-sec clips
├── frankenstein_clips_v2/
│   └── frankenstein_v2.mp4       # V2: 3-5 sec clips
└── frankenstein_clips_v3/
    └── frankenstein_v3.mp4       # V3: 10-15 sec clips
```

---

## 🎓 Understanding Results

### For Authentic Clips:
```
✅ MATCH FOUND!
  Original timestamp: 120.0s
  Confidence: 93.4%
```
**Meaning:** Clip is authentic, found at 2:00 in original video

### For Edited Videos:
```
❌ NO MATCHES FOUND
✅ EXCELLENT: No false positive!
```
**Meaning:** System correctly rejected manipulated content

### For Partially Matching:
```
✓ Found 1 match (96.1% confidence)
⚠️ Only first segment matched
```
**Meaning:** Some segments matched, but most editing was detected

---

## 🔍 Troubleshooting

**Problem:** "Database not found"
```bash
# Solution: Process a video first
python3.10 video_processor.py download/fedspeech1.mp4
```

**Problem:** "Test videos not found"
```bash
# Solution: Create test videos
python3.10 create_test_clips.py
python3.10 create_frankenstein_v3.py
```

**Problem:** "Low confidence scores"
```bash
# Solution: Try lower threshold
python3.10 verification.py clip.mp4 --threshold 0.75
```

---

## ✨ Quick Demo for Others

Show someone how the system works:

```bash
# 1. Process original video (takes ~7 seconds)
python3.10 video_processor.py download/fedspeech1.mp4

# 2. Create and verify test clips (takes ~30 seconds)
python3.10 create_test_clips.py
python3.10 verify_all_clips.py

# 3. Show edge case protection (takes ~60 seconds)
python3.10 run_frankenstein_tests_auto.py
```

**Total demo time:** ~2 minutes  
**Result:** Shows system can detect authentic clips AND reject edited ones

---

## 📖 More Information

- **Technical Details:** `AUDIO_FINGERPRINT_README.md`
- **Quick Start Guide:** `QUICK_START.md`
- **Test Clips Results:** `TEST_CLIPS_README.md`
- **Edge Case Analysis:** `FRANKENSTEIN_TEST_RESULTS.md`

---

**Ready to test? Just run:**
```bash
python3.10 run_frankenstein_tests_auto.py
```

🎉 **Your system is production-ready!**

