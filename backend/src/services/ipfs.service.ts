import fs from 'fs';
import crypto from 'crypto';
import path from 'path';
import { config } from '../config';

// Storage directory for mock IPFS (for hackathon demo)
const MOCK_IPFS_STORAGE = path.join(__dirname, '../../uploads/ipfs-mock');

/**
 * Initialize mock IPFS storage directory
 */
function initMockStorage() {
  if (!fs.existsSync(MOCK_IPFS_STORAGE)) {
    fs.mkdirSync(MOCK_IPFS_STORAGE, { recursive: true });
  }
}

/**
 * Generate a mock CID based on file content
 * Uses SHA-256 hash to create a deterministic CID-like string
 */
function generateMockCID(fileBuffer: Buffer): string {
  const hash = crypto.createHash('sha256').update(fileBuffer).digest('hex');
  // Format like a IPFS CID: Qm + base58-like characters (using hex for simplicity)
  return `Qm${hash.substring(0, 44)}`;
}

/**
 * Upload file to IPFS (Mock implementation for hackathon)
 * Returns CID (Content Identifier)
 *
 * NOTE: This is a mock implementation for development/demo.
 * For production, replace with actual IPFS integration using ipfs-http-client.
 *
 * @throws Error if filePath is invalid, file cannot be read, or upload fails
 */
export async function uploadToIPFS(filePath: string): Promise<string> {
  // Input validation
  if (!filePath || typeof filePath !== 'string' || filePath.trim() === '') {
    throw new Error('Invalid file path: must be a non-empty string');
  }

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  try {
    initMockStorage();

    // Read file
    const fileBuffer = await fs.promises.readFile(filePath);

    // Generate deterministic CID
    const cid = generateMockCID(fileBuffer);

    // Store file in mock IPFS storage
    const storagePath = path.join(MOCK_IPFS_STORAGE, cid);
    await fs.promises.writeFile(storagePath, fileBuffer);

    console.log(`[MOCK IPFS] Uploaded file with CID: ${cid}`);
    return cid;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to upload file to IPFS: ${error.message}`);
    }
    throw new Error('Failed to upload file to IPFS: Unknown error');
  }
}

/**
 * Download file from IPFS (Mock implementation for hackathon)
 * Returns Buffer of file contents
 *
 * NOTE: This is a mock implementation for development/demo.
 * For production, replace with actual IPFS integration using ipfs-http-client.
 *
 * @throws Error if CID is invalid or download fails
 */
export async function downloadFromIPFS(cid: string): Promise<Buffer> {
  // Input validation
  if (!cid || typeof cid !== 'string' || cid.trim() === '') {
    throw new Error('Invalid CID: must be a non-empty string');
  }

  try {
    initMockStorage();

    // Retrieve file from mock storage
    const storagePath = path.join(MOCK_IPFS_STORAGE, cid);

    if (!fs.existsSync(storagePath)) {
      throw new Error(`File not found for CID: ${cid}`);
    }

    const fileBuffer = await fs.promises.readFile(storagePath);
    console.log(`[MOCK IPFS] Downloaded file with CID: ${cid}`);

    return fileBuffer;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to download from IPFS: ${error.message}`);
    }
    throw new Error('Failed to download from IPFS: Unknown error');
  }
}

/**
 * Delete file from IPFS (Mock implementation for hackathon)
 * Removes file from local mock storage
 *
 * NOTE: This is a mock implementation for development/demo.
 * In real IPFS, you would "unpin" the content, not delete it.
 * Real IPFS content may still exist on other nodes.
 *
 * @param cid - Content Identifier of file to delete
 * @throws Error if CID is invalid or deletion fails
 */
export async function deleteFromIPFS(cid: string): Promise<void> {
  // Input validation
  if (!cid || typeof cid !== 'string' || cid.trim() === '') {
    throw new Error('Invalid CID: must be a non-empty string');
  }

  try {
    initMockStorage();

    const storagePath = path.join(MOCK_IPFS_STORAGE, cid);

    // Check if file exists
    if (!fs.existsSync(storagePath)) {
      throw new Error(`File not found for CID: ${cid}`);
    }

    // Delete file
    await fs.promises.unlink(storagePath);
    console.log(`[MOCK IPFS] Deleted file with CID: ${cid}`);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to delete from IPFS: ${error.message}`);
    }
    throw new Error('Failed to delete from IPFS: Unknown error');
  }
}
