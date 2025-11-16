use anchor_lang::prelude::*;

use crate::errors::TruChainError;
use crate::state::{Official, Video, VideoStatus, VIDEO_SIZE};

#[derive(Accounts)]
#[instruction(video_hash: [u8; 32])]
pub struct RegisterVideo<'info> {
    #[account(
        mut,
        has_one = authority @ TruChainError::UnauthorizedOfficial
    )]
    pub official: Account<'info, Official>,

    #[account(
        init,
        payer = authority,
        space = VIDEO_SIZE,
        seeds = [b"video", official.key().as_ref(), &video_hash],
        bump
    )]
    pub video: Account<'info, Video>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

pub fn handler(
    ctx: Context<RegisterVideo>,
    video_hash: [u8; 32],
    ipfs_cid: String,
) -> Result<()> {
    // basic CID validation
    let cid_bytes = ipfs_cid.as_bytes();
    if cid_bytes.is_empty() || cid_bytes.len() > 64 {
        return err!(TruChainError::InvalidIpfsCid);
    }

    let mut cid_padded = [0u8; 64];
    cid_padded[..cid_bytes.len()].copy_from_slice(cid_bytes);

    let official = &ctx.accounts.official;
    let video = &mut ctx.accounts.video;

    video.official = official.key();
    video.video_hash = video_hash;
    video.ipfs_cid = cid_padded;

    // timestamp
    let clock = Clock::get()?;
    video.timestamp = clock.unix_timestamp;

    // initial state
    video.votes = Vec::new();
    video.status = VideoStatus::Unverified;

    video.bump = ctx.bumps.video;

    Ok(())
}
