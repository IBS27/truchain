import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: process.env.PORT || 3001,
  ipfs: {
    host: process.env.IPFS_HOST || 'ipfs.infura.io',
    port: parseInt(process.env.IPFS_PORT || '5001'),
    protocol: process.env.IPFS_PROTOCOL || 'https',
  },
  maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '524288000'), // 500MB
};
