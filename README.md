# TruChain

**Blockchain-based Video Authenticity Verification for Elected Officials**

TruChain is a decentralized system designed to combat misinformation by establishing verifiable provenance for videos of elected officials (presidents, governors, senators, and representatives). Rather than attempting to detect deepfakes after they've been created, TruChain creates an immutable chain of custody for official videos at their source.

## The Problem

In an era of sophisticated video manipulation and deepfakes, determining whether a video clip of an elected official is authentic has become increasingly difficult. Traditional approaches rely on forensic analysis of suspicious videos, but this reactive approach struggles to keep pace with advancing AI capabilities.

## Our Solution

TruChain takes a different approach: **source-level provenance**.

- **Officials** register full, unedited videos of speeches and public appearances on the blockchain
- **Endorsers** (whitelisted verifiers like press pools, official channels) validate these videos
- **Users** can verify short clips they encounter by matching them against authenticated source videos
- **Community feedback** provides additional context about potentially misleading clips

## Core Architecture

### Three-Layer System

**1. Blockchain Layer (Solana)**
- Immutable registry of official videos
- Cryptographic hashes ensure content hasn't been altered
- Endorser voting system establishes authenticity
- Public, transparent verification status

**2. AI Matching Layer (Off-chain)**
- Speech-to-text transcription of registered videos
- Intelligent matching of short clips to full source videos
- Timestamp identification for context verification
- Scalable processing without blockchain overhead

**3. Social Feedback Layer (Web2)**
- Community flags for context (real/fake/misleading/out-of-context)
- Aggregated reputation scores
- Human judgment for nuanced interpretation
- Lightweight storage for rapid iteration

## How It Works

### For Officials (or Their Media Teams)

1. Upload full speech/appearance videos to the portal
2. Video is hashed and stored on IPFS (decentralized storage)
3. Hash and IPFS address are registered on Solana blockchain
4. Creates an immutable record tied to the official's verified wallet

### For Endorsers (Whitelisted Verifiers)

1. Receive official videos through traditional channels
2. Upload received video to verification portal
3. System computes hash and compares to on-chain registry
4. If match found, endorser votes "authentic" or "mismatch"
5. Votes are recorded on-chain, updating video status

**Status Levels:**
- **Authentic**: Sufficient endorser votes confirming legitimacy
- **Disputed**: Conflicting votes or mismatch reports
- **Unverified**: Insufficient endorsement data

### For Regular Users (Social Feed)

1. Browse short video clips in the social feed
2. Click "Verify this clip" on any content
3. AI matches clip audio/transcript against authenticated videos
4. System displays:
   - Original full video (if match found)
   - On-chain verification status
   - Which endorsers have validated it
   - Community flags and context
5. Users can add their own context flags

## Technical Stack

### Blockchain
- **Platform**: Solana (high throughput, low cost)
- **Smart Contracts**: Rust + Anchor framework
- **Wallet Integration**: Phantom wallet via @solana/web3.js

### Frontend
- **Framework**: React + TypeScript
- **Structure**:
  - Portal section (Officials & Endorsers)
  - Feed section (Social verification)
- **Web3 Integration**: Anchor + Phantom wallet adapters

### Backend
- **Runtime**: Node.js (TypeScript)
- **Services**:
  - IPFS upload and pinning
  - AI clip matching endpoints
  - Social flags REST API
- **Database**: SQLite (expandable to PostgreSQL)

### Storage & AI
- **Decentralized Storage**: IPFS
- **AI Processing**:
  - Speech-to-text (Whisper-based)
  - Transcript search and matching
  - Timestamp alignment

## Smart Contract Design

### Official Account
Represents an elected official with:
- Unique official ID
- Name and authority (wallet address)
- List of approved endorsers

### Video Account
Created as a Program Derived Address (PDA) from `(official_id, video_hash)`:
- Reference to official
- Cryptographic hash of video content
- IPFS content identifier (CID)
- Registration timestamp
- Vote counts (authentic/fake)
- Current status (Unverified/Authentic/Disputed)

### Key Instructions

**register_video**: Officials register new videos
- Only callable by official's authority wallet
- Creates Video account with initial Unverified status
- Emits event for off-chain indexing

**endorse_video**: Endorsers vote on authenticity
- Only callable by whitelisted endorsers
- Updates vote tallies
- Auto-updates status based on vote thresholds
- Prevents double-voting

**add_endorser**: Officials designate trusted verifiers
- Adds endorser to official's approved list
- Endorsers can then vote on that official's videos

## Security Model

### On-Chain Security
- Only official's authority wallet can register videos
- Only pre-approved endorsers can vote
- Vote thresholds prevent single-point manipulation
- All transactions are publicly auditable

### Content Security
- Cryptographic hashing ensures content integrity
- IPFS provides content-addressable storage
- Endorsers verify actual received content, not just metadata

### Off-Chain Security
- AI matching operates on authenticated videos only
- Social flags are supplementary context, not authoritative
- Clear separation between protocol layer (blockchain) and community layer (Web2)

## Key Design Decisions

### Why Solana?
- High transaction throughput for endorser votes
- Low transaction costs (important for frequent verifications)
- Fast finality (sub-second confirmation)
- Growing ecosystem of tools and wallets

### Why IPFS?
- Decentralized storage prevents single point of failure
- Content-addressable: hash of content is its address
- Can't be altered without changing the address
- Relatively mature ecosystem with pinning services

### Why Off-Chain AI?
- Video processing is computationally expensive
- Doesn't need blockchain immutability
- Allows for algorithm improvements without protocol changes
- Keeps blockchain lean and focused on provenance

### Why Separate Social Layer?
- Community context doesn't need permanent storage
- Allows for moderation and removal if needed
- More flexible for experimentation
- Reduces blockchain bloat and costs

## Use Cases

**Political Campaigns**: Verify opponent video clips before sharing
**Journalists**: Confirm source authenticity before reporting
**Fact-Checkers**: Quickly validate or debunk viral clips
**Social Platforms**: Integrate verification API for context labels
**Citizens**: Make informed decisions based on verified information

## Project Status

TruChain was developed as a hackathon project demonstrating the viability of source-level provenance for video authenticity. The core functionality is operational, with room for production hardening, scaling improvements, and additional features.

## Philosophy

TruChain doesn't try to detect every possible deepfake or manipulation. Instead, it establishes a foundation of trust: verified, authentic source material that can be referenced. When a clip surfaces, the question changes from "is this fake?" to "does this match a verified source?"

This approach has limitations—it can't verify unregistered content, and context still matters—but it creates a verifiable baseline that didn't exist before.

## Future Directions

- Multi-chain support for broader adoption
- Enhanced AI matching with visual recognition
- Mobile applications for on-the-go verification
- API partnerships with social media platforms
- Expanded to other public figures beyond elected officials
- Integration with browser extensions for inline verification