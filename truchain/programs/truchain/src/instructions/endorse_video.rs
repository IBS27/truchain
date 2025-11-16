use anchor_lang::prelude::*;

use crate::errors::TruChainError;
use crate::state::{Official, Video, Vote, MAX_VOTES};

#[derive(Accounts)]
pub struct EndorseVideo<'info> {
    pub official: Account<'info, Official>,

    #[account(
        mut,
        constraint = video.official == official.key() @ TruChainError::UnauthorizedOfficial
    )]
    pub video: Account<'info, Video>,

    #[account(mut)]
    pub endorser: Signer<'info>,
}

pub fn handler(
    ctx: Context<EndorseVideo>,
    is_authentic: bool,
) -> Result<()> {
    let official = &ctx.accounts.official;
    let video = &mut ctx.accounts.video;
    let endorser = &ctx.accounts.endorser;

    let endorser_key = endorser.key();

    // ensure signer is an approved endorser
    if !official.endorsers.contains(&endorser_key) {
        return err!(TruChainError::UnauthorizedEndorser);
    }

    // ensure they haven't already voted
    if video
        .votes
        .iter()
        .any(|v| v.endorser == endorser_key)
    {
        return err!(TruChainError::AlreadyVoted);
    }

    // ensure we don't exceed pre-allocated space
    if video.votes.len() >= MAX_VOTES {
        return err!(TruChainError::TooManyVotes);
    }

    // record the vote
    video.votes.push(Vote {
        endorser: endorser_key,
        is_authentic,
    });

    // recompute status based on votes (2-of-3)
    video.recompute_status();

    Ok(())
}
