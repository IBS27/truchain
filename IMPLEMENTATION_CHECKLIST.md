# TruChain - Implementation Checklist

This checklist breaks down the project into actionable tasks for hackathon development.

## Phase 1: Project Setup & Infrastructure

### 1.1 Solana Program Setup
- [ ] Initialize Anchor workspace
  ```bash
  anchor init truchain-program
  ```
- [ ] Configure `Anchor.toml` for devnet
- [ ] Setup program ID and deploy keys

### 1.2 Backend Setup
- [ ] Create `backend/` directory
- [ ] Initialize Node.js + TypeScript project
  ```bash
  mkdir backend && cd backend
  npm init -y
  npm install express cors dotenv
  npm install -D typescript @types/node @types/express ts-node nodemon
  ```
- [ ] Setup basic Express server structure
- [ ] Configure environment variables (`.env` file)

### 1.3 Frontend Dependencies
- [ ] Install Solana Web3 dependencies
  ```bash
  cd frontend
  npm install @solana/web3.js @solana/wallet-adapter-react @solana/wallet-adapter-react-ui @solana/wallet-adapter-wallets @solana/wallet-adapter-base
  ```
- [ ] Install routing
  ```bash
  npm install react-router-dom
  npm install -D @types/react-router-dom
  ```
- [ ] Install UI library (optional, for faster development)
  ```bash
  npm install tailwindcss @headlessui/react
  # or: npm install @mui/material @emotion/react @emotion/styled
  ```

### 1.4 IPFS Setup
- [ ] Choose IPFS provider (local node, Infura, or Pinata)
- [ ] Install IPFS dependencies
  ```bash
  # Backend
  cd backend
  npm install ipfs-http-client
  ```
- [ ] Configure IPFS connection in backend

### 1.5 Database Setup
- [ ] Choose database (SQLite for simplicity, or Postgres)
- [ ] Install database dependencies
  ```bash
  cd backend
  npm install better-sqlite3  # for SQLite
  # or: npm install pg  # for Postgres
  ```
- [ ] Create initial schema (see CLAUDE.md for schema)
- [ ] Setup migration scripts (optional for hackathon)

---

## Phase 2: Solana Program (Anchor)

### 2.1 Define Account Structures
- [ ] Create `programs/truchain/src/state/official.rs`
  - Official account structure (official_id, name, authority, endorsers)
- [ ] Create `programs/truchain/src/state/video.rs`
  - Video account structure (official, video_hash, ipfs_cid, votes, status)
  - VideoStatus enum (Unverified, Authentic, Disputed)

### 2.2 Implement Instructions
- [ ] `register_official`
  - Admin-only instruction to create Official account
  - Initialize official_id, name, authority
- [ ] `add_endorser_for_official`
  - Add endorser Pubkey to Official's endorser list
  - Only authority can call
- [ ] `register_video`
  - Create Video PDA from (official_id, video_hash)
  - Store ipfs_cid, timestamp
  - Initialize with Unverified status
  - Only official's authority can call
- [ ] `endorse_video`
  - Verify caller is in endorser list
  - Update authentic_votes or fake_votes
  - Recalculate status based on threshold (e.g., 2-of-3)
  - Emit event for vote

### 2.3 Add Error Handling
- [ ] Define custom errors in `errors.rs`
  - UnauthorizedOfficial
  - UnauthorizedEndorser
  - VideoAlreadyRegistered
  - VideoNotFound
  - etc.

### 2.4 Testing
- [ ] Write integration tests in `tests/truchain.ts`
  - Test register_official
  - Test add_endorser
  - Test register_video
  - Test endorse_video (authentic and fake votes)
  - Test status transitions
- [ ] Run tests: `anchor test`

### 2.5 Deploy
- [ ] Build program: `anchor build`
- [ ] Deploy to devnet: `anchor deploy --provider.cluster devnet`
- [ ] Save program ID to `.env` and `Anchor.toml`

---

## Phase 3: Backend API

### 3.1 IPFS Service
- [ ] Create `backend/src/services/ipfs.service.ts`
- [ ] Implement `uploadToIPFS(file)` → returns `{ hash, cid }`
- [ ] Implement `downloadFromIPFS(cid)` → returns file buffer
- [ ] Create route `POST /api/ipfs/upload`

### 3.2 Database Service
- [ ] Create `backend/src/services/db.service.ts`
- [ ] Initialize database connection
- [ ] Implement CRUD for clips
- [ ] Implement CRUD for flags
- [ ] Implement CRUD for transcripts

### 3.3 AI / Matching Service (Simplified)
- [ ] Create `backend/src/services/ai.service.ts`
- [ ] **Option A - Full Implementation**:
  - Install Whisper or STT library
  - Implement `transcribeVideo(filePath)` → text
  - Implement `matchClipToOfficialVideos(clipTranscript)` → match result
- [ ] **Option B - Mocked for Hackathon**:
  - Create fake transcript data
  - Implement simple substring matching
  - Return mock match results
- [ ] Create route `POST /api/match-clip`

### 3.4 Social API Routes
- [ ] Create `backend/src/routes/feed.ts`
  - `GET /api/feed` - List all clips with flag counts
  - `POST /api/clips` - Create new clip (for seeding data)
- [ ] Create `backend/src/routes/flags.ts`
  - `GET /api/flags/:clip_id` - Get flag counts for clip
  - `POST /api/flags` - Add user flag to clip
  - `GET /api/flags/:clip_id/summary` - Get aggregated flag data

### 3.5 Server Setup
- [ ] Create `backend/src/index.ts`
- [ ] Setup Express app with CORS
- [ ] Register all routes
- [ ] Add error handling middleware
- [ ] Start server on port 3001

---

## Phase 4: Frontend - Portal (Officials & Endorsers)

### 4.1 Wallet Integration
- [ ] Create `frontend/src/hooks/useWallet.ts`
- [ ] Setup Phantom wallet adapter in `App.tsx`
- [ ] Create `WalletConnect.tsx` component
- [ ] Test wallet connection/disconnection

### 4.2 Solana Program Interface
- [ ] Create `frontend/src/services/solana.ts`
- [ ] Load program IDL
- [ ] Implement `registerVideo(officialId, videoHash, ipfsCid)`
- [ ] Implement `endorseVideo(officialId, videoHash, isAuthentic)`
- [ ] Implement `fetchVideoAccount(videoHash)` → Video data
- [ ] Implement `fetchOfficialAccount(officialId)` → Official data

### 4.3 Official Portal
- [ ] Create `frontend/src/pages/portal/OfficialPortal.tsx`
- [ ] Build video upload form
  - File input
  - Compute hash locally (use crypto.subtle or library)
  - Upload to backend IPFS endpoint
  - Display CID and hash
- [ ] Call `registerVideo` on Solana
- [ ] Display list of registered videos with status
- [ ] Show vote counts for each video

### 4.4 Endorser Portal
- [ ] Create `frontend/src/pages/portal/EndorserPortal.tsx`
- [ ] Build video verification interface
  - File input
  - Compute hash locally
  - Search on-chain for matching video_hash
  - Display match result (official name, video metadata)
- [ ] Create voting buttons (Authentic / Fake)
- [ ] Call `endorseVideo` on Solana
- [ ] Display list of videos needing endorsement
- [ ] Show endorsement history

### 4.5 Portal Layout & Routing
- [ ] Setup React Router in `App.tsx`
- [ ] Create routes:
  - `/portal/official`
  - `/portal/endorser`
- [ ] Create navigation/header component
- [ ] Add role detection (based on wallet or manual selection)

---

## Phase 5: Frontend - Feed (Social App)

### 5.1 Feed Page
- [ ] Create `frontend/src/pages/feed/FeedPage.tsx`
- [ ] Fetch clips from backend API (`GET /api/feed`)
- [ ] Display scrollable list of clips
- [ ] Create `ClipCard.tsx` component
  - Video player
  - Title and metadata
  - Flag counts (real/fake/misleading/out-of-context)
  - "Verify" button

### 5.2 Verification Modal
- [ ] Create `frontend/src/pages/feed/VerifyModal.tsx`
- [ ] When "Verify" clicked:
  - Call backend `POST /api/match-clip` with clip ID or file
  - Display loading state
- [ ] If match found:
  - Display matched official video (from IPFS or preview)
  - Fetch on-chain status from Solana
  - Show status badge (Authentic/Disputed/Unverified)
  - Show vote counts and endorser list
- [ ] If no match:
  - Display "No official source found"

### 5.3 Flagging System
- [ ] Create `FlagButtons.tsx` component
- [ ] Add flag buttons: Real / Fake / Misleading / Out of Context
- [ ] Call backend `POST /api/flags` when user flags
- [ ] Update local state to reflect new flag counts
- [ ] Optionally require wallet connection for flagging (or allow anonymous)

### 5.4 Feed Routing
- [ ] Add `/feed` route in `App.tsx`
- [ ] Make feed the default landing page or add home page with navigation

---

## Phase 6: Integration & Testing

### 6.1 End-to-End Flow Testing
- [ ] **Official Flow**:
  1. Connect wallet as official
  2. Upload video
  3. Verify video appears on-chain with Unverified status
- [ ] **Endorser Flow**:
  1. Connect wallet as endorser
  2. Upload same video file
  3. Vote authentic
  4. Verify vote count increases
  5. Add 2nd endorser vote
  6. Verify status changes to Authentic
- [ ] **User Flow**:
  1. Browse feed
  2. Click "Verify" on a clip
  3. Verify match is found
  4. Verify on-chain status displays correctly
  5. Add flag
  6. Verify flag count increases

### 6.2 Error Handling
- [ ] Test wallet disconnection scenarios
- [ ] Test invalid video hash
- [ ] Test unauthorized endorsement attempt
- [ ] Test duplicate video registration
- [ ] Test backend API errors (network failures, IPFS down, etc.)

### 6.3 UI/UX Polish
- [ ] Add loading states for all async operations
- [ ] Add error messages and toasts
- [ ] Add success confirmations
- [ ] Ensure responsive design (mobile-friendly)
- [ ] Add helpful tooltips and explanations

---

## Phase 7: Demo Preparation

### 7.1 Seed Data
- [ ] Create script to seed database with sample clips
- [ ] Create 2-3 official videos and register them on-chain
- [ ] Have endorsers vote on them (mix of Authentic/Disputed/Unverified)
- [ ] Create corresponding short clips in the feed

### 7.2 Documentation
- [ ] Update `README.md` with:
  - Project description
  - Setup instructions
  - How to run (program, backend, frontend)
  - Demo walkthrough
- [ ] Add screenshots or video demo
- [ ] Document environment variables

### 7.3 Deployment (Optional)
- [ ] Deploy Solana program to devnet (already done in Phase 2)
- [ ] Deploy backend to a hosting service (Heroku, Railway, etc.)
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Configure IPFS for production (Pinata/Infura)

---

## Simplified Hackathon Path (If Time is Limited)

If you need to cut scope, here's the minimal viable demo:

### Must-Have (Core Demo Flow)
✅ Solana program with register_video and endorse_video
✅ Official portal: upload video → IPFS → register on-chain
✅ Endorser portal: verify hash → vote
✅ Feed: display pre-seeded clips
✅ Verification: mock matching (hardcode clip → official video mapping)
✅ Display on-chain status

### Nice-to-Have (Add if Time Permits)
- Real AI/STT matching
- User flagging system
- Multiple officials and videos
- Wallet-based role detection
- Production deployment

### Can Skip for Hackathon
- Perfect error handling
- Comprehensive tests
- Beautiful UI (use unstyled or basic components)
- Database migrations
- Advanced IPFS pinning

---

## Success Criteria

Your demo should show:
1. ✅ **Source-level provenance**: Official uploads video → stored on IPFS → registered on Solana
2. ✅ **Endorsement voting**: Endorsers verify and vote → status changes to Authentic
3. ✅ **Clip verification**: User sees clip → verifies against official source → sees on-chain status
4. ✅ **Working end-to-end**: All three roles can interact with the system

Good luck! 🚀
