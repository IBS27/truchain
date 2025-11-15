# TruChain Solana Program Design

**Date:** 2025-11-15
**Status:** Approved for Implementation

## Overview

Blockchain-based video authenticity verification system using Solana for source-level provenance. Officials register videos on-chain, endorsers vote on authenticity, and users verify clips against the authenticated sources.

## Design Decisions

- **Environment:** Solana devnet (for team collaboration and persistence)
- **Vote Threshold:** 3 endorsers per official, 2-of-3 majority for status changes
- **String Storage:** Fixed-length byte arrays for predictable account sizes
- **Vote Mutability:** Immutable - endorsers vote once per video
- **Vote Tracking:** Store individual voter addresses for transparency and double-vote prevention

## Account Structures

### Official Account

```rust
#[account]
pub struct Official {
    pub official_id: u64,           // Unique ID (1, 2, 3...)
    pub name: [u8; 32],             // Fixed-length, UTF-8 padded
    pub authority: Pubkey,          // Wallet that can register videos
    pub endorsers: [Pubkey; 3],     // Exactly 3 endorsers
    pub bump: u8,                   // PDA bump seed
}
```

**Size Calculation:**
```
OFFICIAL_SIZE = 8 (discriminator)
              + 8 (official_id)
              + 32 (name)
              + 32 (authority)
              + 32×3 (endorsers)
              + 1 (bump)
              = 177 bytes
```

**PDA Derivation:** `[b"official", official_id.to_le_bytes()]`

### Video Account

```rust
#[account]
pub struct Video {
    pub official: Pubkey,                    // Link to Official account
    pub video_hash: [u8; 32],                // SHA-256 hash
    pub ipfs_cid: [u8; 64],                  // IPFS CID (padded)
    pub timestamp: i64,                      // Unix timestamp
    pub votes: Vec<Vote>,                    // Max 3 votes
    pub status: VideoStatus,                 // Computed from votes
    pub bump: u8,                            // PDA bump
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct Vote {
    pub endorser: Pubkey,    // 32 bytes
    pub is_authentic: bool,  // 1 byte
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
#[repr(u8)]
pub enum VideoStatus {
    Unverified,
    Authentic,
    Disputed,
}
```

**Size Calculation:**
```
VIDEO_SIZE = 8 (discriminator)
           + 32 (official)
           + 32 (video_hash)
           + 64 (ipfs_cid)
           + 8 (timestamp)
           + 4 (votes vec prefix)
           + 3×(32+1) (max 3 votes)
           + 1 (status enum)
           + 1 (bump)
           = 249 bytes
```

**PDA Derivation:** `[b"video", official.key(), video_hash]`

## Program Instructions

### 1. register_official

**Purpose:** Admin/bootstrap instruction to create Official accounts

**Parameters:**
- `official_id: u64`
- `name: [u8; 32]`
- `authority: Pubkey`
- `endorsers: [Pubkey; 3]`

**Validation:**
- Endorsers array must have exactly 3 elements

**Accounts:**
- `official` (init, payer, space = OFFICIAL_SIZE)
- `admin` (signer, mut) - pays for account creation

### 2. register_video

**Purpose:** Official registers a new video with hash and IPFS CID

**Parameters:**
- `video_hash: [u8; 32]`
- `ipfs_cid: [u8; 64]`

**Validation:**
- Signer must match `official.authority` (via `has_one` constraint)
- Video PDA must not already exist

**Accounts:**
- `official` (has_one = authority)
- `video` (init, payer, space = VIDEO_SIZE)
- `authority` (signer, mut)

**Initialization:**
- `votes: Vec::new()` (empty, capacity for 3)
- `status: VideoStatus::Unverified`
- `timestamp: Clock::get()?.unix_timestamp`

### 3. endorse_video

**Purpose:** Approved endorser votes on video authenticity

**Parameters:**
- `is_authentic: bool`

**Validation:**
- Signer must be in `official.endorsers[0..3]`
- Signer must not have already voted (check votes vec)

**Accounts:**
- `official` (must match video.official)
- `video` (mut)
- `endorser` (signer)

**Logic:**
1. Verify endorser is in official.endorsers list
2. Check endorser hasn't already voted
3. Append `Vote { endorser, is_authentic }` to votes vec
4. Recalculate status using 2-of-3 rule

**Status Update Logic:**
```rust
let authentic_count = votes.iter().filter(|v| v.is_authentic).count();
let fake_count = votes.len() - authentic_count;

video.status = if authentic_count >= 2 {
    VideoStatus::Authentic
} else if fake_count >= 2 {
    VideoStatus::Disputed
} else {
    VideoStatus::Unverified
};
```

## Error Codes

```rust
#[error_code]
pub enum TruChainError {
    #[msg("Only the official's authority can register videos")]
    UnauthorizedOfficial,

    #[msg("Only approved endorsers can vote on videos")]
    UnauthorizedEndorser,

    #[msg("This endorser has already voted on this video")]
    AlreadyVoted,

    #[msg("Video already registered for this official")]
    VideoAlreadyExists,

    #[msg("Invalid official name (must be UTF-8)")]
    InvalidOfficialName,

    #[msg("Invalid IPFS CID format")]
    InvalidIpfsCid,

    #[msg("Must provide exactly 3 endorsers")]
    InvalidEndorserCount,
}
```

## Program Structure

```
programs/truchain/src/
├── lib.rs              // Program entrypoint, declare_id!
├── state/
│   ├── mod.rs
│   ├── official.rs     // Official struct + OFFICIAL_SIZE
│   └── video.rs        // Video, Vote, VideoStatus + VIDEO_SIZE
├── instructions/
│   ├── mod.rs
│   ├── register_official.rs
│   ├── register_video.rs
│   └── endorse_video.rs
└── errors.rs           // TruChainError enum
```

## Testing Strategy

### Happy Paths
1. **Authentic Flow:** Register official → Register video → 2 endorsers vote authentic → Status = Authentic
2. **Disputed Flow:** Register video → 2 endorsers vote fake → Status = Disputed
3. **Unverified:** Register video → 1 endorser votes → Status remains Unverified

### Error Cases
1. Non-authority tries `register_video` → `UnauthorizedOfficial`
2. Non-endorser tries `endorse_video` → `UnauthorizedEndorser`
3. Endorser votes twice on same video → `AlreadyVoted`
4. Register same video twice → `VideoAlreadyExists`
5. Register official with != 3 endorsers → `InvalidEndorserCount`

## Implementation Constraints

1. Use `OFFICIAL_SIZE` and `VIDEO_SIZE` constants with 8-byte discriminator included
2. Use Anchor `seeds = [...]` + `bump` (don't include bump in seeds array)
3. Pre-allocate votes vec with capacity for 3 votes (4 bytes prefix + 3×33 bytes)
4. Mark `VideoStatus` with `#[repr(u8)]` for consistent serialization
5. Enforce exactly 3 endorsers per official
6. Enforce vote-once per endorser per video
7. Use 2-of-3 majority rule for status transitions

## Security Considerations

- PDA derivations prevent account spoofing
- `has_one` constraints verify authority/ownership
- Endorser list validation prevents unauthorized votes
- Double-vote prevention via votes vec check
- Immutable votes prevent vote manipulation
- Fixed account sizes prevent realloc attacks
