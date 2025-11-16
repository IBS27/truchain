# TruChain Frontend & Backend Design

**Date:** 2025-11-15
**Status:** Approved

## Overview

Design for the TruChain video authenticity verification system frontend and backend, implementing role-based UI with automatic role detection, IPFS integration, and Solana program interaction.

---

## System Architecture

### Components

1. **Frontend (React + TypeScript + Vite)**
   - Single-page app with wallet connection
   - Automatic role detection on wallet connect
   - Conditional UI rendering based on role (Admin/Official/Endorser)
   - Uses `@coral-xyz/anchor` to interact with Solana program
   - Direct communication with backend for IPFS operations

2. **Backend (Node.js + Express)**
   - `/api/ipfs/upload` - Accepts video file, computes SHA-256 hash, uploads to IPFS, returns `{ hash, cid }`
   - `/api/ipfs/download/:cid` - Fetches video from IPFS for endorser verification
   - Uses `ipfs-http-client` to connect to public IPFS gateway (Infura)
   - Uses `crypto` module for SHA-256 hashing

3. **Solana Program (Anchor/Rust)**
   - Already deployed with IDL available
   - Three instructions: `registerOfficial`, `registerVideo`, `endorseVideo`

### Data Flow

- Frontend detects wallet role by querying on-chain accounts
- Admin registers officials with their authority wallet + 3 endorser wallets
- Officials upload videos → backend returns hash/CID → frontend calls `registerVideo`
- Endorsers browse pending videos or upload file to verify → vote on-chain via `endorseVideo`

---

## Frontend Structure

### Directory Structure

```
frontend/src/
├── components/
│   ├── WalletConnect.tsx          # Wallet connection UI
│   ├── AdminPanel.tsx              # Register official form
│   ├── OfficialPanel.tsx           # Video upload for officials
│   ├── EndorserPanel.tsx           # Video list + verify/vote
│   └── VideoCard.tsx               # Reusable video display component
├── hooks/
│   ├── useWallet.ts                # Wallet connection hook
│   ├── useAnchorProgram.ts         # Anchor program instance + methods
│   └── useRoleDetection.ts         # Detects wallet role from on-chain data
├── services/
│   ├── solana.ts                   # Solana/Anchor helper functions
│   └── api.ts                      # Backend API calls (IPFS)
├── anchor/
│   └── idl.ts                      # Program IDL (already exists)
└── App.tsx                         # Main app with conditional rendering
```

### Role Detection

**Logic (`useRoleDetection` hook):**
1. Check if wallet address matches hardcoded `ADMIN_WALLET` constant
2. Query all `Official` accounts, check if wallet is any official's `authority`
3. Query all `Official` accounts, check if wallet is in any `endorsers` array
4. Return role: `'admin' | 'official' | 'endorser' | 'user'`

**Note:** No wallets have multiple roles (mutually exclusive).

### App.tsx Flow

```tsx
const { publicKey } = useWallet();
const { role, assignedOfficials } = useRoleDetection(publicKey);

return (
  <div>
    <WalletConnect />
    {role === 'admin' && <AdminPanel />}
    {role === 'official' && <OfficialPanel />}
    {role === 'endorser' && <EndorserPanel officials={assignedOfficials} />}
  </div>
);
```

---

## Component Specifications

### AdminPanel.tsx

**Purpose:** Register new officials on-chain.

**UI Elements:**
- Form with fields:
  - Official ID (number input)
  - Official Name (text input, max 32 bytes)
  - Authority Wallet Address (text input, validates Pubkey)
  - 3 Endorser Wallet Addresses (text inputs, validates unique Pubkeys)
- Submit button calls `registerOfficial` instruction via Anchor
- Success/error messages
- Table listing previously registered officials (query all Official accounts)

### OfficialPanel.tsx

**Purpose:** Upload videos and register them on-chain.

**Upload Flow:**
1. User selects video file via file input
2. Upload to backend `/api/ipfs/upload`
3. Backend returns `{ hash, cid }`
4. Call `registerVideo(videoHash, ipfsCid)` via Anchor
5. Show confirmation with on-chain transaction link

**UI Elements:**
- File input for video upload (accepts video formats)
- Upload progress indicator
- Table showing official's registered videos:
  - IPFS CID (link to IPFS gateway)
  - Video hash
  - Status (Unverified/Authentic/Disputed)
  - Vote counts
  - Timestamp

### EndorserPanel.tsx

**Purpose:** Verify and vote on official videos (hybrid approach).

**Section 1: Pending Videos List**
- Query videos for assigned officials where endorser hasn't voted yet
- Show video player (fetch from IPFS via backend)
- "Vote Authentic" / "Vote Fake" buttons → calls `endorseVideo(isAuthentic: bool)`

**Section 2: Verify Uploaded File**
- File upload input
- Upload to backend to compute hash
- Search on-chain for matching video hash
- If found: show video details + vote buttons
- If not found: show "No match found" message

---

## Backend Specification

### Directory Structure

```
backend/
├── src/
│   ├── index.ts              # Express server setup
│   ├── routes/
│   │   └── ipfs.ts           # IPFS route handlers
│   ├── services/
│   │   ├── ipfs.service.ts   # IPFS client wrapper
│   │   └── hash.service.ts   # Video hashing utilities
│   └── config.ts             # IPFS gateway config
├── uploads/                  # Temporary video storage
└── package.json
```

### Dependencies

- `express` - Web framework
- `multer` - File upload handling
- `ipfs-http-client` - IPFS client
- `crypto` (built-in) - SHA-256 hashing
- `cors` - Enable frontend to call API

### API Endpoints

#### POST `/api/ipfs/upload`

**Accepts:** `multipart/form-data` with video file

**Process:**
1. Save file temporarily with multer
2. Compute SHA-256 hash of file bytes → returns 32-byte array
3. Upload to IPFS via ipfs-http-client → get CID
4. Delete temporary file
5. Return `{ hash: number[], cid: string }`

**Error Handling:**
- File size limits (500MB max)
- Invalid formats
- IPFS upload failures

#### GET `/api/ipfs/download/:cid`

**Accepts:** IPFS CID as URL parameter

**Process:**
1. Fetch file from IPFS using CID
2. Stream video content to response

**Usage:** Frontend uses this to display videos from IPFS

### Configuration

- IPFS gateway: `https://ipfs.infura.io:5001` (or similar public gateway)
- Max file size: 500MB (configurable)
- Port: 3001

---

## Solana/Anchor Integration

### Frontend Dependencies

```json
{
  "@coral-xyz/anchor": "^0.30.0"
}
```

### Anchor Program Setup

**`useAnchorProgram` hook:**
```typescript
import { Program, AnchorProvider } from '@coral-xyz/anchor';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { Truchain } from '../anchor/idl';
import idl from '../anchor/idl';

// Returns initialized program instance
const program = new Program<Truchain>(idl, provider);
```

### Integration Functions (`services/solana.ts`)

#### Role Detection Queries

- `getAllOfficials()` - Fetch all Official accounts using `program.account.official.all()`
- `getVideosForOfficial(officialPubkey)` - Fetch Video accounts filtered by official
- `checkIsAdmin(wallet)` - Compare against hardcoded admin address
- `checkIsOfficialAuthority(wallet)` - Check if wallet matches any official's authority
- `checkIsEndorser(wallet)` - Check if wallet is in any official's endorsers array

#### Transaction Functions

- `registerOfficial(officialId, name, authority, endorsers)` - Calls program instruction
- `registerVideo(officialPubkey, videoHash, ipfsCid)` - Derives Video PDA, calls instruction
- `endorseVideo(officialPubkey, videoHash, isAuthentic)` - Calls endorsement instruction

#### Account Derivation

- Official PDA: `["official", officialId.toBytes()]`
- Video PDA: `["video", officialPubkey, videoHash]`

### Error Handling

- Parse Anchor errors (codes 6000-6009 from IDL)
- Display user-friendly error messages
- Handle transaction failures:
  - Insufficient SOL for transaction fees
  - Rejected transactions
  - Network errors

---

## Setup & Dependencies

### Frontend New Dependencies

```bash
npm install @coral-xyz/anchor
```

### Backend New Project

```bash
mkdir backend && cd backend
npm init -y
npm install express multer ipfs-http-client cors
npm install -D typescript @types/express @types/multer @types/cors ts-node nodemon
```

### Environment Variables

#### Frontend (`.env`)

```
VITE_SOLANA_NETWORK=devnet
VITE_PROGRAM_ID=FGkp4CpRBNDQz2h5idbhbX7cHkbggpsUsF7enLiQE2nT
VITE_ADMIN_WALLET=<admin_public_key>
VITE_BACKEND_URL=http://localhost:3001
```

#### Backend (`.env`)

```
PORT=3001
IPFS_HOST=ipfs.infura.io
IPFS_PORT=5001
IPFS_PROTOCOL=https
MAX_FILE_SIZE=524288000  # 500MB in bytes
```

### Development Workflow

1. Start backend: `cd backend && npm run dev` (runs on port 3001)
2. Start frontend: `cd frontend && npm run dev` (runs on port 5173)
3. Connect Phantom wallet (ensure on Devnet)
4. Admin registers officials first
5. Officials upload videos
6. Endorsers verify and vote

### IPFS Gateway Note

- **For hackathon:** Use Infura's public gateway (no API key needed for basic usage)
- **For production:** Consider Pinata or web3.storage with API keys for better reliability and pinning guarantees

---

## Design Decisions

1. **Auto role detection** - Validates roles against blockchain, prevents unauthorized access
2. **Backend IPFS service** - Keeps API keys secure, centralizes file processing
3. **Single page with conditional sections** - Simple UX since wallets don't have multiple roles
4. **Hybrid endorser workflow** - Browse pending videos (proactive) + upload to verify (reactive)
5. **Minimal dependencies** - Express + public IPFS gateway for quick hackathon setup

---

## Next Steps

1. Set up backend Node.js project with IPFS integration
2. Add @coral-xyz/anchor to frontend dependencies
3. Implement role detection hooks and services
4. Build AdminPanel, OfficialPanel, EndorserPanel components
5. Test end-to-end flow on Devnet
