import { db } from '../database/db';

export interface SocialVideo {
  id: number;
  title: string;
  description: string | null;
  file_path: string;
  file_url: string;
  uploaded_at: string;
  verified_count: number;
  misleading_count: number;
  unverified_count: number;
  fake_count: number;
  dominant_tag: string;
}

export interface FlagCounts {
  verified: number;
  misleading: number;
  unverified: number;
  fake: number;
}

export class SocialService {

  static createVideo(title: string, description: string | null, filePath: string, fileUrl: string): SocialVideo {
    const stmt = db.prepare(`
      INSERT INTO social_videos (title, description, file_path, file_url)
      VALUES (?, ?, ?, ?)
    `);
    const result = stmt.run(title, description, filePath, fileUrl);

    return this.getVideoById(result.lastInsertRowid as number)!;
  }

  static getAllVideos(): SocialVideo[] {
    const stmt = db.prepare(`
      SELECT * FROM social_videos
      ORDER BY uploaded_at DESC
    `);
    return stmt.all() as SocialVideo[];
  }

  static getVideoById(id: number): SocialVideo | undefined {
    const stmt = db.prepare('SELECT * FROM social_videos WHERE id = ?');
    return stmt.get(id) as SocialVideo | undefined;
  }

  static addFlag(videoId: number, flagType: 'verified' | 'misleading' | 'unverified' | 'fake'): void {
    // Insert flag
    const insertStmt = db.prepare(`
      INSERT INTO social_flags (video_id, flag_type)
      VALUES (?, ?)
    `);
    insertStmt.run(videoId, flagType);

    // Map flag types to column names (prevents SQL injection)
    const columnMap: Record<typeof flagType, string> = {
      'verified': 'verified_count',
      'misleading': 'misleading_count',
      'unverified': 'unverified_count',
      'fake': 'fake_count'
    };

    const columnName = columnMap[flagType];

    // Update video counts
    const updateStmt = db.prepare(`
      UPDATE social_videos
      SET ${columnName} = ${columnName} + 1
      WHERE id = ?
    `);
    updateStmt.run(videoId);

    // Recalculate dominant tag
    this.updateDominantTag(videoId);
  }

  static updateDominantTag(videoId: number): void {
    const video = this.getVideoById(videoId);
    if (!video) return;

    const counts = {
      verified: video.verified_count,
      misleading: video.misleading_count,
      unverified: video.unverified_count,
      fake: video.fake_count
    };

    // Find the tag with the most votes
    const dominantTag = Object.entries(counts).reduce((a, b) =>
      counts[a[0] as keyof FlagCounts] > counts[b[0] as keyof FlagCounts] ? a : b
    )[0];

    const stmt = db.prepare('UPDATE social_videos SET dominant_tag = ? WHERE id = ?');
    stmt.run(dominantTag, videoId);
  }

  static getFlagCounts(videoId: number): FlagCounts {
    const video = this.getVideoById(videoId);
    if (!video) {
      return { verified: 0, misleading: 0, unverified: 0, fake: 0 };
    }

    return {
      verified: video.verified_count,
      misleading: video.misleading_count,
      unverified: video.unverified_count,
      fake: video.fake_count
    };
  }
}
