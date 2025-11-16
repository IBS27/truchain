import crypto from 'crypto';
import fs from 'fs';

/**
 * Computes SHA-256 hash of a file
 * Returns 32-byte array matching Solana program's [u8; 32] type
 */
export function hashFile(filePath: string): number[] {
  const fileBuffer = fs.readFileSync(filePath);
  const hashBuffer = crypto.createHash('sha256').update(fileBuffer).digest();

  // Convert Buffer to number array for Solana compatibility
  return Array.from(hashBuffer);
}

/**
 * Validates that hash is exactly 32 bytes
 */
export function validateHash(hash: number[]): boolean {
  return Array.isArray(hash) && hash.length === 32 && hash.every(b => b >= 0 && b <= 255);
}
