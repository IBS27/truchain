use anchor_lang::prelude::*;

use crate::errors::TruChainError;
use crate::state::{Official, OFFICIAL_SIZE};

#[derive(Accounts)]
#[instruction(official_id: u64)]
pub struct RegisterOfficial<'info> {
    #[account(
        init,
        payer = admin,
        space = OFFICIAL_SIZE,
        seeds = [b"official", &official_id.to_le_bytes()],
        bump
    )]
    pub official: Account<'info, Official>,

    #[account(mut)]
    pub admin: Signer<'info>, // bootstrap authority for creating officials

    pub system_program: Program<'info, System>,
}

pub fn handler(
    ctx: Context<RegisterOfficial>,
    official_id: u64,
    name: String,
    authority: Pubkey,
    endorsers: [Pubkey; 3],
) -> Result<()> {
    // validate endorsers count (array always len=3, but we keep the error for clarity)
    // if you ever change to Vec, this becomes important
    if endorsers.len() != 3 {
        return err!(TruChainError::InvalidEndorserCount);
    }

    // validate name length (UTF-8 already guaranteed by String)
    let name_bytes = name.as_bytes();
    if name_bytes.is_empty() || name_bytes.len() > 32 {
        return err!(TruChainError::InvalidOfficialName);
    }

    // pack name into fixed [u8; 32]
    let mut name_padded = [0u8; 32];
    name_padded[..name_bytes.len()].copy_from_slice(name_bytes);

    let official = &mut ctx.accounts.official;

    official.official_id = official_id;
    official.name = name_padded;
    official.authority = authority;
    official.endorsers = endorsers;

    // store bump
    official.bump = ctx.bumps.official;

    Ok(())
}
