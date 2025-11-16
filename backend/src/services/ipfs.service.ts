import { create, IPFSHTTPClient } from 'ipfs-http-client';
import fs from 'fs';
import { config } from '../config';

let ipfsClient: IPFSHTTPClient | null = null;

/**
 * Initialize IPFS client (lazy initialization)
 */
function getIPFSClient(): IPFSHTTPClient {
  if (!ipfsClient) {
    ipfsClient = create({
      host: config.ipfs.host,
      port: config.ipfs.port,
      protocol: config.ipfs.protocol,
    });
  }
  return ipfsClient;
}

/**
 * Upload file to IPFS
 * Returns CID (Content Identifier)
 *
 * @throws Error if filePath is invalid, file cannot be read, or IPFS upload fails
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

  // Try to read file asynchronously and upload to IPFS
  try {
    const fileBuffer = await fs.promises.readFile(filePath);
    const client = getIPFSClient();
    const result = await client.add(fileBuffer);
    return result.cid.toString();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to upload file to IPFS: ${error.message}`);
    }
    throw new Error('Failed to upload file to IPFS: Unknown error');
  }
}

/**
 * Download file from IPFS
 * Returns Buffer of file contents
 *
 * @throws Error if CID is invalid or IPFS download fails
 */
export async function downloadFromIPFS(cid: string): Promise<Buffer> {
  // Input validation
  if (!cid || typeof cid !== 'string' || cid.trim() === '') {
    throw new Error('Invalid CID: must be a non-empty string');
  }

  // Try to download from IPFS
  try {
    const client = getIPFSClient();
    const chunks: Uint8Array[] = [];

    for await (const chunk of client.cat(cid)) {
      chunks.push(chunk);
    }

    return Buffer.concat(chunks);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to download from IPFS: ${error.message}`);
    }
    throw new Error('Failed to download from IPFS: Unknown error');
  }
}
