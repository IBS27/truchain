use anchor_lang::prelude::*;

#[error_code]
pub enum TruChainError {
    #[msg("Only the official's authority can register videos")]
    UnauthorizedOfficial,

    #[msg("Only approved endorsers can vote on videos")]
    UnauthorizedEndorser,

    #[msg("This endorser has already voted on this video")]
    AlreadyVoted,

    #[msg("Maximum number of votes reached for this video")]
    TooManyVotes,

    #[msg("Video already registered for this official")]
    VideoAlreadyExists,

    #[msg("Invalid official name (must be <= 32 bytes UTF-8)")]
    InvalidOfficialName,

    #[msg("Invalid IPFS CID format (must be non-empty and <= 64 bytes)")]
    InvalidIpfsCid,

    #[msg("Must provide exactly 3 endorsers")]
    InvalidEndorserCount,

    #[msg("Duplicate endorsers not allowed - each endorser must be unique")]
    DuplicateEndorsers,

    #[msg("Invalid endorser pubkey - cannot be default or system program")]
    InvalidEndorser,
}
