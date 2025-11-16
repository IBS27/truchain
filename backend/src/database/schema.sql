CREATE TABLE IF NOT EXISTS social_videos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  file_path TEXT NOT NULL,
  file_url TEXT NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  verified_count INTEGER DEFAULT 0,
  misleading_count INTEGER DEFAULT 0,
  unverified_count INTEGER DEFAULT 0,
  fake_count INTEGER DEFAULT 0,
  dominant_tag TEXT DEFAULT 'unverified'
);

CREATE TABLE IF NOT EXISTS social_flags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id INTEGER NOT NULL,
  flag_type TEXT NOT NULL CHECK(flag_type IN ('verified', 'misleading', 'unverified', 'fake')),
  flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (video_id) REFERENCES social_videos(id)
);

CREATE INDEX IF NOT EXISTS idx_social_videos_uploaded_at ON social_videos(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_flags_video_id ON social_flags(video_id);
