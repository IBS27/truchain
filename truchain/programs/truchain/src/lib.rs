use anchor_lang::prelude::*;

pub mod state;
pub mod instructions;
pub mod errors;

use instructions::*;

declare_id!("FGkp4CpRBNDQz2h5idbhbX7cHkbggpsUsF7enLiQE2nT");

#[program]
pub mod truchain {
    use super::*;

    pub fn register_official(
        ctx: Context<RegisterOfficial>,
        official_id: u64,
        name: String,
        authority: Pubkey,
        endorsers: [Pubkey; 3],
    ) -> Result<()> {
        register_official::handler(ctx, official_id, name, authority, endorsers)
    }

    pub fn register_video(
        ctx: Context<RegisterVideo>,
        video_hash: [u8; 32],
        ipfs_cid: String,
    ) -> Result<()> {
        register_video::handler(ctx, video_hash, ipfs_cid)
    }

    pub fn endorse_video(
        ctx: Context<EndorseVideo>,
        is_authentic: bool,
    ) -> Result<()> {
        endorse_video::handler(ctx, is_authentic)
    }
}
