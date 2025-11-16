// API Response Types

export interface UploadResponse {
  hash: number[];
  cid: string;
  aiRegistered?: boolean;
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

// AI Verification Types

export interface AIVerificationResult {
  verification_id: string;
  verified: boolean;
  verification_type: 'full' | 'content_only' | 'not_verified';
  clip_name: string;
  matches: AIMatch[];
  best_match?: AIMatch;
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

export interface AIMatch {
  video_path: string;
  video_name: string;
  start_time: number;
  end_time: number;
  similarity: number;
  matched_text: string;
  start_word_index?: number;
  end_word_index?: number;
  clip_word_count?: number;
  duration?: number;
}

export interface SpeakerVerification {
  verified: boolean;
  similarity: number;
  threshold: number;
  message: string;
}

export interface AIVideoInfo {
  video_name: string;
  duration: number;
  word_count: number;
  cached: boolean;
}

export interface AIHealthResponse {
  status: string;
  text_threshold: number;
  speaker_threshold: number;
  video_directory: string;
  videos_available: number;
}
