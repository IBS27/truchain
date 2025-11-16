# V1 Hybrid System (Archived)

## ⚠️ Status: Archived

This folder contains the **V1 Hybrid Verification System** which has been superseded by the V2 Word-Level Timestamp system.

## What This Was

The V1 Hybrid system attempted to combine:
1. **Text transcription** (30-second segments) for content matching
2. **Audio embeddings** (Wav2Vec2) for speaker verification

## Why It Was Replaced

### Problems with V1 Hybrid:
- ❌ **Boundary alignment issues** - Fixed 30-second segments caused clips to be split across boundaries
- ❌ **False negatives** - Clips starting mid-segment had lower similarity scores
- ❌ **Required ≥30s clips** - Shorter clips didn't work well
- ❌ **~30s timestamp accuracy** - Not precise enough

## Files in This Folder

- `hybrid_verification.py` - Main verification system
- `README_HYBRID.md` - Original documentation
- `HYBRID_SETUP_GUIDE.md` - Setup instructions

## Migration to V2

If you need the functionality from this system, use **V2 instead**:

**V2 Location**: Root directory
- `verification_v2.py` - New verification system
- `README_V2.md` - Documentation

**V2 Improvements**:
- ✅ Word-level timestamps (no boundaries)
- ✅ Sub-second accuracy
- ✅ Works with any clip length
- ✅ No false negatives from boundaries

## Historical Reference

This system is kept for reference only. **Do not use for new projects.**

Use V2 instead: `python3.10 verification_v2.py <clip>`

