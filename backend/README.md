# TruChain Backend

Express server providing IPFS upload/download services for TruChain video authenticity verification system.

## Overview

The backend service handles:
- Video file uploads and hashing (SHA-256)
- IPFS integration for decentralized storage
- File download from IPFS by CID

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- IPFS access (default: Infura IPFS gateway)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file in the backend directory:
```env
PORT=3001
IPFS_HOST=ipfs.infura.io
IPFS_PORT=5001
IPFS_PROTOCOL=https
MAX_FILE_SIZE=524288000
```

3. Run development server:
```bash
npm run dev
```

The server will start on `http://localhost:3001`

## Environment Variables

- `PORT`: Server port (default: 3001)
- `IPFS_HOST`: IPFS gateway host (default: ipfs.infura.io)
- `IPFS_PORT`: IPFS gateway port (default: 5001)
- `IPFS_PROTOCOL`: IPFS protocol (default: https)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 524288000 = 500MB)

## API Endpoints

### Health Check

**GET /health**

Check if the server is running.

**Response:**
```json
{
  "status": "ok"
}
```

### Upload Video to IPFS

**POST /api/ipfs/upload**

Upload a video file, compute SHA-256 hash, and upload to IPFS.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Form field `video` containing the video file

**Supported Video Formats:**
- video/mp4
- video/webm
- video/quicktime

**Response:**
```json
{
  "hash": [/* 32-byte array of numbers (0-255) */],
  "cid": "QmXxx..." // IPFS Content Identifier
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:3001/api/ipfs/upload \
  -F "video=@/path/to/video.mp4"
```

**Error Responses:**
- 400: No file uploaded or invalid file type
- 500: Server error during upload or IPFS processing

### Download Video from IPFS

**GET /api/ipfs/download/:cid**

Download a video file from IPFS by its Content Identifier (CID).

**Parameters:**
- `cid` (path parameter): IPFS Content Identifier

**Response:**
- Content-Type: video/mp4
- Body: Video file binary stream

**Example:**
```bash
curl http://localhost:3001/api/ipfs/download/QmXxx... --output video.mp4
```

**Error Responses:**
- 400: CID is required
- 500: Failed to download from IPFS

## Project Structure

```
backend/
├── src/
│   ├── index.ts           # Main Express server
│   ├── config.ts          # Configuration management
│   ├── routes/
│   │   └── ipfs.ts        # IPFS routes (upload/download)
│   └── services/
│       ├── hash.service.ts   # File hashing utilities
│       └── ipfs.service.ts   # IPFS client operations
├── uploads/               # Temporary upload directory
├── dist/                  # Compiled JavaScript (after build)
├── package.json
├── tsconfig.json
└── .env
```

## Development

### Available Scripts

- `npm run dev` - Start development server with auto-reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Run production server from compiled code

### Adding New Routes

1. Create route file in `src/routes/`
2. Import and register in `src/index.ts`
3. Follow existing patterns for error handling

### Hash Service

The hash service (`src/services/hash.service.ts`) provides:
- `hashFile(filePath: string): number[]` - Computes SHA-256 hash as 32-byte array
- `validateHash(hash: number[]): boolean` - Validates hash format

Hash format matches Solana program's `[u8; 32]` type for on-chain compatibility.

### IPFS Service

The IPFS service (`src/services/ipfs.service.ts`) provides:
- `uploadToIPFS(filePath: string): Promise<string>` - Upload file and return CID
- `downloadFromIPFS(cid: string): Promise<Buffer>` - Download file by CID

## Testing

### Manual Testing

1. Start the server:
```bash
npm run dev
```

2. Test health endpoint:
```bash
curl http://localhost:3001/health
```

3. Test file upload:
```bash
curl -X POST http://localhost:3001/api/ipfs/upload \
  -F "video=@test-video.mp4"
```

4. Test file download (use CID from upload response):
```bash
curl http://localhost:3001/api/ipfs/download/QmXxx... --output downloaded.mp4
```

## Deployment

### Production Build

```bash
npm run build
npm start
```

### Environment Setup

Ensure all environment variables are set in production environment.

## Troubleshooting

### "IPFS upload failed"
- Check IPFS gateway configuration
- Verify network connectivity to IPFS_HOST
- Check file size is under MAX_FILE_SIZE

### "File too large"
- Increase MAX_FILE_SIZE in .env
- Default limit is 500MB

### Port already in use
- Change PORT in .env
- Or kill process using port 3001: `lsof -ti:3001 | xargs kill`

## Security Considerations

- File uploads are validated for video MIME types only
- Files are temporarily stored in `uploads/` and deleted after processing
- Consider adding authentication for production use
- Rate limiting not implemented (add in production)

## Future Enhancements

- Add authentication middleware
- Implement rate limiting
- Add video transcript generation (Whisper AI)
- Add clip matching endpoint
- Add database for video metadata
- Add social flags API
