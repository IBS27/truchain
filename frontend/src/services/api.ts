import type {
  UploadResponse,
  SocialVideo,
  FlagCounts,
  AIVerificationResult,
  AIVideoInfo,
  AIHealthResponse
} from './types';

// Re-export types for convenience
export type {
  UploadResponse,
  SocialVideo,
  FlagCounts,
  AIVerificationResult,
  AIVideoInfo,
  AIHealthResponse
};

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

/**
 * Upload video file to backend
 * Returns hash and IPFS CID
 */
export async function uploadVideo(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('video', file);

  const response = await fetch(`${BACKEND_URL}/api/ipfs/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to upload video');
  }

  return await response.json();
}

/**
 * Get IPFS download URL for a CID
 */
export function getIPFSDownloadUrl(cid: string): string {
  return `${BACKEND_URL}/api/ipfs/download/${cid}`;
}

// Social Video API

export const socialApi = {
  async getAllVideos(): Promise<SocialVideo[]> {
    const response = await fetch(`${BACKEND_URL}/api/social/videos`);
    if (!response.ok) throw new Error('Failed to fetch videos');
    return response.json();
  },

  async uploadVideo(file: File, title: string, description?: string): Promise<SocialVideo> {
    const formData = new FormData();
    formData.append('video', file);
    formData.append('title', title);
    if (description) formData.append('description', description);

    const response = await fetch(`${BACKEND_URL}/api/social/videos/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Failed to upload video');
    return response.json();
  },

  async flagVideo(videoId: number, flagType: 'verified' | 'misleading' | 'unverified' | 'fake'): Promise<{ video: SocialVideo; flagCounts: FlagCounts }> {
    // Get or create a unique user ID for this browser
    let userId = localStorage.getItem('truchain_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
      localStorage.setItem('truchain_user_id', userId);
    }

    const response = await fetch(`${BACKEND_URL}/api/social/videos/${videoId}/flag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ flagType, userId }),
    });

    if (!response.ok) throw new Error('Failed to flag video');
    return response.json();
  },

  async getFlagCounts(videoId: number): Promise<FlagCounts> {
    const response = await fetch(`${BACKEND_URL}/api/social/videos/${videoId}/flags`);
    if (!response.ok) throw new Error('Failed to get flag counts');
    return response.json();
  },
};

// AI Verification API

export const verificationApi = {
  /**
   * Verify a video clip against official videos using AI
   */
  async verifyClip(file: File): Promise<AIVerificationResult> {
    const formData = new FormData();
    formData.append('clip', file);

    const response = await fetch(`${BACKEND_URL}/api/verification/verify-clip`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to verify clip');
    }

    const data = await response.json();
    return data.verification;
  },

  /**
   * Get cached verification result by ID
   */
  async getVerificationResult(verificationId: string): Promise<AIVerificationResult> {
    const response = await fetch(`${BACKEND_URL}/api/verification/result/${verificationId}`);

    if (!response.ok) {
      throw new Error('Failed to get verification result');
    }

    const data = await response.json();
    return data.verification;
  },

  /**
   * List all videos available in AI service
   */
  async listVideos(): Promise<AIVideoInfo[]> {
    const response = await fetch(`${BACKEND_URL}/api/verification/videos`);

    if (!response.ok) {
      throw new Error('Failed to list AI videos');
    }

    const data = await response.json();
    return data.videos;
  },

  /**
   * Check AI service health
   */
  async checkHealth(): Promise<AIHealthResponse> {
    const response = await fetch(`${BACKEND_URL}/api/verification/health`);

    if (!response.ok) {
      throw new Error('AI service unavailable');
    }

    const data = await response.json();
    return data.aiService;
  },
};

/**
 * Upload official video and register with AI service
 */
export async function uploadOfficialVideo(file: File, title?: string): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('video', file);
  if (title) {
    formData.append('title', title);
  }

  const response = await fetch(`${BACKEND_URL}/api/ipfs/upload?registerWithAI=true`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to upload video');
  }

  return await response.json();
}
