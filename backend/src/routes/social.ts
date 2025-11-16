import express, { Request, Response } from 'express';
import multer from 'multer';
import path from 'path';
import { SocialService } from '../services/social.service';

const router = express.Router();

// Configure multer for video uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, '../../uploads/social'));
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${Math.random().toString(36).substring(7)}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /mp4|mov|avi|webm/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
      cb(null, true);
    } else {
      cb(new Error('Only video files are allowed'));
    }
  }
});

// POST /api/social/videos/upload
router.post('/videos/upload', upload.single('video'), (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No video file provided' });
    }

    const { title, description } = req.body;
    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    const fileUrl = `/uploads/social/${req.file.filename}`;
    const video = SocialService.createVideo(title, description || null, req.file.path, fileUrl);

    res.json(video);
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Failed to upload video' });
  }
});

// GET /api/social/videos
router.get('/videos', (req: Request, res: Response) => {
  try {
    const videos = SocialService.getAllVideos();
    res.json(videos);
  } catch (error) {
    console.error('Fetch videos error:', error);
    res.status(500).json({ error: 'Failed to fetch videos' });
  }
});

// POST /api/social/videos/:id/flag
router.post('/videos/:id/flag', (req: Request, res: Response) => {
  try {
    const videoId = parseInt(req.params.id);
    const { flagType } = req.body;

    if (!['verified', 'misleading', 'unverified', 'fake'].includes(flagType)) {
      return res.status(400).json({ error: 'Invalid flag type' });
    }

    const video = SocialService.getVideoById(videoId);
    if (!video) {
      return res.status(404).json({ error: 'Video not found' });
    }

    SocialService.addFlag(videoId, flagType);
    const flagCounts = SocialService.getFlagCounts(videoId);
    const updatedVideo = SocialService.getVideoById(videoId);

    res.json({ video: updatedVideo, flagCounts });
  } catch (error) {
    console.error('Flag error:', error);
    res.status(500).json({ error: 'Failed to add flag' });
  }
});

// GET /api/social/videos/:id/flags
router.get('/videos/:id/flags', (req: Request, res: Response) => {
  try {
    const videoId = parseInt(req.params.id);
    const video = SocialService.getVideoById(videoId);

    if (!video) {
      return res.status(404).json({ error: 'Video not found' });
    }

    const flagCounts = SocialService.getFlagCounts(videoId);
    res.json(flagCounts);
  } catch (error) {
    console.error('Get flags error:', error);
    res.status(500).json({ error: 'Failed to get flag counts' });
  }
});

export default router;
