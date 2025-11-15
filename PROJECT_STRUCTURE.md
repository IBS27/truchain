# TruChain - Project Structure

This document outlines the expected directory structure for the complete project.

```
truchain/
├── CLAUDE.md                    # Main project context (you are here)
├── PROJECT_STRUCTURE.md         # This file
├── README.md                    # User-facing documentation
│
├── programs/                    # Solana/Anchor programs
│   └── truchain/
│       ├── Cargo.toml
│       ├── Xargo.toml
│       └── src/
│           ├── lib.rs           # Main program entry
│           ├── state/           # Account structures
│           │   ├── mod.rs
│           │   ├── official.rs  # Official account
│           │   └── video.rs     # Video account
│           ├── instructions/    # Program instructions
│           │   ├── mod.rs
│           │   ├── register_official.rs
│           │   ├── add_endorser.rs
│           │   ├── register_video.rs
│           │   └── endorse_video.rs
│           └── errors.rs        # Custom errors
│
├── tests/                       # Anchor integration tests
│   └── truchain.ts
│
├── frontend/                    # React + TypeScript app
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts          # or webpack/CRA config
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── pages/
│       │   ├── portal/
│       │   │   ├── OfficialPortal.tsx    # For officials to upload videos
│       │   │   └── EndorserPortal.tsx    # For endorsers to vote
│       │   └── feed/
│       │       ├── FeedPage.tsx          # Social feed of clips
│       │       └── VerifyModal.tsx       # Clip verification modal
│       ├── components/
│       │   ├── WalletConnect.tsx         # Phantom wallet connection
│       │   ├── VideoUpload.tsx           # Video upload component
│       │   ├── ClipCard.tsx              # Individual clip in feed
│       │   ├── StatusBadge.tsx           # Authentic/Disputed/Unverified badge
│       │   ├── EndorsementVoting.tsx     # Endorser vote buttons
│       │   └── FlagButtons.tsx           # Social flag buttons
│       ├── hooks/
│       │   ├── useWallet.ts              # Wallet connection hook
│       │   ├── useSolanaProgram.ts       # Interact with Solana program
│       │   └── useIPFS.ts                # IPFS operations
│       ├── services/
│       │   ├── api.ts                    # Backend API client
│       │   ├── solana.ts                 # Solana program interface
│       │   └── ipfs.ts                   # IPFS client
│       ├── types/
│       │   ├── accounts.ts               # Solana account types
│       │   └── api.ts                    # API response types
│       └── utils/
│           ├── hash.ts                   # File hashing utilities
│           └── constants.ts              # Config constants
│
├── backend/                     # Node.js backend
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts             # Server entry point
│       ├── config/
│       │   └── database.ts      # DB connection config
│       ├── routes/
│       │   ├── ipfs.ts          # IPFS upload endpoints
│       │   ├── feed.ts          # Feed/clips endpoints
│       │   ├── flags.ts         # Social flags endpoints
│       │   └── match.ts         # AI matching endpoints
│       ├── services/
│       │   ├── ipfs.service.ts  # IPFS integration
│       │   ├── ai.service.ts    # AI/STT/matching logic
│       │   └── db.service.ts    # Database operations
│       ├── models/
│       │   ├── Clip.ts          # Clip model
│       │   ├── Flag.ts          # Flag model
│       │   └── Transcript.ts    # Video transcript model
│       └── utils/
│           ├── hash.ts          # File hashing (shared with frontend)
│           └── stt.ts           # Speech-to-text utilities
│
├── scripts/                     # Deployment and utility scripts
│   ├── deploy-program.sh        # Deploy Solana program
│   ├── init-officials.ts        # Bootstrap initial officials
│   └── seed-data.ts             # Seed test data
│
├── migrations/                  # Database migrations (if using proper DB)
│   └── 001_initial_schema.sql
│
├── .env.example                 # Environment variables template
├── Anchor.toml                  # Anchor configuration
└── package.json                 # Workspace root
```

## Key Directories Explained

### `/programs/truchain`
Solana program written in Rust using Anchor framework. Contains:
- Account structures (Official, Video)
- Instructions (register_official, add_endorser, register_video, endorse_video)
- Business logic for endorsement voting and status updates

### `/frontend`
React + TypeScript single-page application with two main sections:
- **Portal** (`/portal/official`, `/portal/endorser`): For officials and endorsers
- **Feed** (`/feed`): Social media-style feed for regular users

### `/backend`
Node.js (TypeScript) backend providing:
- IPFS upload service
- AI clip-matching endpoints
- Social flags API
- Database operations

### `/tests`
Anchor integration tests for the Solana program.

### `/scripts`
Deployment and utility scripts for program deployment and data seeding.

## Environment Variables

Create a `.env` file in the root (copy from `.env.example`):

```bash
# Solana
SOLANA_NETWORK=devnet  # or localnet, mainnet-beta
PROGRAM_ID=<deployed_program_id>
OFFICIAL_WALLET=<official_wallet_pubkey>

# IPFS
IPFS_API_URL=http://localhost:5001  # or Infura/Pinata
IPFS_GATEWAY=http://localhost:8080

# Backend
BACKEND_PORT=3001
DATABASE_URL=./truchain.db  # SQLite path or Postgres URL

# AI (optional)
OPENAI_API_KEY=<key>  # if using OpenAI Whisper API
WHISPER_MODEL=base    # or tiny, small, medium, large

# Frontend
VITE_BACKEND_URL=http://localhost:3001
VITE_SOLANA_NETWORK=devnet
```

## Getting Started

1. **Install Dependencies**:
   ```bash
   # Install Anchor (Solana program framework)
   cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
   avm install latest
   avm use latest

   # Install Node dependencies
   npm install  # or yarn install
   ```

2. **Build Solana Program**:
   ```bash
   anchor build
   ```

3. **Deploy to Devnet**:
   ```bash
   anchor deploy --provider.cluster devnet
   ```

4. **Start Backend**:
   ```bash
   cd backend
   npm run dev
   ```

5. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## Development Workflow

1. **Program Changes**: Edit `/programs/truchain/src/*` → `anchor build` → `anchor deploy`
2. **Frontend Changes**: Edit `/frontend/src/*` → Hot reload
3. **Backend Changes**: Edit `/backend/src/*` → Restart server (or use nodemon)
4. **Database Changes**: Create migration in `/migrations/` → Run migration

## Testing

```bash
# Test Solana program
anchor test

# Test backend
cd backend && npm test

# Test frontend
cd frontend && npm test
```
