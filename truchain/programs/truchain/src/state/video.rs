use anchor_lang::prelude::*;

// Max votes = 3 endorsers
pub const MAX_VOTES: usize = 3;

#[account]
pub struct Video {
    pub official: Pubkey,           // link to Official account
    pub video_hash: [u8; 32],       // SHA-256 of full video file
    pub ipfs_cid: [u8; 64],         // IPFS CID bytes, padded
    pub timestamp: i64,             // unix timestamp
    pub votes: Vec<Vote>,           // up to 3 votes
    pub status: VideoStatus,        // Unverified / Authentic / Disputed
    pub bump: u8,                   // PDA bump
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct Vote {
    pub endorser: Pubkey,
    pub is_authentic: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
#[repr(u8)]
pub enum VideoStatus {
    Unverified = 0,
    Authentic = 1,
    Disputed = 2,
}

// Account size calculation:
// 8  discriminator
// 32 official
// 32 video_hash
// 64 ipfs_cid
// 8  timestamp
// 4  votes vec length prefix (u32)
// 3 * (32 + 1) votes (Pubkey + bool)
// 1  status enum tag
// 1  bump
pub const VIDEO_SIZE: usize =
    8       // disc
    + 32    // official
    + 32    // video_hash
    + 64    // ipfs_cid
    + 8     // timestamp
    + 4     // votes vec length prefix
    + MAX_VOTES * (32 + 1) // 3 votes max
    + 1     // status
    + 1;    // bump

impl Video {
    // Recompute status based on current votes using 2-of-3 rule
    pub fn recompute_status(&mut self) {
        let authentic = self.votes.iter().filter(|v| v.is_authentic).count();
        let fake = self.votes.len().saturating_sub(authentic);

        self.status = if authentic >= 2 {
            VideoStatus::Authentic
        } else if fake >= 2 {
            VideoStatus::Disputed
        } else {
            VideoStatus::Unverified
        };
    }
}
