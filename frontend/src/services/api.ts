const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export interface UploadResponse {
  hash: number[];
  cid: string;
}

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
