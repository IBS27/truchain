// API Response Types

export interface UploadResponse {
  hash: number[];
  cid: string;
}

export interface SocialVideo {
  id: number;
  title: string;
  description: string | null;
  file_path: string;
  file_url: string;
  uploaded_at: string;
  verified_count: number;
  misleading_count: number;
  unverified_count: number;
  fake_count: number;
  dominant_tag: 'verified' | 'misleading' | 'unverified' | 'fake';
}

export interface FlagCounts {
  verified: number;
  misleading: number;
  unverified: number;
  fake: number;
}
