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
 */
export async function uploadToIPFS(filePath: string): Promise<string> {
  const client = getIPFSClient();
  const fileBuffer = fs.readFileSync(filePath);

  const result = await client.add(fileBuffer);
  return result.cid.toString();
}

/**
 * Download file from IPFS
 * Returns Buffer of file contents
 */
export async function downloadFromIPFS(cid: string): Promise<Buffer> {
  const client = getIPFSClient();
  const chunks: Uint8Array[] = [];

  for await (const chunk of client.cat(cid)) {
    chunks.push(chunk);
  }

  return Buffer.concat(chunks);
}
