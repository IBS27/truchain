/**
 * Verification Service
 * Frontend service for video clip verification
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

/**
 * Types for verification responses
 */
export interface VerificationMatch {
  video_path: string;
  video_name: string;
  start_time: number;
  end_time: number;
  similarity: number;
  matched_text: string;
}

export interface SpeakerVerification {
  verified: boolean;
  similarity: number;
  threshold: number;
  message: string;
}

export interface VerificationResult {
  verification_id: string;
  verified: boolean;
  verification_type: 'full' | 'content_only' | 'not_verified';
  clip_name: string;
  matches: VerificationMatch[];
  best_match?: VerificationMatch;
  speaker_verification?: SpeakerVerification;
  clip_info: {
    word_count: number;
    duration: number;
    text: string;
  };
  timestamp: string;
  text_threshold: number;
  speaker_threshold: number;
}

export interface VerificationResponse {
  success: boolean;
  verification: VerificationResult;
}

export interface AIVideoInfo {
  video_name: string;
  duration: number;
  word_count: number;
  cached: boolean;
}

export interface VerificationHealthResponse {
  success: boolean;
  aiService: {
    status: string;
    text_threshold: number;
    speaker_threshold: number;
    video_directory: string;
    videos_available: number;
  };
  backend: {
    status: string;
    timestamp: string;
  };
}

/**
 * Verify a video clip against official videos
 * Returns hybrid verification result (content + speaker)
 *
 * @param clipFile - Video clip file to verify
 * @returns Verification result
 */
export async function verifyClip(clipFile: File): Promise<VerificationResult> {
  const formData = new FormData();
  formData.append('clip', clipFile);

  const response = await fetch(`${API_BASE_URL}/api/verification/verify-clip`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Verification failed');
  }

  const data: VerificationResponse = await response.json();
  return data.verification;
}

/**
 * Get cached verification result by ID
 *
 * @param verificationId - Verification ID
 * @returns Cached verification result
 */
export async function getVerificationResult(
  verificationId: string
): Promise<VerificationResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/verification/result/${verificationId}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to get verification result');
  }

  const data: VerificationResponse = await response.json();
  return data.verification;
}

/**
 * List all videos available in the AI verification database
 *
 * @returns List of videos
 */
export async function listVerificationVideos(): Promise<AIVideoInfo[]> {
  const response = await fetch(`${API_BASE_URL}/api/verification/videos`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to list videos');
  }

  const data = await response.json();
  return data.videos;
}

/**
 * Trigger preprocessing of all videos in the database
 * This transcribes all videos and caches them for faster verification
 */
export async function preprocessVideos(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/verification/preprocess`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to start preprocessing');
  }
}

/**
 * Clear the AI service's transcription cache
 */
export async function clearVerificationCache(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/verification/cache`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to clear cache');
  }
}

/**
 * Check verification service health status
 *
 * @returns Health status
 */
export async function checkVerificationHealth(): Promise<VerificationHealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/verification/health`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Health check failed');
  }

  return response.json();
}

/**
 * Format timestamp in seconds to MM:SS format
 *
 * @param seconds - Time in seconds
 * @returns Formatted time string (MM:SS)
 */
export function formatTimestamp(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Get verification type badge color
 *
 * @param verificationType - Type of verification
 * @returns CSS color class or color value
 */
export function getVerificationTypeBadge(
  verificationType: 'full' | 'content_only' | 'not_verified'
): { label: string; color: string; description: string } {
  switch (verificationType) {
    case 'full':
      return {
        label: 'Verified',
        color: 'green',
        description: 'Content and speaker both verified - Authentic clip',
      };
    case 'content_only':
      return {
        label: 'Content Only',
        color: 'orange',
        description:
          'Content matches but speaker does not - Possible deepfake or voiceover',
      };
    case 'not_verified':
      return {
        label: 'Not Verified',
        color: 'red',
        description: 'Content not found in database of official videos',
      };
  }
}

/**
 * Get similarity percentage as formatted string
 *
 * @param similarity - Similarity score (0.0 to 1.0)
 * @returns Formatted percentage string
 */
export function formatSimilarity(similarity: number): string {
  return `${(similarity * 100).toFixed(1)}%`;
}
