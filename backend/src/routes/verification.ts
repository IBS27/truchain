import express, { Request, Response } from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import { AIVerificationService } from '../services/ai-verification.service';

const router = express.Router();

// Configure multer for clip uploads
const clipUpload = multer({
  dest: 'uploads/clips/',
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB limit
  fileFilter: (req, file, cb) => {
    const allowedMimes = ['video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo'];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only video files are allowed.'));
    }
  },
});

/**
 * POST /api/verification/verify-clip
 * Verify a video clip against the database of official videos
 *
 * Performs hybrid verification (content + speaker) and returns:
 * - verification_type: 'full' (both match), 'content_only' (possible deepfake), 'not_verified'
 * - Matched video and timestamp
 * - Speaker verification results
 */
router.post('/verify-clip', clipUpload.single('clip'), async (req: Request, res: Response) => {
  let tempFilePath: string | undefined;

  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No clip file provided' });
    }

    tempFilePath = req.file.path;

    console.log(`\n${'='.repeat(70)}`);
    console.log('CLIP VERIFICATION REQUEST');
    console.log('='.repeat(70));
    console.log(`Clip: ${req.file.originalname}`);
    console.log(`Size: ${(req.file.size / (1024 * 1024)).toFixed(2)} MB`);
    console.log('='.repeat(70) + '\n');

    // Call AI service to verify clip
    const aiResult = await AIVerificationService.verifyClip(tempFilePath);

    // TODO: Query Solana blockchain for matched video's on-chain status
    // This will be implemented when Solana program is integrated
    // For now, return AI verification result only

    const result = {
      success: true,
      verification: aiResult,
      // onChainStatus: null, // Will be populated when Solana integration is complete
    };

    console.log(`\n${'='.repeat(70)}`);
    console.log('VERIFICATION RESULT');
    console.log('='.repeat(70));
    console.log(`Type: ${aiResult.verification_type}`);
    console.log(`Verified: ${aiResult.verified ? 'YES' : 'NO'}`);
    if (aiResult.best_match) {
      console.log(`Matched: ${aiResult.best_match.video_name}`);
      console.log(`Timestamp: ${aiResult.best_match.start_time.toFixed(1)}s - ${aiResult.best_match.end_time.toFixed(1)}s`);
      console.log(`Similarity: ${(aiResult.best_match.similarity * 100).toFixed(1)}%`);
    }
    if (aiResult.speaker_verification) {
      console.log(`Speaker: ${aiResult.speaker_verification.verified ? 'VERIFIED' : 'NOT VERIFIED'}`);
      console.log(`Speaker Similarity: ${(aiResult.speaker_verification.similarity * 100).toFixed(1)}%`);
    }
    console.log('='.repeat(70) + '\n');

    res.json(result);
  } catch (error) {
    console.error('Verification error:', error);

    if (error instanceof Error) {
      if (error.message.includes('AI service is not running')) {
        return res.status(503).json({
          error: 'AI service unavailable',
          message: 'The AI verification service is not running. Please start the Python AI service.',
          details: error.message,
        });
      }

      return res.status(500).json({
        error: 'Verification failed',
        message: error.message,
      });
    }

    res.status(500).json({
      error: 'Verification failed',
      message: 'An unknown error occurred',
    });
  } finally {
    // Clean up temporary file
    if (tempFilePath && fs.existsSync(tempFilePath)) {
      try {
        fs.unlinkSync(tempFilePath);
      } catch (error) {
        console.error('Failed to clean up temp file:', error);
      }
    }
  }
});

/**
 * GET /api/verification/result/:verificationId
 * Get cached verification result by ID
 */
router.get('/result/:verificationId', async (req: Request, res: Response) => {
  try {
    const { verificationId } = req.params;

    if (!verificationId) {
      return res.status(400).json({ error: 'Verification ID is required' });
    }

    const result = await AIVerificationService.getVerificationResult(verificationId);

    res.json({
      success: true,
      verification: result,
    });
  } catch (error) {
    console.error('Get verification result error:', error);

    if (error instanceof Error) {
      if (error.message.includes('not found')) {
        return res.status(404).json({
          error: 'Verification result not found',
          message: error.message,
        });
      }

      return res.status(500).json({
        error: 'Failed to get verification result',
        message: error.message,
      });
    }

    res.status(500).json({
      error: 'Failed to get verification result',
      message: 'An unknown error occurred',
    });
  }
});

/**
 * GET /api/verification/videos
 * List all videos available in the AI service database
 */
router.get('/videos', async (req: Request, res: Response) => {
  try {
    const videos = await AIVerificationService.listVideos();

    res.json({
      success: true,
      videos,
      count: videos.length,
    });
  } catch (error) {
    console.error('List videos error:', error);

    if (error instanceof Error) {
      return res.status(500).json({
        error: 'Failed to list videos',
        message: error.message,
      });
    }

    res.status(500).json({
      error: 'Failed to list videos',
      message: 'An unknown error occurred',
    });
  }
});

/**
 * POST /api/verification/preprocess
 * Preprocess all videos in the AI service database
 * This transcribes all videos and caches them for faster verification
 */
router.post('/preprocess', async (req: Request, res: Response) => {
  try {
    await AIVerificationService.preprocessAllVideos();

    res.json({
      success: true,
      message: 'Video preprocessing started in background',
    });
  } catch (error) {
    console.error('Preprocess error:', error);

    if (error instanceof Error) {
      return res.status(500).json({
        error: 'Failed to start preprocessing',
        message: error.message,
      });
    }

    res.status(500).json({
      error: 'Failed to start preprocessing',
      message: 'An unknown error occurred',
    });
  }
});

/**
 * DELETE /api/verification/cache
 * Clear the AI service's transcription cache
 */
router.delete('/cache', async (req: Request, res: Response) => {
  try {
    await AIVerificationService.clearCache();

    res.json({
      success: true,
      message: 'AI service cache cleared successfully',
    });
  } catch (error) {
    console.error('Clear cache error:', error);

    if (error instanceof Error) {
      return res.status(500).json({
        error: 'Failed to clear cache',
        message: error.message,
      });
    }

    res.status(500).json({
      error: 'Failed to clear cache',
      message: 'An unknown error occurred',
    });
  }
});

/**
 * GET /api/verification/health
 * Check AI service health status
 */
router.get('/health', async (req: Request, res: Response) => {
  try {
    const health = await AIVerificationService.checkHealth();

    res.json({
      success: true,
      aiService: health,
      backend: {
        status: 'healthy',
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    console.error('Health check error:', error);

    if (error instanceof Error) {
      return res.status(503).json({
        success: false,
        error: 'AI service unavailable',
        message: error.message,
        backend: {
          status: 'healthy',
          timestamp: new Date().toISOString(),
        },
      });
    }

    res.status(503).json({
      success: false,
      error: 'AI service unavailable',
      message: 'An unknown error occurred',
    });
  }
});

export default router;
