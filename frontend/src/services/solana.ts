import { Program } from '@coral-xyz/anchor';
import { PublicKey } from '@solana/web3.js';
import type { Truchain } from '../anchor/idl';

const ADMIN_WALLET = import.meta.env.VITE_ADMIN_WALLET;

/**
 * Fetch all Official accounts from the program
 */
export async function getAllOfficials(program: Program<Truchain>) {
  return await program.account.Official.all();
}

/**
 * Fetch all Video accounts for a specific official
 */
export async function getVideosForOfficial(
  program: Program<Truchain>,
  officialPubkey: PublicKey
) {
  const videos = await program.account.Video.all();
  return videos.filter((v: any) => v.account.official.equals(officialPubkey));
}

/**
 * Check if wallet is the admin
 */
export function checkIsAdmin(walletPubkey: PublicKey | null): boolean {
  if (!walletPubkey || !ADMIN_WALLET) return false;
  return walletPubkey.toString() === ADMIN_WALLET;
}

/**
 * Check if wallet is an official's authority
 * Returns the Official account if true, null otherwise
 */
export async function checkIsOfficialAuthority(
  program: Program<Truchain>,
  walletPubkey: PublicKey | null
) {
  if (!walletPubkey) return null;

  const officials = await getAllOfficials(program);
  return officials.find((o: any) => o.account.authority.equals(walletPubkey)) || null;
}

/**
 * Check if wallet is an endorser for any official
 * Returns array of Official accounts where wallet is an endorser
 */
export async function checkIsEndorser(
  program: Program<Truchain>,
  walletPubkey: PublicKey | null
) {
  if (!walletPubkey) return [];

  const officials = await getAllOfficials(program);
  return officials.filter((o: any) =>
    o.account.endorsers.some((e: PublicKey) => e.equals(walletPubkey))
  );
}

/**
 * Register a new official (admin only)
 */
export async function registerOfficial(
  program: Program<Truchain>,
  officialId: number,
  name: string,
  authority: PublicKey,
  endorsers: [PublicKey, PublicKey, PublicKey]
) {
  // Convert officialId to u64 bytes (8 bytes, little-endian)
  const officialIdBuffer = new Uint8Array(8);
  const view = new DataView(officialIdBuffer.buffer);
  view.setBigUint64(0, BigInt(officialId), true); // true = little-endian

  const [officialPda] = PublicKey.findProgramAddressSync(
    [new TextEncoder().encode('official'), officialIdBuffer],
    program.programId
  );

  return await program.methods
    .registerOfficial(officialId, name, authority, endorsers)
    .accountsPartial({
      official: officialPda,
      admin: program.provider.publicKey!,
    })
    .rpc();
}

/**
 * Register a video (official's authority only)
 */
export async function registerVideo(
  program: Program<Truchain>,
  officialPubkey: PublicKey,
  videoHash: number[],
  ipfsCid: string
) {
  const [videoPda] = PublicKey.findProgramAddressSync(
    [new TextEncoder().encode('video'), officialPubkey.toBuffer(), Uint8Array.from(videoHash)],
    program.programId
  );

  return await program.methods
    .registerVideo(videoHash, ipfsCid)
    .accountsPartial({
      official: officialPubkey,
      video: videoPda,
      authority: program.provider.publicKey!,
    })
    .rpc();
}

/**
 * Endorse a video (endorser only)
 */
export async function endorseVideo(
  program: Program<Truchain>,
  officialPubkey: PublicKey,
  videoHash: number[],
  isAuthentic: boolean
) {
  const [videoPda] = PublicKey.findProgramAddressSync(
    [new TextEncoder().encode('video'), officialPubkey.toBuffer(), Uint8Array.from(videoHash)],
    program.programId
  );

  return await program.methods
    .endorseVideo(isAuthentic)
    .accountsPartial({
      official: officialPubkey,
      video: videoPda,
      endorser: program.provider.publicKey!,
    })
    .rpc();
}
