import express, { Request, Response } from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import { uploadToIPFS, downloadFromIPFS, deleteFromIPFS } from '../services/ipfs.service';
import { hashFile } from '../services/hash.service';
import { AIVerificationService } from '../services/ai-verification.service';
import { config } from '../config';

const router = express.Router();

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: config.maxFileSize },
  fileFilter: (req, file, cb) => {
    const allowedMimes = ['video/mp4', 'video/webm', 'video/quicktime'];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only video files are allowed.'));
    }
  },
});

/**
 * POST /api/ipfs/upload
 * Upload video file, compute hash, upload to IPFS, and register with AI service
 *
 * Query params:
 * - registerWithAI: 'true' to register video with AI service (for official videos)
 * - title: Optional title for the video
 */
router.post('/upload', upload.single('video'), async (req: Request, res: Response) => {
  let aiVideoPath: string | undefined;

  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePath = req.file.path;
    const registerWithAI = req.query.registerWithAI === 'true' || req.body.registerWithAI === true;
    const title = req.query.title as string || req.body.title as string || req.file.originalname;

    console.log(`\nUploading video: ${req.file.originalname}`);
    console.log(`Register with AI: ${registerWithAI}`);

    // Compute hash
    const hash = hashFile(filePath);

    // Upload to IPFS
    const cid = await uploadToIPFS(filePath);

    // If this is an official video, register it with AI service
    if (registerWithAI) {
      try {
        console.log('Registering video with AI service...');

        // Copy file to AI service directory
        const filename = `${cid}_${req.file.originalname}`;
        aiVideoPath = await AIVerificationService.copyVideoToAIDirectory(filePath, filename);

        // Register with AI service (transcribe and cache)
        await AIVerificationService.registerOfficialVideo(aiVideoPath, title);

        console.log('✓ Video registered with AI service');
      } catch (aiError) {
        console.error('Warning: Failed to register with AI service:', aiError);
        // Don't fail the upload if AI registration fails
        // Clean up AI video file if it was created
        if (aiVideoPath && fs.existsSync(aiVideoPath)) {
          fs.unlinkSync(aiVideoPath);
        }
      }
    }

    // Clean up temporary upload file
    fs.unlinkSync(filePath);

    res.json({
      hash,
      cid,
      aiRegistered: registerWithAI,
    });
  } catch (error) {
    // Clean up files if they exist
    if (req.file?.path && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    if (aiVideoPath && fs.existsSync(aiVideoPath)) {
      fs.unlinkSync(aiVideoPath);
    }

    console.error('Upload error:', error);
    res.status(500).json({
      error: 'Failed to upload file',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/ipfs/download/:cid
 * Download video from IPFS by CID
 */
router.get('/download/:cid', async (req: Request, res: Response) => {
  try {
    const { cid } = req.params;

    if (!cid) {
      return res.status(400).json({ error: 'CID is required' });
    }

    const fileBuffer = await downloadFromIPFS(cid);

    // Set appropriate headers
    res.setHeader('Content-Type', 'video/mp4');
    res.setHeader('Content-Length', fileBuffer.length);

    res.send(fileBuffer);
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({
      error: 'Failed to download file',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * DELETE /api/ipfs/:cid
 * Delete video from IPFS and AI service
 *
 * NOTE: This is for the mock IPFS implementation only.
 * Blockchain records cannot be deleted (immutable by design).
 * This endpoint removes:
 * - Video file from IPFS mock storage
 * - Video file from AI layer download directory
 * - Video from AI service database
 *
 * Query params:
 * - deleteFromAI: 'true' to also delete from AI service (default: true)
 */
router.delete('/:cid', async (req: Request, res: Response) => {
  const { cid } = req.params;
  const deleteFromAI = req.query.deleteFromAI !== 'false'; // Default to true
  const deletedItems: string[] = [];
  const errors: string[] = [];

  try {
    if (!cid) {
      return res.status(400).json({ error: 'CID is required' });
    }

    console.log(`\nDeleting video with CID: ${cid}`);
    console.log(`Delete from AI: ${deleteFromAI}`);

    // Step 1: Delete from IPFS mock storage
    try {
      await deleteFromIPFS(cid);
      deletedItems.push('IPFS storage');
      console.log('✓ Deleted from IPFS storage');
    } catch (error) {
      const errMsg = error instanceof Error ? error.message : 'Unknown error';
      errors.push(`IPFS deletion failed: ${errMsg}`);
      console.error('✗ Failed to delete from IPFS:', errMsg);
    }

    // Step 2: Delete from AI service if requested
    if (deleteFromAI) {
      try {
        // Find and delete AI video files (may have different filenames)
        const AI_VIDEO_DIR = path.join(__dirname, '../../ai-layer/download');

        if (fs.existsSync(AI_VIDEO_DIR)) {
          const files = fs.readdirSync(AI_VIDEO_DIR);
          const matchingFiles = files.filter(file => file.startsWith(cid));

          for (const file of matchingFiles) {
            const filePath = path.join(AI_VIDEO_DIR, file);
            fs.unlinkSync(filePath);
            console.log(`✓ Deleted AI video file: ${file}`);
          }

          if (matchingFiles.length > 0) {
            deletedItems.push(`AI download directory (${matchingFiles.length} file(s))`);
          }
        }

        // Delete from AI service database
        try {
          const aiVideos = await AIVerificationService.listVideos();
          const matchingVideo = aiVideos.find(v => v.video_name.startsWith(cid));

          if (matchingVideo) {
            await AIVerificationService.deleteVideo(matchingVideo.video_name);
            deletedItems.push('AI service database');
            console.log(`✓ Deleted from AI service database: ${matchingVideo.video_name}`);
          }
        } catch (aiError) {
          const errMsg = aiError instanceof Error ? aiError.message : 'Unknown error';
          errors.push(`AI service deletion failed: ${errMsg}`);
          console.error('✗ Failed to delete from AI service:', errMsg);
        }
      } catch (error) {
        const errMsg = error instanceof Error ? error.message : 'Unknown error';
        errors.push(`AI deletion failed: ${errMsg}`);
        console.error('✗ Failed to delete from AI layer:', errMsg);
      }
    }

    // Prepare response
    const response: any = {
      success: deletedItems.length > 0,
      cid,
      deleted: deletedItems,
    };

    if (errors.length > 0) {
      response.warnings = errors;
      response.message = 'Partial deletion completed with warnings';
    } else {
      response.message = 'Video deleted successfully';
    }

    // Add blockchain notice
    response.note = 'Blockchain records remain immutable and cannot be deleted';

    console.log(`\n${response.success ? '✓' : '✗'} Deletion complete`);
    console.log(`Deleted from: ${deletedItems.join(', ')}`);
    if (errors.length > 0) {
      console.log(`Warnings: ${errors.join(', ')}`);
    }

    const statusCode = response.success ? (errors.length > 0 ? 207 : 200) : 500;
    res.status(statusCode).json(response);

  } catch (error) {
    console.error('Deletion error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete video',
      message: error instanceof Error ? error.message : 'Unknown error',
      deleted: deletedItems,
      warnings: errors,
    });
  }
});

export default router;
