import crypto from 'crypto';
import fs from 'fs';

/**
 * Computes SHA-256 hash of a file
 * Returns 32-byte array matching Solana program's [u8; 32] type
 *
 * @throws Error if filePath is invalid or file cannot be read
 */
export function hashFile(filePath: string): number[] {
  // Input validation
  if (!filePath || typeof filePath !== 'string' || filePath.trim() === '') {
    throw new Error('Invalid file path: must be a non-empty string');
  }

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  // Try to read and hash the file
  try {
    const fileBuffer = fs.readFileSync(filePath);
    const hashBuffer = crypto.createHash('sha256').update(fileBuffer).digest();

    // Convert Buffer to number array for Solana compatibility
    return Array.from(hashBuffer);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to read or hash file: ${error.message}`);
    }
    throw new Error('Failed to read or hash file: Unknown error');
  }
}

/**
 * Validates that hash is exactly 32 bytes
 */
export function validateHash(hash: number[]): boolean {
  return Array.isArray(hash) && hash.length === 32 && hash.every(b => b >= 0 && b <= 255);
}
