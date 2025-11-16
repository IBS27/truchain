import axios, { AxiosError } from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import { downloadFromIPFS } from './ipfs.service';
const FormData = require('form-data');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';
const AI_VIDEO_DIR = path.join(__dirname, '../../ai-layer/download');

/**
 * Types for AI verification responses
 */
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

/**
 * AI Verification Service
 * Communicates with the Python AI service for video verification
 */
export class AIVerificationService {

  /**
   * Check if AI service is healthy and accessible
   */
  static async checkHealth(): Promise<AIHealthResponse> {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/health`, {
        timeout: 5000,
      });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(`AI service health check failed: ${error.message}`);
      }
      throw new Error('AI service health check failed: Unknown error');
    }
  }

  /**
   * List all videos available in the AI service database
   */
  static async listVideos(): Promise<AIVideoInfo[]> {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/videos`);
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(`Failed to list AI videos: ${error.message}`);
      }
      throw new Error('Failed to list AI videos: Unknown error');
    }
  }

  /**
   * Register an official video with the AI service
   * This transcribes the video and caches it for future verification
   *
   * @param videoPath - Local path to the video file
   * @param title - Title/name for the video (optional)
   */
  static async registerOfficialVideo(
    videoPath: string,
    title?: string
  ): Promise<void> {
    try {
      if (!fs.existsSync(videoPath)) {
        throw new Error(`Video file not found: ${videoPath}`);
      }

      const form = new FormData();
      form.append('file', fs.createReadStream(videoPath));
      if (title) {
        form.append('title', title);
      }

      await axios.post(`${AI_SERVICE_URL}/videos/add`, form, {
        headers: form.getHeaders(),
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
      });

      console.log(`✓ Registered video with AI service: ${path.basename(videoPath)}`);
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(`Failed to register video with AI service: ${error.message}`);
      }
      throw new Error('Failed to register video with AI service: Unknown error');
    }
  }

  /**
   * Verify a clip against the database of official videos
   * Returns hybrid verification result (content + speaker)
   *
   * @param clipPath - Local path to the clip file
   */
  static async verifyClip(clipPath: string): Promise<AIVerificationResult> {
    try {
      if (!fs.existsSync(clipPath)) {
        throw new Error(`Clip file not found: ${clipPath}`);
      }

      const form = new FormData();
      form.append('file', fs.createReadStream(clipPath));

      const response = await axios.post(`${AI_SERVICE_URL}/verify`, form, {
        headers: form.getHeaders(),
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        timeout: 120000, // 2 minutes timeout for verification
      });

      console.log(`✓ Verified clip: ${path.basename(clipPath)}`);
      console.log(`  Verification type: ${response.data.verification_type}`);
      if (response.data.best_match) {
        console.log(`  Best match: ${response.data.best_match.video_name} (${response.data.best_match.similarity.toFixed(2)})`);
      }

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.code === 'ECONNREFUSED') {
          throw new Error('AI service is not running. Please start the Python AI service on port 8000.');
        }
        throw new Error(`Failed to verify clip: ${error.message}`);
      }
      throw new Error('Failed to verify clip: Unknown error');
    }
  }

  /**
   * Get cached verification result by ID
   *
   * @param verificationId - Verification ID returned from verifyClip
   */
  static async getVerificationResult(verificationId: string): Promise<AIVerificationResult> {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/verify/${verificationId}`);
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response?.status === 404) {
          throw new Error('Verification result not found');
        }
        throw new Error(`Failed to get verification result: ${error.message}`);
      }
      throw new Error('Failed to get verification result: Unknown error');
    }
  }

  /**
   * Download video from IPFS and prepare it for AI service
   * Saves the video to the AI service's video directory
   *
   * @param cid - IPFS CID of the video
   * @param filename - Desired filename for the video
   * @returns Path to the prepared video file
   */
  static async prepareVideoForAI(cid: string, filename: string): Promise<string> {
    try {
      // Ensure AI video directory exists
      if (!fs.existsSync(AI_VIDEO_DIR)) {
        fs.mkdirSync(AI_VIDEO_DIR, { recursive: true });
        console.log(`✓ Created AI video directory: ${AI_VIDEO_DIR}`);
      }

      // Download from IPFS
      console.log(`Downloading video from IPFS: ${cid}`);
      const fileBuffer = await downloadFromIPFS(cid);

      // Save to AI video directory
      const outputPath = path.join(AI_VIDEO_DIR, filename);
      await fs.promises.writeFile(outputPath, fileBuffer);

      console.log(`✓ Saved video for AI service: ${outputPath}`);
      return outputPath;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to prepare video for AI: ${error.message}`);
      }
      throw new Error('Failed to prepare video for AI: Unknown error');
    }
  }

  /**
   * Copy a local video file to the AI service's video directory
   * Useful when video is already on local filesystem
   *
   * @param sourcePath - Path to source video file
   * @param filename - Desired filename in AI directory
   * @returns Path to the copied video file
   */
  static async copyVideoToAIDirectory(sourcePath: string, filename: string): Promise<string> {
    try {
      if (!fs.existsSync(sourcePath)) {
        throw new Error(`Source video not found: ${sourcePath}`);
      }

      // Ensure AI video directory exists
      if (!fs.existsSync(AI_VIDEO_DIR)) {
        fs.mkdirSync(AI_VIDEO_DIR, { recursive: true });
        console.log(`✓ Created AI video directory: ${AI_VIDEO_DIR}`);
      }

      const destPath = path.join(AI_VIDEO_DIR, filename);
      await fs.promises.copyFile(sourcePath, destPath);

      console.log(`✓ Copied video to AI directory: ${destPath}`);
      return destPath;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to copy video to AI directory: ${error.message}`);
      }
      throw new Error('Failed to copy video to AI directory: Unknown error');
    }
  }

  /**
   * Preprocess all videos in the AI service database
   * Transcribes all videos and caches them for faster verification
   */
  static async preprocessAllVideos(): Promise<void> {
    try {
      await axios.post(`${AI_SERVICE_URL}/preprocess`);
      console.log('✓ Started preprocessing all videos in AI service');
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(`Failed to preprocess videos: ${error.message}`);
      }
      throw new Error('Failed to preprocess videos: Unknown error');
    }
  }

  /**
   * Clear the AI service's transcription cache
   * Forces re-transcription of all videos on next verification
   */
  static async clearCache(): Promise<void> {
    try {
      await axios.get(`${AI_SERVICE_URL}/cache/clear`);
      console.log('✓ Cleared AI service cache');
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(`Failed to clear cache: ${error.message}`);
      }
      throw new Error('Failed to clear cache: Unknown error');
    }
  }

  /**
   * Delete a video from the AI service database
   *
   * @param videoName - Name of the video file to delete
   */
  static async deleteVideo(videoName: string): Promise<void> {
    try {
      await axios.delete(`${AI_SERVICE_URL}/videos/${videoName}`);
      console.log(`✓ Deleted video from AI service: ${videoName}`);
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response?.status === 404) {
          throw new Error('Video not found in AI service');
        }
        throw new Error(`Failed to delete video: ${error.message}`);
      }
      throw new Error('Failed to delete video: Unknown error');
    }
  }
}
