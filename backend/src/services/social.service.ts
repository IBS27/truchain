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

  static addFlag(videoId: number, userId: string, flagType: 'verified' | 'misleading' | 'unverified' | 'fake'): void {
    // Map flag types to column names (prevents SQL injection)
    const columnMap: Record<typeof flagType, string> = {
      'verified': 'verified_count',
      'misleading': 'misleading_count',
      'unverified': 'unverified_count',
      'fake': 'fake_count'
    };

    // Use transaction to ensure atomicity
    const transaction = db.transaction(() => {
      // Check if user already has a vote for this video
      const existingVote = db.prepare(`
        SELECT flag_type FROM social_flags
        WHERE video_id = ? AND user_id = ?
      `).get(videoId, userId) as { flag_type: string } | undefined;

      if (existingVote && existingVote.flag_type !== flagType) {
        // User is changing their vote - decrement old count
        const oldColumnName = columnMap[existingVote.flag_type as typeof flagType];
        db.prepare(`
          UPDATE social_videos
          SET ${oldColumnName} = MAX(0, ${oldColumnName} - 1)
          WHERE id = ?
        `).run(videoId);

        // Update the flag type
        db.prepare(`
          UPDATE social_flags
          SET flag_type = ?, flagged_at = CURRENT_TIMESTAMP
          WHERE video_id = ? AND user_id = ?
        `).run(flagType, videoId, userId);

        // Increment new count
        const newColumnName = columnMap[flagType];
        db.prepare(`
          UPDATE social_videos
          SET ${newColumnName} = ${newColumnName} + 1
          WHERE id = ?
        `).run(videoId);
      } else if (!existingVote) {
        // New vote - insert flag
        db.prepare(`
          INSERT INTO social_flags (video_id, user_id, flag_type)
          VALUES (?, ?, ?)
        `).run(videoId, userId, flagType);

        // Increment count
        const columnName = columnMap[flagType];
        db.prepare(`
          UPDATE social_videos
          SET ${columnName} = ${columnName} + 1
          WHERE id = ?
        `).run(videoId);
      }
      // If existingVote.flag_type === flagType, do nothing (user clicked same button)
    });

    // Execute transaction
    transaction();

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
