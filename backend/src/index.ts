import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import ipfsRoutes from './routes/ipfs';
import socialRoutes from './routes/social';
import verificationRoutes from './routes/verification';
import { config } from './config';
import './database/db'; // Initialize database

dotenv.config();

const app = express();
const PORT = config.port;

app.use(cors());
app.use(express.json());

// Serve uploaded files
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Serve official AI videos
app.use('/official-videos', express.static(path.join(__dirname, '../ai-layer/download')));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/ipfs', ipfsRoutes);
app.use('/api/social', socialRoutes);
app.use('/api/verification', verificationRoutes);

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
  console.log(`\nAvailable endpoints:`);
  console.log(`  - GET  /health`);
  console.log(`  - POST /api/ipfs/upload`);
  console.log(`  - GET  /api/ipfs/download/:cid`);
  console.log(`  - POST /api/verification/verify-clip`);
  console.log(`  - GET  /api/verification/health`);
  console.log(`  - GET  /api/verification/videos`);
  console.log(`  - POST /api/verification/preprocess`);
  console.log(`  - GET  /api/social/videos`);
  console.log(`  - POST /api/social/videos/upload`);
});
