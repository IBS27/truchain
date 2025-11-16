#!/usr/bin/env python3
"""
FastAPI Backend for Video Verification V2
Provides REST API for clip verification with word-level timestamps.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
from pathlib import Path
import tempfile
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from word_transcription import WordTranscriber
from sliding_window_matcher import SlidingWindowMatcher, format_time
from speaker_verification import SpeakerVerifier

# Initialize FastAPI app
app = FastAPI(
    title="Video Verification API",
    description="Verify video clips using word-level timestamp matching",
    version="2.0.0"
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TEXT_THRESHOLD = 0.80  # 80% text similarity threshold
SPEAKER_THRESHOLD = 0.85  # 85% speaker similarity threshold
VIDEO_DIRECTORY = "download"
UPLOAD_DIRECTORY = "uploads"
Path(UPLOAD_DIRECTORY).mkdir(exist_ok=True)

# Initialize services
transcriber = WordTranscriber()
matcher = SlidingWindowMatcher(similarity_threshold=TEXT_THRESHOLD)
speaker_verifier = SpeakerVerifier()  # Initialize speaker verifier

# In-memory storage for verification results
verification_cache: Dict[str, Dict] = {}


# Pydantic models
class VerificationResult(BaseModel):
    """Verification result response model."""
    verification_id: str
    verified: bool
    verification_type: str  # "full", "content_only", "not_verified"
    clip_name: str
    matches: List[Dict]
    best_match: Optional[Dict]
    speaker_verification: Optional[Dict]
    clip_info: Dict
    timestamp: str
    text_threshold: float
    speaker_threshold: float


class VideoInfo(BaseModel):
    """Video information model."""
    video_name: str
    duration: float
    word_count: int
    cached: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    text_threshold: float
    speaker_threshold: float
    video_directory: str
    videos_available: int


# Helper functions
def cleanup_temp_file(file_path: str):
    """Clean up temporary file in background."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete temp file {file_path}: {e}")


def get_available_videos() -> List[Path]:
    """Get list of available videos in directory."""
    video_dir = Path(VIDEO_DIRECTORY)
    if not video_dir.exists():
        return []
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
    
    return video_files


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Video Verification API V2",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Returns system status and configuration.
    """
    videos = get_available_videos()
    
    return HealthResponse(
        status="healthy",
        text_threshold=TEXT_THRESHOLD,
        speaker_threshold=SPEAKER_THRESHOLD,
        video_directory=VIDEO_DIRECTORY,
        videos_available=len(videos)
    )


@app.get("/videos", response_model=List[VideoInfo], tags=["Videos"])
async def list_videos():
    """
    List all available videos in the database.
    Shows which videos are cached.
    """
    videos = get_available_videos()
    video_info_list = []
    
    for video_path in videos:
        cache_path = transcriber.get_cache_path(str(video_path))
        cached = cache_path.exists()
        
        # If cached, get info from cache
        if cached:
            try:
                transcription = transcriber.load_from_cache(str(video_path))
                video_info_list.append(VideoInfo(
                    video_name=video_path.name,
                    duration=transcription['duration'],
                    word_count=transcription['word_count'],
                    cached=True
                ))
            except:
                video_info_list.append(VideoInfo(
                    video_name=video_path.name,
                    duration=0.0,
                    word_count=0,
                    cached=False
                ))
        else:
            video_info_list.append(VideoInfo(
                video_name=video_path.name,
                duration=0.0,
                word_count=0,
                cached=False
            ))
    
    return video_info_list


@app.post("/verify", response_model=VerificationResult, tags=["Verification"])
async def verify_clip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Verify a video clip using HYBRID VERIFICATION (Content + Speaker).
    
    Two-stage verification process:
    1. Content Verification: Word-level text matching to find WHAT was said
    2. Speaker Verification: Audio embedding comparison to verify WHO said it
    
    Upload a video clip and get verification results including:
    - verification_type: "full" (both match), "content_only" (possible deepfake), or "not_verified"
    - Exact timestamp where content was found
    - Text similarity score
    - Speaker similarity score
    - Matched text
    
    Parameters:
    - file: Video clip file (mp4, avi, mov, etc.)
    
    Returns:
    - Hybrid verification result with content and speaker verification details
    """
    
    # Generate unique ID for this verification
    verification_id = str(uuid.uuid4())
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        # Create temp file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=UPLOAD_DIRECTORY) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # Step 1: Transcribe clip
        try:
            clip_transcription = transcriber.transcribe_clip(temp_file_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to transcribe clip: {str(e)}"
            )
        
        # Step 2: Get all videos
        video_files = get_available_videos()
        
        if not video_files:
            raise HTTPException(
                status_code=404,
                detail=f"No videos found in {VIDEO_DIRECTORY}"
            )
        
        # Step 3: Transcribe all videos (with caching)
        video_transcriptions = []
        for video_path in video_files:
            try:
                transcription = transcriber.transcribe_with_word_timestamps(str(video_path))
                video_transcriptions.append(transcription)
            except Exception as e:
                print(f"Warning: Failed to transcribe {video_path.name}: {e}")
                continue
        
        if not video_transcriptions:
            raise HTTPException(
                status_code=500,
                detail="Failed to transcribe any videos"
            )
        
        # Step 4: Search for matches
        matches = matcher.search_all_videos(clip_transcription, video_transcriptions)
        
        # Step 5: Speaker Verification (if content match found)
        speaker_verification = None
        verification_type = "not_verified"
        content_verified = len(matches) > 0
        best_match = matches[0] if matches else None
        
        if content_verified and best_match:
            # Perform speaker verification on the matched segment
            try:
                # Get matched timestamps
                original_video_path = f"{VIDEO_DIRECTORY}/{best_match['video_name']}"
                start_time = best_match['start_time']
                end_time = best_match['end_time']
                duration = end_time - start_time
                verify_duration = min(10.0, duration)  # Analyze up to 10 seconds
                
                # Verify speaker
                speaker_result = speaker_verifier.verify_speaker(
                    clip_path=temp_file_path,
                    clip_start=0,
                    clip_duration=verify_duration,
                    original_path=original_video_path,
                    original_start=start_time,
                    original_duration=verify_duration,
                    threshold=SPEAKER_THRESHOLD
                )
                
                speaker_verification = {
                    "verified": speaker_result['verified'],
                    "similarity": speaker_result['similarity'],
                    "threshold": speaker_result['threshold'],
                    "message": speaker_result['message']
                }
                
                # Determine final verification type
                if speaker_result['verified']:
                    verification_type = "full"  # Both content and speaker match
                else:
                    verification_type = "content_only"  # Content matches, speaker doesn't
                    
            except Exception as e:
                print(f"Warning: Speaker verification failed: {e}")
                speaker_verification = {
                    "verified": False,
                    "error": str(e),
                    "message": "Speaker verification failed"
                }
                verification_type = "content_only"
        
        # Final verification status
        fully_verified = (verification_type == "full")
        
        result = {
            "verification_id": verification_id,
            "verified": fully_verified,
            "verification_type": verification_type,
            "clip_name": file.filename,
            "matches": matches,
            "best_match": best_match,
            "speaker_verification": speaker_verification,
            "clip_info": {
                "word_count": clip_transcription['word_count'],
                "duration": clip_transcription['duration'],
                "text": clip_transcription['full_text']
            },
            "timestamp": datetime.now().isoformat(),
            "text_threshold": TEXT_THRESHOLD,
            "speaker_threshold": SPEAKER_THRESHOLD
        }
        
        # Cache result
        verification_cache[verification_id] = result
        
        # Schedule cleanup of temp file
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        return VerificationResult(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@app.get("/verify/{verification_id}", tags=["Verification"])
async def get_verification_result(verification_id: str):
    """
    Get cached verification result by ID.
    
    Parameters:
    - verification_id: Unique verification ID from previous verify request
    
    Returns:
    - Cached verification result
    """
    if verification_id not in verification_cache:
        raise HTTPException(
            status_code=404,
            detail=f"Verification result not found: {verification_id}"
        )
    
    return verification_cache[verification_id]


@app.post("/videos/add", tags=["Videos"])
async def add_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = None
):
    """
    Add a new video to the database.
    
    Uploads a video file, transcribes it with word-level timestamps,
    and adds it to the available videos for verification.
    
    Parameters:
    - file: Video file (mp4, avi, mov, etc.)
    - title: Optional custom title (defaults to filename)
    
    Returns:
    - Video information including transcription status
    """
    
    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    
    if suffix not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(valid_extensions)}"
        )
    
    # Use provided title or filename
    video_title = title or Path(file.filename).stem
    
    # Save video to VIDEO_DIRECTORY
    video_dir = Path(VIDEO_DIRECTORY)
    video_dir.mkdir(exist_ok=True)
    
    # Generate unique filename if already exists
    base_name = Path(file.filename).stem
    counter = 1
    video_path = video_dir / file.filename
    
    while video_path.exists():
        new_name = f"{base_name}_{counter}{suffix}"
        video_path = video_dir / new_name
        counter += 1
    
    try:
        # Save uploaded file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Transcribe in background
        def transcribe_video():
            """Background task to transcribe the video."""
            try:
                transcriber.transcribe_with_word_timestamps(str(video_path))
                print(f"✓ Successfully transcribed: {video_path.name}")
            except Exception as e:
                print(f"✗ Error transcribing {video_path.name}: {e}")
        
        background_tasks.add_task(transcribe_video)
        
        return {
            "status": "success",
            "message": f"Video uploaded and queued for transcription",
            "video_info": {
                "filename": video_path.name,
                "title": video_title,
                "path": str(video_path),
                "size_mb": video_path.stat().st_size / (1024 * 1024),
                "transcription_status": "processing"
            }
        }
        
    except Exception as e:
        # Clean up file on error
        if video_path.exists():
            video_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save video: {str(e)}"
        )


@app.delete("/videos/{video_name}", tags=["Videos"])
async def delete_video(video_name: str):
    """
    Delete a video from the database.
    
    Removes the video file and its cached transcription.
    
    Parameters:
    - video_name: Name of the video file to delete
    
    Returns:
    - Deletion status
    """
    video_path = Path(VIDEO_DIRECTORY) / video_name
    
    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Video not found: {video_name}"
        )
    
    try:
        # Delete video file
        video_path.unlink()
        
        # Delete cached transcription
        cache_path = transcriber.get_cache_path(str(video_path))
        if cache_path.exists():
            cache_path.unlink()
        
        return {
            "status": "success",
            "message": f"Deleted video: {video_name}",
            "deleted": {
                "video": str(video_path),
                "cache": str(cache_path) if cache_path.exists() else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}"
        )


@app.post("/preprocess", tags=["System"])
async def preprocess_videos(background_tasks: BackgroundTasks):
    """
    Pre-process all videos in the database.
    Transcribes all videos and caches them for faster verification.
    
    This is optional but recommended for faster verification times.
    Run this once when new videos are added to the database.
    
    Returns:
    - Status message
    """
    video_files = get_available_videos()
    
    if not video_files:
        raise HTTPException(
            status_code=404,
            detail=f"No videos found in {VIDEO_DIRECTORY}"
        )
    
    def process_all():
        """Background task to process all videos."""
        for video_path in video_files:
            try:
                transcriber.transcribe_with_word_timestamps(str(video_path))
            except Exception as e:
                print(f"Error processing {video_path.name}: {e}")
    
    # Run in background
    background_tasks.add_task(process_all)
    
    return {
        "status": "started",
        "message": f"Pre-processing {len(video_files)} videos in background",
        "videos": [v.name for v in video_files]
    }


@app.get("/cache/clear", tags=["System"])
async def clear_cache():
    """
    Clear all cached transcriptions.
    Forces re-transcription of all videos on next verification.
    
    Use this if videos have been updated or if you want to regenerate transcriptions.
    """
    cache_dir = transcriber.CACHE_DIR
    
    if not cache_dir.exists():
        return {
            "status": "success",
            "message": "Cache directory does not exist",
            "cleared": 0
        }
    
    cleared_count = 0
    for cache_file in cache_dir.glob("*.json"):
        try:
            cache_file.unlink()
            cleared_count += 1
        except Exception as e:
            print(f"Warning: Could not delete {cache_file}: {e}")
    
    return {
        "status": "success",
        "message": f"Cleared {cleared_count} cached transcription(s)",
        "cleared": cleared_count
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    print("="*80)
    print("VIDEO VERIFICATION API V2 - HYBRID VERIFICATION")
    print("="*80)
    print(f"\nText Threshold: {TEXT_THRESHOLD:.0%}")
    print(f"Speaker Threshold: {SPEAKER_THRESHOLD:.0%}")
    print(f"Video directory: {VIDEO_DIRECTORY}")
    print(f"Upload directory: {UPLOAD_DIRECTORY}")
    print("\nVerification Modes:")
    print("  • Full: Content + Speaker match")
    print("  • Content Only: Content matches, speaker doesn't (possible deepfake)")
    print("  • Not Verified: Content not found")
    print("\nStarting server...")
    print("API docs: http://localhost:8000/docs")
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

