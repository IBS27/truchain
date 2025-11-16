import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import ipfsRoutes from './routes/ipfs';
import { config } from './config';

dotenv.config();

const app = express();
const PORT = config.port;

app.use(cors());
app.use(express.json());

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/ipfs', ipfsRoutes);

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
