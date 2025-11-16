#!/usr/bin/env ts-node

/**
 * Backfill Script - Download all IPFS videos to AI service directory
 *
 * This script:
 * 1. Fetches all video CIDs from the mock IPFS storage
 * 2. Downloads each video to the AI service directory
 * 3. Registers each video with the AI service for transcription
 *
 * Usage:
 *   ts-node scripts/backfill-ai-videos.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import { AIVerificationService } from '../src/services/ai-verification.service';

const IPFS_MOCK_DIR = path.join(__dirname, '../uploads/ipfs-mock');
const AI_DOWNLOAD_DIR = path.join(__dirname, '../../ai-layer/download');

interface VideoMetadata {
  filename: string;
  cid: string;
  uploadedAt: string;
  size: number;
}

/**
 * Get all videos from mock IPFS storage
 */
function getAllIPFSVideos(): VideoMetadata[] {
  if (!fs.existsSync(IPFS_MOCK_DIR)) {
    console.log('⚠️  IPFS mock directory not found. No videos to backfill.');
    return [];
  }

  const files = fs.readdirSync(IPFS_MOCK_DIR);
  const videos: VideoMetadata[] = [];

  for (const file of files) {
    const filePath = path.join(IPFS_MOCK_DIR, file);

    // Skip directories
    if (!fs.statSync(filePath).isFile()) {
      continue;
    }

    // Check if it has a video extension OR is a file without extension (CID-only)
    const hasVideoExt = file.endsWith('.mp4') || file.endsWith('.mov') || file.endsWith('.avi');
    const hasNoExt = !file.includes('.');

    if (hasVideoExt || hasNoExt) {
      const stats = fs.statSync(filePath);

      videos.push({
        filename: file,
        cid: file.replace(/\.[^/.]+$/, ''), // Remove extension to get CID (or keep as-is if no extension)
        uploadedAt: stats.mtime.toISOString(),
        size: stats.size,
      });
    }
  }

  return videos;
}

/**
 * Ensure AI download directory exists
 */
function ensureAIDirectoryExists(): void {
  if (!fs.existsSync(AI_DOWNLOAD_DIR)) {
    console.log(`📁 Creating AI download directory: ${AI_DOWNLOAD_DIR}`);
    fs.mkdirSync(AI_DOWNLOAD_DIR, { recursive: true });
  }
}

/**
 * Copy video to AI directory if not already present
 */
function copyVideoToAI(sourceFile: string, cid: string): string {
  let ext = path.extname(sourceFile);

  // If no extension, assume it's MP4 (IPFS files are stored without extensions)
  if (!ext) {
    ext = '.mp4';
  }

  const destFile = path.join(AI_DOWNLOAD_DIR, `${cid}${ext}`);

  if (fs.existsSync(destFile)) {
    console.log(`   ⏭️  Already exists: ${path.basename(destFile)}`);
    return destFile;
  }

  fs.copyFileSync(sourceFile, destFile);
  console.log(`   ✅ Copied: ${path.basename(destFile)}`);
  return destFile;
}

/**
 * Main backfill function
 */
async function backfillVideos(): Promise<void> {
  console.log('═══════════════════════════════════════════════════════');
  console.log('🔄 AI Video Backfill Script');
  console.log('═══════════════════════════════════════════════════════\n');

  // Step 1: Check AI service health
  console.log('1️⃣  Checking AI service health...');
  try {
    const health = await AIVerificationService.checkHealth();
    console.log(`   ✅ AI service is healthy`);
    console.log(`   📊 Videos in AI database: ${health.videos_available}`);
  } catch (error) {
    console.error('   ❌ AI service is not available!');
    console.error(`   Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    console.log('\n💡 Make sure the AI service is running:');
    console.log('   cd ai-layer && ./start_ai_service.sh\n');
    process.exit(1);
  }

  // Step 2: Ensure AI directory exists
  console.log('\n2️⃣  Ensuring AI directory exists...');
  ensureAIDirectoryExists();
  console.log(`   ✅ AI directory ready: ${AI_DOWNLOAD_DIR}`);

  // Step 3: Get all IPFS videos
  console.log('\n3️⃣  Scanning IPFS storage...');
  const videos = getAllIPFSVideos();
  console.log(`   📹 Found ${videos.length} video(s) in IPFS`);

  if (videos.length === 0) {
    console.log('\n✨ No videos to backfill. You\'re all set!');
    return;
  }

  // Step 4: Copy and register each video
  console.log('\n4️⃣  Copying videos to AI directory and registering...\n');

  let successCount = 0;
  let skipCount = 0;
  let errorCount = 0;

  for (let i = 0; i < videos.length; i++) {
    const video = videos[i];
    console.log(`\n📹 [${i + 1}/${videos.length}] Processing: ${video.filename}`);
    console.log(`   CID: ${video.cid}`);
    console.log(`   Size: ${(video.size / 1024 / 1024).toFixed(2)} MB`);

    try {
      // Copy to AI directory
      const sourcePath = path.join(IPFS_MOCK_DIR, video.filename);
      const destPath = copyVideoToAI(sourcePath, video.cid);

      // Check if already in AI database
      const aiVideos = await AIVerificationService.listVideos();
      const alreadyRegistered = aiVideos.some(v => v.video_name === path.basename(destPath));

      if (alreadyRegistered) {
        console.log(`   ⏭️  Already registered with AI service`);
        skipCount++;
      } else {
        // Register with AI service
        console.log(`   🔄 Registering with AI service...`);
        await AIVerificationService.registerOfficialVideo(
          destPath,
          `Official Video - ${video.cid}`
        );
        console.log(`   ✅ Registered and transcribed`);
        successCount++;
      }
    } catch (error) {
      console.error(`   ❌ Failed to process video`);
      console.error(`   Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      errorCount++;
    }
  }

  // Step 5: Summary
  console.log('\n═══════════════════════════════════════════════════════');
  console.log('📊 Backfill Summary');
  console.log('═══════════════════════════════════════════════════════');
  console.log(`✅ Successfully processed: ${successCount}`);
  console.log(`⏭️  Already existed: ${skipCount}`);
  console.log(`❌ Errors: ${errorCount}`);
  console.log(`📹 Total videos: ${videos.length}`);

  // Final health check
  console.log('\n5️⃣  Final AI service status...');
  try {
    const health = await AIVerificationService.checkHealth();
    console.log(`   ✅ Videos now in AI database: ${health.videos_available}`);
  } catch (error) {
    console.error(`   ⚠️  Could not get final status: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }

  console.log('\n✨ Backfill complete!\n');
}

// Run the backfill
backfillVideos()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error('\n💥 Backfill failed with error:');
    console.error(error);
    process.exit(1);
  });
