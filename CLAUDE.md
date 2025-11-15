# TruChain - Video Authenticity Verification System

## Project Overview

A blockchain-based system for verifying the authenticity of videos of elected officials (president, governors, senators, representatives) using source-level provenance rather than on-the-fly forensics.

**Core Concept**: Blockchain for provenance, AI for clip-to-source matching, social layer for human judgment about context.

---

## Tech Stack

### Blockchain
- **Chain**: Solana
- **Smart Contracts**: Rust using Anchor framework
- **Wallet**: Phantom wallet
- **Web3 Client**: @solana/web3.js + Anchor/Phantom adapters

### Frontend
- **Framework**: React + TypeScript
- **Structure**: Single app with two main sections:
  - Portal (Officials & Endorsers)
  - Feed (Social media for users)

### Backend
- **Runtime**: Node.js (TypeScript preferred)
- **Services**:
  - IPFS upload service
  - AI/clip-matching endpoints
  - Social flags + REST API
- **Database**: SQLite/Postgres (or simple file/in-memory for demo)

### Storage & AI
- **Decentralized Storage**: IPFS (with basic pinning)
- **AI Layer**: Off-chain, lightweight
  - Speech-to-text (Whisper or similar)
  - Transcript search for clip matching
  - Can be mocked/simplified for hackathon

---

## System Architecture

### Three Main Roles

#### 1. Official (Elected Official's Media Team)
**Responsibilities**:
- Upload full official speech videos to the portal
- Videos are hashed, stored on IPFS, and registered on Solana

**Flow**:
1. Upload video file via portal
2. Portal hashes the file
3. Upload to IPFS → get CID
4. Call Solana program: `register_video(official_id, video_hash, ipfs_cid)`

#### 2. Endorser (Whitelisted Verifiers)
**Responsibilities**:
- Verify that official videos they receive match what's on-chain
- Vote on authenticity

**Flow**:
1. Receive official video through normal channels
2. Upload/select file in portal
3. Portal recomputes hash and checks against on-chain data
4. If match found, submit endorsement vote:
   - `vote_authentic(video_hash)` or `vote_mismatch(video_hash)`
5. Program updates vote counts and overall status

**Status Thresholds**:
- **Authentic**: Enough "authentic" votes (e.g., 2-of-3)
- **Disputed**: Enough "fake/mismatch" votes
- **Unverified**: Not enough votes yet

#### 3. Regular User (Social App)
**Responsibilities**:
- Browse short clips of speeches
- Verify clip authenticity
- Flag clips with context feedback

**Flow**:
1. Scroll feed of short clips (20-30s segments)
2. Click "Verify this clip"
3. Frontend sends clip to backend AI endpoint
4. AI matches clip against known official videos (from IPFS + on-chain metadata)
5. If match found:
   - Display original full video
   - Show on-chain status (Authentic/Disputed/Unverified)
   - Show which endorsers voted
6. User can flag clip as:
   - Real (matches authentic source)
   - Fake (not from any authentic source)
   - Misleading / Out-of-context
7. Flags stored in Web2 DB (NOT on-chain)

---

## On-Chain Data Model (Solana/Anchor)

### Official Account
```rust
pub struct Official {
    pub official_id: u64,
    pub name: String,  // or fixed-length
    pub authority: Pubkey,  // Official's wallet
    pub endorsers: Vec<Pubkey>,  // Whitelisted endorsers
}
```

### Video Account
**PDA derived from**: `(official_id, video_hash)`

```rust
pub struct Video {
    pub official: Pubkey,  // → Official account
    pub video_hash: [u8; 32],
    pub ipfs_cid: String,  // or fixed-length bytes
    pub timestamp: i64,
    pub authentic_votes: u32,
    pub fake_votes: u32,
    pub status: VideoStatus,  // enum
}

pub enum VideoStatus {
    Unverified,
    Authentic,
    Disputed,
}
```

### Program Instructions

1. **register_official** (admin-only or bootstrap)
   - Creates a new Official account

2. **add_endorser_for_official**
   - Adds endorser Pubkey to Official's endorser list

3. **register_video(official_id, video_hash, ipfs_cid)**
   - Only official's authority can call
   - Creates Video account with Unverified status

4. **endorse_video(official_id, video_hash, vote_is_authentic: bool)**
   - Only approved endorsers can call
   - Updates vote counts
   - Updates status based on thresholds

**Security Rules**:
- Only official's authority can call `register_video`
- Only approved endorser Pubkeys can call `endorse_video`
- Status auto-updates based on vote thresholds (e.g., 2-of-3)

---

## Frontend Structure

### Directory Layout
```
frontend/
├── src/
│   ├── pages/
│   │   ├── portal/
│   │   │   ├── Official.tsx
│   │   │   └── Endorser.tsx
│   │   └── feed/
│   │       ├── Feed.tsx
│   │       └── VerifyModal.tsx
│   ├── components/
│   │   ├── WalletConnect.tsx
│   │   ├── VideoUpload.tsx
│   │   ├── ClipCard.tsx
│   │   └── StatusBadge.tsx
│   ├── hooks/
│   │   ├── useWallet.ts
│   │   ├── useSolana.ts
│   │   └── useIPFS.ts
│   └── services/
│       ├── api.ts
│       ├── solana.ts
│       └── ipfs.ts
```

### Portal Section (`/portal/official`, `/portal/endorser`)

**Features**:
- Wallet connection (Phantom via @solana/web3.js + wallet adapter)
- Role detection (based on wallet → role mapping)

**Official View**:
- Upload full video file
- Call backend to upload to IPFS → get CID and hash
- Call Solana program to `register_video`
- List registered videos + on-chain status

**Endorser View**:
- Upload/choose received file
- Check local hash vs on-chain videos for assigned officials
- If match: show "Vote authentic / Vote mismatch" buttons
- Sign and send Solana transaction to `endorse_video`
- List videos needing endorsement

### Feed Section (`/feed`)

**Features**:
- Scrollable list of short clips (from backend DB or mocked)
- Each clip shows:
  - Video player
  - Title, basic metadata
  - "Verify" button

**Verification Flow**:
- Opens modal/verification view
- Uploads or uses clip file
- Calls backend AI endpoint for matching
- Backend returns:
  - **Found**: `official_video_id`, `video_hash`, `ipfs_cid`, `timestamp`, `status`
  - **Not Found**: No matching official video
- Fetch on-chain status & endorsements
- Display status: Authentic / Disputed / Unverified
- Show social flag counts (real/fake/misleading)
- Allow user to add their own flag

---

## Backend Services

### IPFS Service
**Endpoint**: `/api/ipfs/upload`
- Accepts video file upload
- Computes hash
- Uploads to IPFS
- Returns: `{ hash, cid }`

### AI / Clip Matching Layer
**Endpoint**: `/api/match-clip`

**When official registers video**:
1. Download video from IPFS
2. Run speech-to-text (Whisper or similar)
3. Store transcript + timestamps in DB

**When user verifies clip**:
1. Run speech-to-text on clip
2. Search for matching text in transcripts of videos with `Authentic` status
3. Return best match: `official_video_id` + approximate timestamp + confidence score

**Fallback for Hackathon**:
- Mock with simple substring search on pre-made transcripts
- Or fake "matching" function for demo
- Keep interface clean for future swapping

### Social API

**Endpoints**:

`GET /api/feed`
- List clips with flags and counts

`POST /api/flags`
- Create/update user flag for a clip
- Body: `{ clip_id, flag_type: 'real' | 'fake' | 'misleading' | 'out_of_context' }`

`GET /api/flags/:clip_id`
- Get flag counts for a clip

### Database Schema

**Clips Table**:
```sql
CREATE TABLE clips (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    title TEXT,
    official_video_id TEXT,  -- if matched
    created_at TIMESTAMP
);
```

**Flags Table**:
```sql
CREATE TABLE flags (
    id INTEGER PRIMARY KEY,
    clip_id INTEGER,
    user_id TEXT,  -- optional, can be wallet address
    flag_type TEXT,  -- 'real', 'fake', 'misleading', 'out_of_context'
    created_at TIMESTAMP,
    FOREIGN KEY (clip_id) REFERENCES clips(id)
);
```

**Video Transcripts Table** (for AI matching):
```sql
CREATE TABLE video_transcripts (
    id INTEGER PRIMARY KEY,
    video_hash TEXT,
    transcript TEXT,
    timestamps TEXT,  -- JSON array of timestamp markers
    created_at TIMESTAMP
);
```

---

## Key Distinctions

### On-Chain (Protocol Authenticity Layer)
- **Who**: Officials + Endorsers only
- **What**: Video registration, hash storage, endorsement votes, status
- **Why**: Immutable, verifiable source-of-truth for official videos

### Off-Chain (Community/Social Feedback Layer)
- **Who**: Any user
- **What**: Clip flags (real/fake/misleading/out-of-context)
- **Why**: Contextual feedback, doesn't need blockchain permanence

---

## Development Priorities (Hackathon)

1. **Working end-to-end flow** over perfect architecture
2. **Simple Solana/Anchor program**:
   - No over-engineered PDAs
   - Just enough to show: registration, endorsement, status updates
3. **Clean UX with clear separation**:
   - Portal: Upload & endorse
   - Feed: Scroll & verify clips
4. **Minimal but believable AI**:
   - Simple transcript matching is fine
   - Can be mocked for demo
5. **Clear comments**:
   - Explain Solana-specific concepts (accounts, PDAs) in code comments

---

## Next Steps for Implementation

1. **Setup project structure**:
   - Initialize Anchor project for Solana program
   - Setup React + TypeScript frontend
   - Setup Node.js backend

2. **Solana Program**:
   - Define accounts (Official, Video)
   - Implement instructions (register_official, add_endorser, register_video, endorse_video)
   - Add vote threshold logic

3. **Backend**:
   - IPFS integration
   - Database setup
   - AI/matching endpoints (or mock)
   - Social API

4. **Frontend**:
   - Wallet integration
   - Portal views (Official, Endorser)
   - Feed view
   - Verification modal

5. **Integration**:
   - Connect frontend to Solana program
   - Connect frontend to backend APIs
   - Test end-to-end flows

---

## Important Notes

- This is a **hackathon project**: favor simplicity, clarity, and working demos
- Code should have clear comments, especially for Solana-specific concepts
- AI layer can be simplified or mocked
- Database can be simple (SQLite or in-memory for demo)
- Focus on demonstrating the core concept: source-level provenance via blockchain
