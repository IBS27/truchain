use anchor_lang::prelude::*;

// The on-chain identity for a single official/source.
#[account]
pub struct Official {
    pub official_id: u64,        // e.g. 1, 2, 3...
    pub name: [u8; 32],          // UTF-8 bytes, padded/truncated
    pub authority: Pubkey,       // wallet that can register videos
    pub endorsers: [Pubkey; 3],  // exactly 3 endorsers
    pub bump: u8,                // PDA bump
}

// Account size calculation (bytes)
// 8  discriminator
// 8  official_id
// 32 name
// 32 authority
// 32*3 endorsers
// 1  bump
pub const OFFICIAL_SIZE: usize = 8 + 8 + 32 + 32 + 32 * 3 + 1;
