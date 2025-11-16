# Frontend & Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build role-based frontend UI with auto role detection and backend IPFS service for TruChain video verification system.

**Architecture:** React frontend with conditional rendering based on on-chain role detection (Admin/Official/Endorser). Backend Express service handles IPFS uploads and video hashing. Frontend uses @coral-xyz/anchor for Solana program interaction.

**Tech Stack:** React, TypeScript, @coral-xyz/anchor, @solana/web3.js, Node.js, Express, ipfs-http-client

---

## Task 1: Frontend Dependencies Setup

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/.env`

**Step 1: Add @coral-xyz/anchor dependency**

Run from worktree root:
```bash
cd /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/frontend
npm install @coral-xyz/anchor
```

Expected: Package installed successfully

**Step 2: Create frontend environment file**

Create `frontend/.env`:
```env
VITE_SOLANA_NETWORK=devnet
VITE_PROGRAM_ID=FGkp4CpRBNDQz2h5idbhbX7cHkbggpsUsF7enLiQE2nT
VITE_ADMIN_WALLET=YOUR_ADMIN_WALLET_HERE
VITE_BACKEND_URL=http://localhost:3001
```

**Step 3: Verify build works**

Run: `npm run build`
Expected: Build completes without errors

**Step 4: Commit**

```bash
git add package.json package-lock.json .env
git commit -m "feat: add Anchor dependency and environment config"
```

---

## Task 2: Backend Project Setup

**Files:**
- Create: `backend/package.json`
- Create: `backend/tsconfig.json`
- Create: `backend/.env`
- Create: `backend/src/index.ts`
- Create: `backend/.gitignore`

**Step 1: Initialize backend project**

Run from worktree root:
```bash
mkdir -p /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/backend
cd /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/backend
npm init -y
```

**Step 2: Install backend dependencies**

Run:
```bash
npm install express multer ipfs-http-client cors dotenv
npm install -D typescript @types/express @types/multer @types/cors @types/node ts-node nodemon
```

Expected: All packages installed successfully

**Step 3: Create TypeScript config**

Create `backend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**Step 4: Create backend environment file**

Create `backend/.env`:
```env
PORT=3001
IPFS_HOST=ipfs.infura.io
IPFS_PORT=5001
IPFS_PROTOCOL=https
MAX_FILE_SIZE=524288000
```

**Step 5: Create backend .gitignore**

Create `backend/.gitignore`:
```
node_modules/
dist/
.env
uploads/
*.log
```

**Step 6: Update package.json scripts**

Modify `backend/package.json` to add scripts:
```json
{
  "scripts": {
    "dev": "nodemon --exec ts-node src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

**Step 7: Create basic Express server**

Create `backend/src/index.ts`:
```typescript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
```

**Step 8: Test backend server**

Run: `npm run dev`
Expected: Server starts on port 3001

Test in another terminal: `curl http://localhost:3001/health`
Expected: `{"status":"ok"}`

**Step 9: Commit**

```bash
git add backend/
git commit -m "feat: initialize backend Express server"
```

---

## Task 3: Backend Hash Service

**Files:**
- Create: `backend/src/services/hash.service.ts`

**Step 1: Create hash service**

Create `backend/src/services/hash.service.ts`:
```typescript
import crypto from 'crypto';
import fs from 'fs';

/**
 * Computes SHA-256 hash of a file
 * Returns 32-byte array matching Solana program's [u8; 32] type
 */
export function hashFile(filePath: string): number[] {
  const fileBuffer = fs.readFileSync(filePath);
  const hashBuffer = crypto.createHash('sha256').update(fileBuffer).digest();

  // Convert Buffer to number array for Solana compatibility
  return Array.from(hashBuffer);
}

/**
 * Validates that hash is exactly 32 bytes
 */
export function validateHash(hash: number[]): boolean {
  return Array.isArray(hash) && hash.length === 32 && hash.every(b => b >= 0 && b <= 255);
}
```

**Step 2: Verify hash service compiles**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add backend/src/services/hash.service.ts
git commit -m "feat: add file hashing service for SHA-256"
```

---

## Task 4: Backend IPFS Service

**Files:**
- Create: `backend/src/services/ipfs.service.ts`
- Create: `backend/src/config.ts`

**Step 1: Create config file**

Create `backend/src/config.ts`:
```typescript
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
```

**Step 2: Create IPFS service**

Create `backend/src/services/ipfs.service.ts`:
```typescript
import { create, IPFSHTTPClient } from 'ipfs-http-client';
import fs from 'fs';
import { config } from '../config';

let ipfsClient: IPFSHTTPClient | null = null;

/**
 * Initialize IPFS client (lazy initialization)
 */
function getIPFSClient(): IPFSHTTPClient {
  if (!ipfsClient) {
    ipfsClient = create({
      host: config.ipfs.host,
      port: config.ipfs.port,
      protocol: config.ipfs.protocol,
    });
  }
  return ipfsClient;
}

/**
 * Upload file to IPFS
 * Returns CID (Content Identifier)
 */
export async function uploadToIPFS(filePath: string): Promise<string> {
  const client = getIPFSClient();
  const fileBuffer = fs.readFileSync(filePath);

  const result = await client.add(fileBuffer);
  return result.cid.toString();
}

/**
 * Download file from IPFS
 * Returns Buffer of file contents
 */
export async function downloadFromIPFS(cid: string): Promise<Buffer> {
  const client = getIPFSClient();
  const chunks: Uint8Array[] = [];

  for await (const chunk of client.cat(cid)) {
    chunks.push(chunk);
  }

  return Buffer.concat(chunks);
}
```

**Step 3: Verify IPFS service compiles**

Run: `npm run build`
Expected: Build completes without errors

**Step 4: Commit**

```bash
git add backend/src/config.ts backend/src/services/ipfs.service.ts
git commit -m "feat: add IPFS service for upload/download"
```

---

## Task 5: Backend IPFS Routes

**Files:**
- Create: `backend/src/routes/ipfs.ts`
- Modify: `backend/src/index.ts`
- Create: `backend/uploads/.gitkeep`

**Step 1: Create uploads directory**

Run:
```bash
mkdir -p /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/backend/uploads
touch /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/backend/uploads/.gitkeep
```

**Step 2: Create IPFS routes**

Create `backend/src/routes/ipfs.ts`:
```typescript
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
```

**Step 3: Register routes in main server**

Modify `backend/src/index.ts`:
```typescript
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
```

**Step 4: Verify backend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add IPFS upload/download API routes"
```

---

## Task 6: Frontend Anchor Program Hook

**Files:**
- Create: `frontend/src/hooks/useAnchorProgram.ts`

**Step 1: Create Anchor program hook**

Create `frontend/src/hooks/useAnchorProgram.ts`:
```typescript
import { useMemo } from 'react';
import { AnchorProvider, Program } from '@coral-xyz/anchor';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { Truchain } from '../anchor/idl';
import idl from '../anchor/idl';

/**
 * Hook to get initialized Anchor program instance
 * Returns null if wallet not connected
 */
export function useAnchorProgram() {
  const { connection } = useConnection();
  const wallet = useWallet();

  const program = useMemo(() => {
    if (!wallet.publicKey || !wallet.signTransaction || !wallet.signAllTransactions) {
      return null;
    }

    const provider = new AnchorProvider(
      connection,
      wallet as any,
      { commitment: 'confirmed' }
    );

    return new Program<Truchain>(
      idl as any,
      provider
    );
  }, [connection, wallet]);

  return program;
}
```

**Step 2: Verify frontend builds**

Run from frontend directory:
```bash
cd /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/frontend
npm run build
```

Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/hooks/useAnchorProgram.ts
git commit -m "feat: add Anchor program hook"
```

---

## Task 7: Frontend Solana Service

**Files:**
- Create: `frontend/src/services/solana.ts`

**Step 1: Create Solana service with helper functions**

Create `frontend/src/services/solana.ts`:
```typescript
import { Program } from '@coral-xyz/anchor';
import { PublicKey } from '@solana/web3.js';
import { Truchain } from '../anchor/idl';

const ADMIN_WALLET = import.meta.env.VITE_ADMIN_WALLET;

/**
 * Fetch all Official accounts from the program
 */
export async function getAllOfficials(program: Program<Truchain>) {
  return await program.account.official.all();
}

/**
 * Fetch all Video accounts for a specific official
 */
export async function getVideosForOfficial(
  program: Program<Truchain>,
  officialPubkey: PublicKey
) {
  const videos = await program.account.video.all();
  return videos.filter(v => v.account.official.equals(officialPubkey));
}

/**
 * Check if wallet is the admin
 */
export function checkIsAdmin(walletPubkey: PublicKey | null): boolean {
  if (!walletPubkey || !ADMIN_WALLET) return false;
  return walletPubkey.toString() === ADMIN_WALLET;
}

/**
 * Check if wallet is an official's authority
 * Returns the Official account if true, null otherwise
 */
export async function checkIsOfficialAuthority(
  program: Program<Truchain>,
  walletPubkey: PublicKey | null
) {
  if (!walletPubkey) return null;

  const officials = await getAllOfficials(program);
  return officials.find(o => o.account.authority.equals(walletPubkey)) || null;
}

/**
 * Check if wallet is an endorser for any official
 * Returns array of Official accounts where wallet is an endorser
 */
export async function checkIsEndorser(
  program: Program<Truchain>,
  walletPubkey: PublicKey | null
) {
  if (!walletPubkey) return [];

  const officials = await getAllOfficials(program);
  return officials.filter(o =>
    o.account.endorsers.some(e => e.equals(walletPubkey))
  );
}

/**
 * Register a new official (admin only)
 */
export async function registerOfficial(
  program: Program<Truchain>,
  officialId: number,
  name: string,
  authority: PublicKey,
  endorsers: [PublicKey, PublicKey, PublicKey]
) {
  const [officialPda] = PublicKey.findProgramAddressSync(
    [Buffer.from('official'), Buffer.from(officialId.toString().padStart(8, '0'))],
    program.programId
  );

  return await program.methods
    .registerOfficial(officialId, name, authority, endorsers)
    .accounts({
      official: officialPda,
      admin: program.provider.publicKey!,
    })
    .rpc();
}

/**
 * Register a video (official's authority only)
 */
export async function registerVideo(
  program: Program<Truchain>,
  officialPubkey: PublicKey,
  videoHash: number[],
  ipfsCid: string
) {
  const [videoPda] = PublicKey.findProgramAddressSync(
    [Buffer.from('video'), officialPubkey.toBuffer(), Buffer.from(videoHash)],
    program.programId
  );

  return await program.methods
    .registerVideo(videoHash, ipfsCid)
    .accounts({
      official: officialPubkey,
      video: videoPda,
      authority: program.provider.publicKey!,
    })
    .rpc();
}

/**
 * Endorse a video (endorser only)
 */
export async function endorseVideo(
  program: Program<Truchain>,
  officialPubkey: PublicKey,
  videoHash: number[],
  isAuthentic: boolean
) {
  const [videoPda] = PublicKey.findProgramAddressSync(
    [Buffer.from('video'), officialPubkey.toBuffer(), Buffer.from(videoHash)],
    program.programId
  );

  return await program.methods
    .endorseVideo(isAuthentic)
    .accounts({
      official: officialPubkey,
      video: videoPda,
      endorser: program.provider.publicKey!,
    })
    .rpc();
}
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/services/solana.ts
git commit -m "feat: add Solana service with program interaction functions"
```

---

## Task 8: Frontend API Service

**Files:**
- Create: `frontend/src/services/api.ts`

**Step 1: Create API service for backend calls**

Create `frontend/src/services/api.ts`:
```typescript
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export interface UploadResponse {
  hash: number[];
  cid: string;
}

/**
 * Upload video file to backend
 * Returns hash and IPFS CID
 */
export async function uploadVideo(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('video', file);

  const response = await fetch(`${BACKEND_URL}/api/ipfs/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to upload video');
  }

  return await response.json();
}

/**
 * Get IPFS download URL for a CID
 */
export function getIPFSDownloadUrl(cid: string): string {
  return `${BACKEND_URL}/api/ipfs/download/${cid}`;
}
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add API service for backend communication"
```

---

## Task 9: Frontend Role Detection Hook

**Files:**
- Create: `frontend/src/hooks/useRoleDetection.ts`

**Step 1: Create role detection hook**

Create `frontend/src/hooks/useRoleDetection.ts`:
```typescript
import { useState, useEffect } from 'react';
import { PublicKey } from '@solana/web3.js';
import { useAnchorProgram } from './useAnchorProgram';
import {
  checkIsAdmin,
  checkIsOfficialAuthority,
  checkIsEndorser,
} from '../services/solana';

export type Role = 'admin' | 'official' | 'endorser' | 'user' | null;

export interface RoleDetectionResult {
  role: Role;
  loading: boolean;
  officialAccount: any | null; // Official account if role is 'official'
  assignedOfficials: any[]; // Official accounts if role is 'endorser'
}

/**
 * Hook to detect wallet role based on on-chain data
 * Returns role, loading state, and relevant account data
 */
export function useRoleDetection(walletPubkey: PublicKey | null): RoleDetectionResult {
  const program = useAnchorProgram();
  const [result, setResult] = useState<RoleDetectionResult>({
    role: null,
    loading: true,
    officialAccount: null,
    assignedOfficials: [],
  });

  useEffect(() => {
    async function detectRole() {
      if (!walletPubkey || !program) {
        setResult({
          role: null,
          loading: false,
          officialAccount: null,
          assignedOfficials: [],
        });
        return;
      }

      setResult(prev => ({ ...prev, loading: true }));

      try {
        // Check admin first (cheapest check)
        if (checkIsAdmin(walletPubkey)) {
          setResult({
            role: 'admin',
            loading: false,
            officialAccount: null,
            assignedOfficials: [],
          });
          return;
        }

        // Check if official's authority
        const officialAccount = await checkIsOfficialAuthority(program, walletPubkey);
        if (officialAccount) {
          setResult({
            role: 'official',
            loading: false,
            officialAccount,
            assignedOfficials: [],
          });
          return;
        }

        // Check if endorser
        const assignedOfficials = await checkIsEndorser(program, walletPubkey);
        if (assignedOfficials.length > 0) {
          setResult({
            role: 'endorser',
            loading: false,
            officialAccount: null,
            assignedOfficials,
          });
          return;
        }

        // Default to user
        setResult({
          role: 'user',
          loading: false,
          officialAccount: null,
          assignedOfficials: [],
        });
      } catch (error) {
        console.error('Role detection error:', error);
        setResult({
          role: null,
          loading: false,
          officialAccount: null,
          assignedOfficials: [],
        });
      }
    }

    detectRole();
  }, [walletPubkey, program]);

  return result;
}
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/hooks/useRoleDetection.ts
git commit -m "feat: add role detection hook"
```

---

## Task 10: Admin Panel Component

**Files:**
- Create: `frontend/src/components/AdminPanel.tsx`

**Step 1: Create AdminPanel component**

Create `frontend/src/components/AdminPanel.tsx`:
```typescript
import { useState } from 'react';
import { PublicKey } from '@solana/web3.js';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { registerOfficial, getAllOfficials } from '../services/solana';

export function AdminPanel() {
  const program = useAnchorProgram();
  const [officialId, setOfficialId] = useState('');
  const [name, setName] = useState('');
  const [authority, setAuthority] = useState('');
  const [endorser1, setEndorser1] = useState('');
  const [endorser2, setEndorser2] = useState('');
  const [endorser3, setEndorser3] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [officials, setOfficials] = useState<any[]>([]);

  const loadOfficials = async () => {
    if (!program) return;
    try {
      const allOfficials = await getAllOfficials(program);
      setOfficials(allOfficials);
    } catch (error) {
      console.error('Failed to load officials:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!program) {
      setMessage({ type: 'error', text: 'Program not initialized' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // Validate inputs
      const authorityPubkey = new PublicKey(authority);
      const endorser1Pubkey = new PublicKey(endorser1);
      const endorser2Pubkey = new PublicKey(endorser2);
      const endorser3Pubkey = new PublicKey(endorser3);

      // Check for duplicates
      const endorsers = [endorser1, endorser2, endorser3];
      if (new Set(endorsers).size !== endorsers.length) {
        throw new Error('Endorsers must be unique');
      }

      const tx = await registerOfficial(
        program,
        parseInt(officialId),
        name,
        authorityPubkey,
        [endorser1Pubkey, endorser2Pubkey, endorser3Pubkey]
      );

      setMessage({ type: 'success', text: `Official registered! Transaction: ${tx}` });

      // Reset form
      setOfficialId('');
      setName('');
      setAuthority('');
      setEndorser1('');
      setEndorser2('');
      setEndorser3('');

      // Reload officials list
      await loadOfficials();
    } catch (error: any) {
      console.error('Registration error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to register official' });
    } finally {
      setLoading(false);
    }
  };

  // Load officials on mount
  useState(() => {
    loadOfficials();
  });

  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <h2>Admin Panel - Register Official</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: '40px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label>
            Official ID:
            <input
              type="number"
              value={officialId}
              onChange={(e) => setOfficialId(e.target.value)}
              required
              style={{ marginLeft: '10px', padding: '5px', width: '200px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Name (max 32 bytes):
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={32}
              required
              style={{ marginLeft: '10px', padding: '5px', width: '300px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Authority Wallet:
            <input
              type="text"
              value={authority}
              onChange={(e) => setAuthority(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Endorser 1:
            <input
              type="text"
              value={endorser1}
              onChange={(e) => setEndorser1(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Endorser 2:
            <input
              type="text"
              value={endorser2}
              onChange={(e) => setEndorser2(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Endorser 3:
            <input
              type="text"
              value={endorser3}
              onChange={(e) => setEndorser3(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Registering...' : 'Register Official'}
        </button>
      </form>

      {message && (
        <div
          style={{
            padding: '10px',
            marginBottom: '20px',
            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
            color: message.type === 'success' ? '#155724' : '#721c24',
            borderRadius: '4px',
          }}
        >
          {message.text}
        </div>
      )}

      <h3>Registered Officials</h3>
      {officials.length === 0 ? (
        <p>No officials registered yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>ID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Name</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Authority</th>
            </tr>
          </thead>
          <tbody>
            {officials.map((official, idx) => (
              <tr key={idx}>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {official.account.officialId.toString()}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {Buffer.from(official.account.name).toString('utf8').replace(/\0/g, '')}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '12px' }}>
                  {official.account.authority.toString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/components/AdminPanel.tsx
git commit -m "feat: add AdminPanel component"
```

---

## Task 11: Official Panel Component

**Files:**
- Create: `frontend/src/components/OfficialPanel.tsx`

**Step 1: Create OfficialPanel component**

Create `frontend/src/components/OfficialPanel.tsx`:
```typescript
import { useState, useEffect } from 'react';
import { PublicKey } from '@solana/web3.js';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { registerVideo, getVideosForOfficial } from '../services/solana';
import { uploadVideo, getIPFSDownloadUrl } from '../services/api';

interface OfficialPanelProps {
  officialAccount: any;
}

export function OfficialPanel({ officialAccount }: OfficialPanelProps) {
  const program = useAnchorProgram();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [videos, setVideos] = useState<any[]>([]);

  const loadVideos = async () => {
    if (!program) return;
    try {
      const officialVideos = await getVideosForOfficial(program, officialAccount.publicKey);
      setVideos(officialVideos);
    } catch (error) {
      console.error('Failed to load videos:', error);
    }
  };

  useEffect(() => {
    loadVideos();
  }, [program, officialAccount]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !program) return;

    setLoading(true);
    setMessage(null);

    try {
      // Step 1: Upload to backend (IPFS + hash)
      setMessage({ type: 'success', text: 'Uploading to IPFS...' });
      const { hash, cid } = await uploadVideo(file);

      // Step 2: Register on-chain
      setMessage({ type: 'success', text: 'Registering on blockchain...' });
      const tx = await registerVideo(
        program,
        officialAccount.publicKey,
        hash,
        cid
      );

      setMessage({ type: 'success', text: `Video registered! Transaction: ${tx}` });
      setFile(null);

      // Reload videos
      await loadVideos();
    } catch (error: any) {
      console.error('Upload error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to upload video' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: any) => {
    if (status.unverified !== undefined) return 'Unverified';
    if (status.authentic !== undefined) return 'Authentic';
    if (status.disputed !== undefined) return 'Disputed';
    return 'Unknown';
  };

  const getStatusColor = (status: any) => {
    if (status.unverified !== undefined) return '#ffc107';
    if (status.authentic !== undefined) return '#28a745';
    if (status.disputed !== undefined) return '#dc3545';
    return '#6c757d';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1000px' }}>
      <h2>Official Panel - Upload Videos</h2>
      <p>Official: {Buffer.from(officialAccount.account.name).toString('utf8').replace(/\0/g, '')}</p>

      <div style={{ marginBottom: '40px' }}>
        <h3>Upload New Video</h3>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            disabled={loading}
          />
        </div>
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          style={{
            padding: '10px 20px',
            backgroundColor: !file || loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: !file || loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Uploading...' : 'Upload Video'}
        </button>
      </div>

      {message && (
        <div
          style={{
            padding: '10px',
            marginBottom: '20px',
            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
            color: message.type === 'success' ? '#155724' : '#721c24',
            borderRadius: '4px',
          }}
        >
          {message.text}
        </div>
      )}

      <h3>Registered Videos</h3>
      {videos.length === 0 ? (
        <p>No videos registered yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>IPFS CID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Status</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Votes</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {videos.map((video, idx) => {
              const cidString = Buffer.from(video.account.ipfsCid).toString('utf8').replace(/\0/g, '');
              const status = video.account.status;
              const votes = video.account.votes || [];
              const authenticVotes = votes.filter((v: any) => v.isAuthentic).length;
              const fakeVotes = votes.length - authenticVotes;

              return (
                <tr key={idx}>
                  <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '12px' }}>
                    <a href={getIPFSDownloadUrl(cidString)} target="_blank" rel="noopener noreferrer">
                      {cidString}
                    </a>
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: getStatusColor(status),
                        color: 'white',
                        fontSize: '12px',
                      }}
                    >
                      {getStatusDisplay(status)}
                    </span>
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    ✓ {authenticVotes} / ✗ {fakeVotes}
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    {new Date(video.account.timestamp.toNumber() * 1000).toLocaleString()}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/components/OfficialPanel.tsx
git commit -m "feat: add OfficialPanel component"
```

---

## Task 12: Endorser Panel Component

**Files:**
- Create: `frontend/src/components/EndorserPanel.tsx`

**Step 1: Create EndorserPanel component**

Create `frontend/src/components/EndorserPanel.tsx`:
```typescript
import { useState, useEffect } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { getVideosForOfficial, endorseVideo } from '../services/solana';
import { uploadVideo, getIPFSDownloadUrl } from '../services/api';

interface EndorserPanelProps {
  assignedOfficials: any[];
}

export function EndorserPanel({ assignedOfficials }: EndorserPanelProps) {
  const program = useAnchorProgram();
  const { publicKey } = useWallet();
  const [pendingVideos, setPendingVideos] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [matchResult, setMatchResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadPendingVideos = async () => {
    if (!program || !publicKey) return;

    try {
      const allVideos = [];
      for (const official of assignedOfficials) {
        const videos = await getVideosForOfficial(program, official.publicKey);

        // Filter videos where this endorser hasn't voted yet
        const unvotedVideos = videos.filter(video => {
          const hasVoted = video.account.votes.some((v: any) =>
            v.endorser.equals(publicKey)
          );
          return !hasVoted;
        });

        allVideos.push(...unvotedVideos.map(v => ({
          ...v,
          officialName: Buffer.from(official.account.name).toString('utf8').replace(/\0/g, ''),
          officialPubkey: official.publicKey,
        })));
      }

      setPendingVideos(allVideos);
    } catch (error) {
      console.error('Failed to load pending videos:', error);
    }
  };

  useEffect(() => {
    loadPendingVideos();
  }, [program, publicKey, assignedOfficials]);

  const handleVote = async (video: any, isAuthentic: boolean) => {
    if (!program) return;

    setLoading(true);
    setMessage(null);

    try {
      const tx = await endorseVideo(
        program,
        video.officialPubkey,
        Array.from(video.account.videoHash),
        isAuthentic
      );

      setMessage({
        type: 'success',
        text: `Vote submitted! Transaction: ${tx}`,
      });

      // Reload pending videos
      await loadPendingVideos();
    } catch (error: any) {
      console.error('Vote error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to submit vote' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileVerify = async () => {
    if (!file || !program) return;

    setLoading(true);
    setMessage(null);
    setMatchResult(null);

    try {
      // Upload file to get hash
      const { hash } = await uploadVideo(file);

      // Search for matching video on-chain
      const allVideos = [];
      for (const official of assignedOfficials) {
        const videos = await getVideosForOfficial(program, official.publicKey);
        allVideos.push(...videos.map(v => ({
          ...v,
          officialName: Buffer.from(official.account.name).toString('utf8').replace(/\0/g, ''),
          officialPubkey: official.publicKey,
        })));
      }

      const hashString = hash.join(',');
      const match = allVideos.find(v =>
        Array.from(v.account.videoHash).join(',') === hashString
      );

      if (match) {
        setMatchResult(match);
        setMessage({ type: 'success', text: 'Match found! You can vote below.' });
      } else {
        setMessage({ type: 'error', text: 'No matching video found on-chain.' });
      }
    } catch (error: any) {
      console.error('Verify error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to verify file' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: any) => {
    if (status.unverified !== undefined) return 'Unverified';
    if (status.authentic !== undefined) return 'Authentic';
    if (status.disputed !== undefined) return 'Disputed';
    return 'Unknown';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px' }}>
      <h2>Endorser Panel</h2>
      <p>You are an endorser for {assignedOfficials.length} official(s)</p>

      {/* Section 1: Pending Videos */}
      <div style={{ marginBottom: '40px' }}>
        <h3>Pending Videos (Need Your Vote)</h3>
        {pendingVideos.length === 0 ? (
          <p>No pending videos to vote on.</p>
        ) : (
          <div>
            {pendingVideos.map((video, idx) => {
              const cidString = Buffer.from(video.account.ipfsCid).toString('utf8').replace(/\0/g, '');
              const votes = video.account.votes || [];
              const authenticVotes = votes.filter((v: any) => v.isAuthentic).length;
              const fakeVotes = votes.length - authenticVotes;

              return (
                <div
                  key={idx}
                  style={{
                    border: '1px solid #ddd',
                    padding: '15px',
                    marginBottom: '15px',
                    borderRadius: '8px',
                  }}
                >
                  <h4>Video from {video.officialName}</h4>
                  <p>
                    <strong>IPFS CID:</strong>{' '}
                    <a href={getIPFSDownloadUrl(cidString)} target="_blank" rel="noopener noreferrer">
                      {cidString}
                    </a>
                  </p>
                  <p>
                    <strong>Status:</strong> {getStatusDisplay(video.account.status)}
                  </p>
                  <p>
                    <strong>Current Votes:</strong> ✓ {authenticVotes} / ✗ {fakeVotes}
                  </p>
                  <div>
                    <button
                      onClick={() => handleVote(video, true)}
                      disabled={loading}
                      style={{
                        padding: '8px 16px',
                        marginRight: '10px',
                        backgroundColor: loading ? '#ccc' : '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Vote Authentic
                    </button>
                    <button
                      onClick={() => handleVote(video, false)}
                      disabled={loading}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: loading ? '#ccc' : '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Vote Fake
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Section 2: Verify Uploaded File */}
      <div style={{ marginBottom: '40px' }}>
        <h3>Verify Uploaded File</h3>
        <p>Upload a video file to check if it matches any registered videos</p>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="file"
            accept="video/*"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setFile(e.target.files[0]);
                setMatchResult(null);
              }
            }}
            disabled={loading}
          />
        </div>
        <button
          onClick={handleFileVerify}
          disabled={!file || loading}
          style={{
            padding: '10px 20px',
            backgroundColor: !file || loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: !file || loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Verifying...' : 'Verify File'}
        </button>

        {matchResult && (
          <div
            style={{
              marginTop: '20px',
              border: '1px solid #28a745',
              padding: '15px',
              borderRadius: '8px',
              backgroundColor: '#d4edda',
            }}
          >
            <h4>Match Found!</h4>
            <p><strong>Official:</strong> {matchResult.officialName}</p>
            <p><strong>Status:</strong> {getStatusDisplay(matchResult.account.status)}</p>
            <div>
              <button
                onClick={() => handleVote(matchResult, true)}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  marginRight: '10px',
                  backgroundColor: loading ? '#ccc' : '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                Vote Authentic
              </button>
              <button
                onClick={() => handleVote(matchResult, false)}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  backgroundColor: loading ? '#ccc' : '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                Vote Fake
              </button>
            </div>
          </div>
        )}
      </div>

      {message && (
        <div
          style={{
            padding: '10px',
            marginBottom: '20px',
            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
            color: message.type === 'success' ? '#155724' : '#721c24',
            borderRadius: '4px',
          }}
        >
          {message.text}
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/components/EndorserPanel.tsx
git commit -m "feat: add EndorserPanel component with hybrid verification"
```

---

## Task 13: Update App.tsx with Role-Based Rendering

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: Update App.tsx to use role detection and panels**

Replace contents of `frontend/src/App.tsx`:
```typescript
import { useMemo } from 'react';
import {
  ConnectionProvider,
  WalletProvider,
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets';
import {
  WalletModalProvider,
  WalletMultiButton,
} from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';
import { useWallet } from '@solana/wallet-adapter-react';

import { useRoleDetection } from './hooks/useRoleDetection';
import { AdminPanel } from './components/AdminPanel';
import { OfficialPanel } from './components/OfficialPanel';
import { EndorserPanel } from './components/EndorserPanel';

import './App.css';
import '@solana/wallet-adapter-react-ui/styles.css';

function AppContent() {
  const { publicKey } = useWallet();
  const { role, loading, officialAccount, assignedOfficials } = useRoleDetection(publicKey);

  if (!publicKey) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h1>TruChain - Video Authenticity Verification</h1>
        <p>Please connect your wallet to continue</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2>Detecting your role...</h2>
        <p>Please wait while we check your permissions on-chain</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h1>TruChain</h1>
        <p>
          <strong>Role:</strong> {role || 'Unknown'} | <strong>Wallet:</strong>{' '}
          {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
        </p>
      </div>

      {role === 'admin' && <AdminPanel />}
      {role === 'official' && officialAccount && <OfficialPanel officialAccount={officialAccount} />}
      {role === 'endorser' && <EndorserPanel assignedOfficials={assignedOfficials} />}
      {role === 'user' && (
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <h2>User View</h2>
          <p>You don't have admin, official, or endorser privileges.</p>
          <p>Social feed functionality coming soon!</p>
        </div>
      )}
      {!role && (
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <h2>Error</h2>
          <p>Failed to detect your role. Please try reconnecting your wallet.</p>
        </div>
      )}
    </div>
  );
}

function App() {
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);

  const wallets = useMemo(
    () => [new PhantomWalletAdapter()],
    [network]
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <div style={{ padding: '20px', textAlign: 'right' }}>
            <WalletMultiButton />
          </div>
          <AppContent />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}

export default App;
```

**Step 2: Verify frontend builds**

Run: `npm run build`
Expected: Build completes without errors

**Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: integrate role-based rendering in App"
```

---

## Task 14: Final Testing & Documentation

**Files:**
- Create: `backend/README.md`
- Create: `TESTING.md`

**Step 1: Create backend README**

Create `backend/README.md`:
```markdown
# TruChain Backend

Express server providing IPFS upload/download services for TruChain.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
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

## API Endpoints

### POST /api/ipfs/upload
Upload video file, compute SHA-256 hash, upload to IPFS.

**Request:** multipart/form-data with `video` field

**Response:**
```json
{
  "hash": [/* 32-byte array */],
  "cid": "QmXxx..."
}
```

### GET /api/ipfs/download/:cid
Download video from IPFS by CID.

**Response:** Video file stream

## Development

- Build: `npm run build`
- Start production: `npm start`
```

**Step 2: Create testing guide**

Create `TESTING.md` in worktree root:
```markdown
# TruChain Testing Guide

## Prerequisites

1. Phantom wallet installed and set to Devnet
2. Devnet SOL in your wallet (airdrop from faucet)
3. Backend and frontend running

## Setup

### Backend
```bash
cd backend
npm install
npm run dev  # Runs on port 3001
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on port 5173
```

## Test Flow

### 1. Admin Registration

1. Connect wallet configured as ADMIN (set in frontend/.env)
2. You should see "Admin Panel"
3. Register an official:
   - Official ID: 1
   - Name: "Test Official"
   - Authority: [wallet address for official]
   - Endorsers: [3 wallet addresses]
4. Verify transaction succeeds
5. Check official appears in table

### 2. Official Upload

1. Connect wallet that matches the authority you set
2. You should see "Official Panel"
3. Upload a test video file (any video format)
4. Wait for upload and blockchain registration
5. Verify video appears in table with "Unverified" status

### 3. Endorser Verification

1. Connect wallet that matches one of the endorsers
2. You should see "Endorser Panel"
3. Check "Pending Videos" section shows the video
4. Click "Vote Authentic" or "Vote Fake"
5. Verify transaction succeeds
6. Status should update after enough votes (2-of-3)

### 4. Endorser File Verification

1. As endorser, go to "Verify Uploaded File" section
2. Upload the same video file the official uploaded
3. Click "Verify File"
4. Should show "Match found!"
5. Can vote from here as well

## Expected Behavior

- Admin wallet: Shows only Admin Panel
- Official authority wallet: Shows only Official Panel
- Endorser wallet: Shows only Endorser Panel
- Other wallets: Shows "User View" (not implemented yet)

## Troubleshooting

### "Program not initialized"
- Check wallet is connected
- Check VITE_PROGRAM_ID in frontend/.env matches deployed program

### "Failed to upload video"
- Check backend is running on port 3001
- Check VITE_BACKEND_URL in frontend/.env
- Check file size is under 500MB

### "Failed to register official"
- Ensure connected wallet matches VITE_ADMIN_WALLET
- Check all endorser addresses are valid and unique
- Ensure you have enough SOL for transaction fees

### Role detection shows wrong role
- Check on-chain data with Solana explorer
- Verify wallet addresses match exactly
- Try disconnecting and reconnecting wallet
```

**Step 3: Commit**

```bash
git add backend/README.md TESTING.md
git commit -m "docs: add backend README and testing guide"
```

---

## Summary

This plan implements the complete TruChain frontend and backend with:

1. **Backend:** Express server with IPFS upload/download and video hashing
2. **Frontend:** Role-based UI with auto-detection (Admin/Official/Endorser)
3. **Integration:** Anchor program interaction for all on-chain operations
4. **Testing:** Clear testing guide for all roles

**Key Files Created:**
- Backend: `backend/src/` (index, routes, services, config)
- Frontend: `frontend/src/hooks/` (useAnchorProgram, useRoleDetection)
- Frontend: `frontend/src/services/` (solana, api)
- Frontend: `frontend/src/components/` (AdminPanel, OfficialPanel, EndorserPanel)

**Next Steps:**
1. Test end-to-end flow on Devnet
2. Add error handling improvements
3. Implement user feed view (future)
4. Add video preview in panels
5. Improve styling/UX
