import express, { Request, Response } from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { uploadToIPFS, downloadFromIPFS } from '../services/ipfs.service';
import { hashFile } from '../services/hash.service';
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
 * Upload video file, compute hash, upload to IPFS
 */
router.post('/upload', upload.single('video'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePath = req.file.path;

    // Compute hash
    const hash = hashFile(filePath);

    // Upload to IPFS
    const cid = await uploadToIPFS(filePath);

    // Clean up temporary file
    fs.unlinkSync(filePath);

    res.json({
      hash,
      cid,
    });
  } catch (error) {
    // Clean up file if it exists
    if (req.file?.path && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
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

export default router;
