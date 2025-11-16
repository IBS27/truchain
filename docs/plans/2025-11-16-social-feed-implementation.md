# Social Media Feed Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a TikTok/Instagram-style short-form video feed for regular users to browse, upload, and flag video clips.

**Architecture:** Backend stores videos on local filesystem with SQLite for metadata and flags. Frontend uses React components with native HTML5 video players. Community flagging determines dominant verification status (Verified/Misleading/Unverified/Fake).

**Tech Stack:** Express.js, SQLite, Multer (file uploads), React, Tailwind CSS, shadcn/ui

---

## Task 1: Backend Database Setup

**Files:**
- Create: `backend/src/database/db.ts`
- Create: `backend/src/database/schema.sql`
- Modify: `backend/package.json`

**Step 1: Install SQLite dependency**

```bash
cd backend
npm install better-sqlite3
npm install --save-dev @types/better-sqlite3
```

**Step 2: Create database schema file**

Create `backend/src/database/schema.sql`:

```sql
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
```

**Step 3: Create database initialization module**

Create `backend/src/database/db.ts`:

```typescript
import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

const dbPath = path.join(__dirname, '../../data/social.db');
const schemaPath = path.join(__dirname, 'schema.sql');

// Ensure data directory exists
const dataDir = path.dirname(dbPath);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

export const db = new Database(dbPath);

// Initialize schema
const schema = fs.readFileSync(schemaPath, 'utf-8');
db.exec(schema);

console.log('Database initialized at:', dbPath);
```

**Step 4: Verify database initialization**

Run: `cd backend && npx ts-node src/database/db.ts`
Expected: "Database initialized at: <path>/data/social.db" with no errors

**Step 5: Commit**

```bash
git add backend/src/database/db.ts backend/src/database/schema.sql backend/package.json backend/package-lock.json
git commit -m "feat: add SQLite database for social videos"
```

---

## Task 2: Backend File Storage Setup

**Files:**
- Create: `backend/uploads/social/.gitkeep`
- Modify: `backend/.gitignore`
- Modify: `backend/src/index.ts`

**Step 1: Create uploads directory with .gitkeep**

```bash
cd backend
mkdir -p uploads/social
touch uploads/social/.gitkeep
```

**Step 2: Update .gitignore to ignore uploaded videos**

Add to `backend/.gitignore`:

```
# Uploaded videos (keep directory structure)
uploads/social/*
!uploads/social/.gitkeep
```

**Step 3: Add static file serving to Express**

Modify `backend/src/index.ts` to serve uploads:

```typescript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import ipfsRoutes from './routes/ipfs';
import { config } from './config';

dotenv.config();

const app = express();
const PORT = config.port;

app.use(cors());
app.use(express.json());

// Serve uploaded files
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/ipfs', ipfsRoutes);

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
```

**Step 4: Test static file serving**

Run backend: `cd backend && npm run dev`
Create test file: `echo "test" > backend/uploads/social/test.txt`
Test: `curl http://localhost:3001/uploads/social/test.txt`
Expected: "test"
Clean up: `rm backend/uploads/social/test.txt`

**Step 5: Commit**

```bash
git add backend/uploads/social/.gitkeep backend/.gitignore backend/src/index.ts
git commit -m "feat: add file storage for social videos"
```

---

## Task 3: Backend Social Video Service

**Files:**
- Create: `backend/src/services/social.service.ts`

**Step 1: Install multer for file uploads**

```bash
cd backend
npm install multer
npm install --save-dev @types/multer
```

**Step 2: Create social video service**

Create `backend/src/services/social.service.ts`:

```typescript
import { db } from '../database/db';
import path from 'path';
import fs from 'fs';

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

    // Update video counts
    const updateStmt = db.prepare(`
      UPDATE social_videos
      SET ${flagType}_count = ${flagType}_count + 1
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
```

**Step 3: Verify service compiles**

Run: `cd backend && npx tsc --noEmit`
Expected: No compilation errors

**Step 4: Commit**

```bash
git add backend/src/services/social.service.ts backend/package.json backend/package-lock.json
git commit -m "feat: add social video service with flag management"
```

---

## Task 4: Backend Social API Routes

**Files:**
- Create: `backend/src/routes/social.ts`
- Modify: `backend/src/index.ts`

**Step 1: Create social routes**

Create `backend/src/routes/social.ts`:

```typescript
import express, { Request, Response } from 'express';
import multer from 'multer';
import path from 'path';
import { SocialService } from '../services/social.service';

const router = express.Router();

// Configure multer for video uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, '../../uploads/social'));
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${Math.random().toString(36).substring(7)}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /mp4|mov|avi|webm/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
      cb(null, true);
    } else {
      cb(new Error('Only video files are allowed'));
    }
  }
});

// POST /api/social/videos/upload
router.post('/videos/upload', upload.single('video'), (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No video file provided' });
    }

    const { title, description } = req.body;
    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    const fileUrl = `/uploads/social/${req.file.filename}`;
    const video = SocialService.createVideo(title, description || null, req.file.path, fileUrl);

    res.json(video);
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Failed to upload video' });
  }
});

// GET /api/social/videos
router.get('/videos', (req: Request, res: Response) => {
  try {
    const videos = SocialService.getAllVideos();
    res.json(videos);
  } catch (error) {
    console.error('Fetch videos error:', error);
    res.status(500).json({ error: 'Failed to fetch videos' });
  }
});

// POST /api/social/videos/:id/flag
router.post('/videos/:id/flag', (req: Request, res: Response) => {
  try {
    const videoId = parseInt(req.params.id);
    const { flagType } = req.body;

    if (!['verified', 'misleading', 'unverified', 'fake'].includes(flagType)) {
      return res.status(400).json({ error: 'Invalid flag type' });
    }

    const video = SocialService.getVideoById(videoId);
    if (!video) {
      return res.status(404).json({ error: 'Video not found' });
    }

    SocialService.addFlag(videoId, flagType);
    const flagCounts = SocialService.getFlagCounts(videoId);
    const updatedVideo = SocialService.getVideoById(videoId);

    res.json({ video: updatedVideo, flagCounts });
  } catch (error) {
    console.error('Flag error:', error);
    res.status(500).json({ error: 'Failed to add flag' });
  }
});

// GET /api/social/videos/:id/flags
router.get('/videos/:id/flags', (req: Request, res: Response) => {
  try {
    const videoId = parseInt(req.params.id);
    const video = SocialService.getVideoById(videoId);

    if (!video) {
      return res.status(404).json({ error: 'Video not found' });
    }

    const flagCounts = SocialService.getFlagCounts(videoId);
    res.json(flagCounts);
  } catch (error) {
    console.error('Get flags error:', error);
    res.status(500).json({ error: 'Failed to get flag counts' });
  }
});

export default router;
```

**Step 2: Register social routes in main app**

Modify `backend/src/index.ts`:

```typescript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import ipfsRoutes from './routes/ipfs';
import socialRoutes from './routes/social';
import { config } from './config';
import './database/db'; // Initialize database

dotenv.config();

const app = express();
const PORT = config.port;

app.use(cors());
app.use(express.json());

// Serve uploaded files
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/ipfs', ipfsRoutes);
app.use('/api/social', socialRoutes);

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
```

**Step 3: Test backend endpoints**

Start backend: `cd backend && npm run dev`

Test upload (requires video file):
```bash
curl -X POST http://localhost:3001/api/social/videos/upload \
  -F "video=@/path/to/test-video.mp4" \
  -F "title=Test Video" \
  -F "description=Test description"
```
Expected: JSON response with video object

Test get videos:
```bash
curl http://localhost:3001/api/social/videos
```
Expected: JSON array with uploaded video

**Step 4: Commit**

```bash
git add backend/src/routes/social.ts backend/src/index.ts backend/package.json backend/package-lock.json
git commit -m "feat: add social video API endpoints"
```

---

## Task 5: Frontend API Service

**Files:**
- Modify: `frontend/src/services/api.ts`

**Step 1: Add social video types**

Add to `frontend/src/services/api.ts`:

```typescript
// ... existing imports and types ...

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
  dominant_tag: 'verified' | 'misleading' | 'unverified' | 'fake';
}

export interface FlagCounts {
  verified: number;
  misleading: number;
  unverified: number;
  fake: number;
}

// ... existing code ...
```

**Step 2: Add social video API functions**

Add to end of `frontend/src/services/api.ts`:

```typescript
// Social Video API

const BACKEND_URL = 'http://localhost:3001';

export const socialApi = {
  async getAllVideos(): Promise<SocialVideo[]> {
    const response = await fetch(`${BACKEND_URL}/api/social/videos`);
    if (!response.ok) throw new Error('Failed to fetch videos');
    return response.json();
  },

  async uploadVideo(file: File, title: string, description?: string): Promise<SocialVideo> {
    const formData = new FormData();
    formData.append('video', file);
    formData.append('title', title);
    if (description) formData.append('description', description);

    const response = await fetch(`${BACKEND_URL}/api/social/videos/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Failed to upload video');
    return response.json();
  },

  async flagVideo(videoId: number, flagType: 'verified' | 'misleading' | 'unverified' | 'fake'): Promise<{ video: SocialVideo; flagCounts: FlagCounts }> {
    const response = await fetch(`${BACKEND_URL}/api/social/videos/${videoId}/flag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ flagType }),
    });

    if (!response.ok) throw new Error('Failed to flag video');
    return response.json();
  },

  async getFlagCounts(videoId: number): Promise<FlagCounts> {
    const response = await fetch(`${BACKEND_URL}/api/social/videos/${videoId}/flags`);
    if (!response.ok) throw new Error('Failed to get flag counts');
    return response.json();
  },
};
```

**Step 3: Verify TypeScript compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No compilation errors

**Step 4: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add social video API client functions"
```

---

## Task 6: Frontend Badge Component (Warning Variant)

**Files:**
- Modify: `frontend/src/components/ui/badge.tsx`

**Step 1: Add warning variant to badge**

Modify `frontend/src/components/ui/badge.tsx` to add the warning variant:

```typescript
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
        outline: "text-foreground",
        success:
          "border-transparent bg-green-500 text-white shadow hover:bg-green-600",
        warning:
          "border-transparent bg-orange-500 text-white shadow hover:bg-orange-600",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/ui/badge.tsx
git commit -m "feat: add warning variant to badge component"
```

---

## Task 7: Frontend Dialog Component

**Files:**
- Create: `frontend/src/components/ui/dialog.tsx`

**Step 1: Install Radix UI Dialog**

```bash
cd frontend
npm install @radix-ui/react-dialog
```

**Step 2: Create dialog component**

Create `frontend/src/components/ui/dialog.tsx`:

```typescript
import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { cn } from "@/lib/utils"

const Dialog = DialogPrimitive.Root

const DialogTrigger = DialogPrimitive.Trigger

const DialogPortal = DialogPrimitive.Portal

const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] rounded-lg",
        className
      )}
      {...props}
    >
      {children}
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col space-y-1.5 text-center sm:text-left",
      className
    )}
    {...props}
  />
)
DialogHeader.displayName = "DialogHeader"

const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
)
DialogFooter.displayName = "DialogFooter"

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/ui/dialog.tsx frontend/package.json frontend/package-lock.json
git commit -m "feat: add dialog component for modals"
```

---

## Task 8: Frontend VideoCard Component

**Files:**
- Create: `frontend/src/components/VideoCard.tsx`

**Step 1: Create VideoCard component**

Create `frontend/src/components/VideoCard.tsx`:

```typescript
import { useState } from 'react';
import { SocialVideo, socialApi } from '../services/api';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface VideoCardProps {
  video: SocialVideo;
  onFlagUpdate: () => void;
  onVerifyClick: (videoId: number) => void;
  onDetailsClick: (videoId: number) => void;
}

export function VideoCard({ video, onFlagUpdate, onVerifyClick, onDetailsClick }: VideoCardProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [flagging, setFlagging] = useState(false);

  const badgeVariant = {
    verified: 'success' as const,
    misleading: 'warning' as const,
    unverified: 'secondary' as const,
    fake: 'destructive' as const,
  }[video.dominant_tag];

  const handleFlag = async (flagType: 'verified' | 'misleading' | 'unverified' | 'fake') => {
    setFlagging(true);
    try {
      await socialApi.flagVideo(video.id, flagType);
      onFlagUpdate();
    } catch (error) {
      console.error('Failed to flag video:', error);
      alert('Failed to flag video. Please try again.');
    } finally {
      setFlagging(false);
    }
  };

  const handlePlayPause = (e: React.MouseEvent<HTMLVideoElement>) => {
    const videoElement = e.currentTarget;
    if (videoElement.paused) {
      videoElement.play();
      setIsPlaying(true);
    } else {
      videoElement.pause();
      setIsPlaying(false);
    }
  };

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        {/* Video Player */}
        <div className="relative bg-black aspect-video">
          <video
            src={`http://localhost:3001${video.file_url}`}
            className="w-full h-full object-contain cursor-pointer"
            onClick={handlePlayPause}
            controls
            preload="metadata"
          />

          {/* Status Badge */}
          <div className="absolute top-3 right-3">
            <Badge variant={badgeVariant} className="text-sm">
              {video.dominant_tag.charAt(0).toUpperCase() + video.dominant_tag.slice(1)}
            </Badge>
          </div>
        </div>

        {/* Video Info */}
        <div className="p-4 space-y-3">
          <div>
            <h3 className="font-semibold text-lg">{video.title}</h3>
            {video.description && (
              <p className="text-sm text-muted-foreground mt-1">{video.description}</p>
            )}
          </div>

          {/* View Details Link */}
          <button
            onClick={() => onDetailsClick(video.id)}
            className="text-sm text-blue-600 hover:underline"
          >
            View Details
          </button>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => onVerifyClick(video.id)}
            >
              Verify
            </Button>
          </div>

          {/* Flag Buttons */}
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFlag('verified')}
              disabled={flagging}
              className="text-green-600 border-green-600 hover:bg-green-50"
            >
              ✓ Verified
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFlag('misleading')}
              disabled={flagging}
              className="text-orange-600 border-orange-600 hover:bg-orange-50"
            >
              ⚠ Misleading
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFlag('unverified')}
              disabled={flagging}
              className="text-gray-600 border-gray-600 hover:bg-gray-50"
            >
              ? Unverified
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFlag('fake')}
              disabled={flagging}
              className="text-red-600 border-red-600 hover:bg-red-50"
            >
              ✗ Fake
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/VideoCard.tsx
git commit -m "feat: add VideoCard component with flag buttons"
```

---

## Task 9: Frontend FlagDetailsModal Component

**Files:**
- Create: `frontend/src/components/FlagDetailsModal.tsx`

**Step 1: Create FlagDetailsModal component**

Create `frontend/src/components/FlagDetailsModal.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { FlagCounts, socialApi } from '../services/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';

interface FlagDetailsModalProps {
  videoId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export function FlagDetailsModal({ videoId, isOpen, onClose }: FlagDetailsModalProps) {
  const [flagCounts, setFlagCounts] = useState<FlagCounts | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (videoId && isOpen) {
      setLoading(true);
      socialApi.getFlagCounts(videoId)
        .then(setFlagCounts)
        .catch(err => console.error('Failed to load flag counts:', err))
        .finally(() => setLoading(false));
    }
  }, [videoId, isOpen]);

  const total = flagCounts
    ? flagCounts.verified + flagCounts.misleading + flagCounts.unverified + flagCounts.fake
    : 0;

  const getPercentage = (count: number) => {
    return total > 0 ? Math.round((count / total) * 100) : 0;
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Flag Details</DialogTitle>
          <DialogDescription>
            Community verification breakdown for this video
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : flagCounts ? (
          <div className="space-y-4">
            {/* Verified */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-green-600">Verified</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.verified} ({getPercentage(flagCounts.verified)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.verified)}%` }}
                />
              </div>
            </div>

            {/* Misleading */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-orange-600">Misleading</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.misleading} ({getPercentage(flagCounts.misleading)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.misleading)}%` }}
                />
              </div>
            </div>

            {/* Unverified */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-600">Unverified</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.unverified} ({getPercentage(flagCounts.unverified)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.unverified)}%` }}
                />
              </div>
            </div>

            {/* Fake */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-red-600">Fake</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.fake} ({getPercentage(flagCounts.fake)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.fake)}%` }}
                />
              </div>
            </div>

            <div className="pt-2 border-t text-sm text-muted-foreground">
              Total votes: {total}
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/FlagDetailsModal.tsx
git commit -m "feat: add FlagDetailsModal component"
```

---

## Task 10: Frontend UploadVideoModal Component

**Files:**
- Create: `frontend/src/components/UploadVideoModal.tsx`

**Step 1: Create UploadVideoModal component**

Create `frontend/src/components/UploadVideoModal.tsx`:

```typescript
import { useState } from 'react';
import { socialApi } from '../services/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';

interface UploadVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

export function UploadVideoModal({ isOpen, onClose, onUploadSuccess }: UploadVideoModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !title.trim()) {
      alert('Please select a video and enter a title');
      return;
    }

    setUploading(true);
    setProgress(0);

    try {
      // Simulate progress (real implementation would track actual upload)
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      await socialApi.uploadVideo(file, title, description || undefined);

      clearInterval(progressInterval);
      setProgress(100);

      // Reset form
      setFile(null);
      setTitle('');
      setDescription('');

      onUploadSuccess();
      onClose();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleClose = () => {
    if (!uploading) {
      setFile(null);
      setTitle('');
      setDescription('');
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload Video</DialogTitle>
          <DialogDescription>
            Share a video clip to the community feed
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Input */}
          <div>
            <Label htmlFor="video">Video File</Label>
            <Input
              id="video"
              type="file"
              accept="video/mp4,video/mov,video/avi,video/webm"
              onChange={handleFileChange}
              disabled={uploading}
            />
            {file && (
              <p className="text-sm text-muted-foreground mt-1">
                Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
          </div>

          {/* Video Preview */}
          {file && (
            <div className="aspect-video bg-black rounded overflow-hidden">
              <video
                src={URL.createObjectURL(file)}
                className="w-full h-full object-contain"
                controls
              />
            </div>
          )}

          {/* Title Input */}
          <div>
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter video title"
              disabled={uploading}
            />
          </div>

          {/* Description Input */}
          <div>
            <Label htmlFor="description">Description (optional)</Label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter video description"
              disabled={uploading}
              className="w-full min-h-[80px] px-3 py-2 text-sm rounded-md border border-input bg-background"
            />
          </div>

          {/* Progress Bar */}
          {uploading && (
            <div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-muted-foreground mt-1 text-center">
                Uploading... {progress}%
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={uploading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploading || !file || !title.trim()}
              className="flex-1"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/UploadVideoModal.tsx
git commit -m "feat: add UploadVideoModal component with preview"
```

---

## Task 11: Frontend VerifyPlaceholder Component

**Files:**
- Create: `frontend/src/components/VerifyPlaceholder.tsx`

**Step 1: Create VerifyPlaceholder component**

Create `frontend/src/components/VerifyPlaceholder.tsx`:

```typescript
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface VerifyPlaceholderProps {
  videoId: number;
  videoTitle: string;
  onBack: () => void;
}

export function VerifyPlaceholder({ videoId, videoTitle, onBack }: VerifyPlaceholderProps) {
  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>AI Verification</CardTitle>
          <CardDescription>
            Verifying: {videoTitle}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold mb-2">AI Verification Coming Soon</h3>
            <p className="text-muted-foreground mb-6">
              This feature will use AI to match video clips against authenticated official videos
              on the blockchain, providing instant verification of authenticity.
            </p>
            <div className="bg-muted p-4 rounded-lg text-left space-y-2">
              <p className="text-sm font-medium">Planned Features:</p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Speech-to-text analysis</li>
                <li>Transcript matching against official videos</li>
                <li>Blockchain-verified source tracking</li>
                <li>Timestamp and context verification</li>
              </ul>
            </div>
          </div>

          <Button onClick={onBack} className="w-full">
            Back to Feed
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/VerifyPlaceholder.tsx
git commit -m "feat: add VerifyPlaceholder component"
```

---

## Task 12: Frontend SocialFeed Component

**Files:**
- Create: `frontend/src/components/SocialFeed.tsx`

**Step 1: Create SocialFeed component**

Create `frontend/src/components/SocialFeed.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { SocialVideo, socialApi } from '../services/api';
import { VideoCard } from './VideoCard';
import { UploadVideoModal } from './UploadVideoModal';
import { FlagDetailsModal } from './FlagDetailsModal';
import { VerifyPlaceholder } from './VerifyPlaceholder';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

export function SocialFeed() {
  const [videos, setVideos] = useState<SocialVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [detailsModalVideoId, setDetailsModalVideoId] = useState<number | null>(null);
  const [verifyingVideoId, setVerifyingVideoId] = useState<number | null>(null);

  const loadVideos = async () => {
    try {
      const fetchedVideos = await socialApi.getAllVideos();
      setVideos(fetchedVideos);
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVideos();
  }, []);

  const handleUploadSuccess = () => {
    loadVideos();
  };

  const handleFlagUpdate = () => {
    loadVideos();
  };

  const handleVerifyClick = (videoId: number) => {
    setVerifyingVideoId(videoId);
  };

  const handleDetailsClick = (videoId: number) => {
    setDetailsModalVideoId(videoId);
  };

  const handleBackFromVerify = () => {
    setVerifyingVideoId(null);
  };

  // If verifying a video, show placeholder
  if (verifyingVideoId !== null) {
    const video = videos.find(v => v.id === verifyingVideoId);
    return (
      <VerifyPlaceholder
        videoId={verifyingVideoId}
        videoTitle={video?.title || 'Unknown'}
        onBack={handleBackFromVerify}
      />
    );
  }

  return (
    <div className="relative">
      {/* Header */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Social Feed</CardTitle>
          <CardDescription>
            Browse and verify video clips from the community
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Loading State */}
      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <div className="text-muted-foreground">Loading videos...</div>
          </CardContent>
        </Card>
      ) : videos.length === 0 ? (
        /* Empty State */
        <Card>
          <CardContent className="py-12 text-center">
            <div className="text-6xl mb-4">📹</div>
            <h3 className="text-xl font-semibold mb-2">No videos yet</h3>
            <p className="text-muted-foreground mb-6">
              Be the first to upload a video to the feed!
            </p>
            <Button onClick={() => setUploadModalOpen(true)}>
              Upload Video
            </Button>
          </CardContent>
        </Card>
      ) : (
        /* Video Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map(video => (
            <VideoCard
              key={video.id}
              video={video}
              onFlagUpdate={handleFlagUpdate}
              onVerifyClick={handleVerifyClick}
              onDetailsClick={handleDetailsClick}
            />
          ))}
        </div>
      )}

      {/* Floating Action Button */}
      {videos.length > 0 && (
        <button
          onClick={() => setUploadModalOpen(true)}
          className="fixed bottom-8 right-8 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center text-2xl transition-colors z-40"
          aria-label="Upload video"
        >
          +
        </button>
      )}

      {/* Modals */}
      <UploadVideoModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />

      <FlagDetailsModal
        videoId={detailsModalVideoId}
        isOpen={detailsModalVideoId !== null}
        onClose={() => setDetailsModalVideoId(null)}
      />
    </div>
  );
}
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/SocialFeed.tsx
git commit -m "feat: add SocialFeed component with grid layout"
```

---

## Task 13: Integrate SocialFeed into App

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: Import and use SocialFeed**

Modify `frontend/src/App.tsx` to replace the user placeholder:

```typescript
import { useMemo } from 'react';
import {
  ConnectionProvider,
  WalletProvider,
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';
import { useWallet } from '@solana/wallet-adapter-react';

import { useRoleDetection } from './hooks/useRoleDetection';
import { AdminPanel } from './components/AdminPanel';
import { OfficialPanel } from './components/OfficialPanel';
import { EndorserPanel } from './components/EndorserPanel';
import { SocialFeed } from './components/SocialFeed';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { WalletButton } from './components/WalletButton';

function AppContent() {
  const { publicKey } = useWallet();
  const { role, loading, officialAccount, assignedOfficials } = useRoleDetection(publicKey);

  if (!publicKey) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl mb-2">TruChain</CardTitle>
            <CardDescription className="text-base">
              Video Authenticity Verification System
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground">
              Please connect your wallet to continue
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <CardTitle>Detecting your role...</CardTitle>
            <CardDescription>
              Please wait while we check your permissions on-chain
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="pb-8">
      {/* Role Info Banner */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-muted-foreground">Role:</span>
              <Badge variant={role === 'admin' ? 'default' : role === 'official' ? 'success' : 'secondary'} className="text-sm">
                {role || 'Unknown'}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">Wallet:</span>
              <code className="text-xs bg-muted px-2 py-1 rounded">
                {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
              </code>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      {role === 'admin' && <AdminPanel />}
      {role === 'official' && officialAccount && <OfficialPanel officialAccount={officialAccount} />}
      {role === 'endorser' && <EndorserPanel assignedOfficials={assignedOfficials} />}
      {role === 'user' && <SocialFeed />}
      {!role && (
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-destructive">Error</CardTitle>
            <CardDescription>
              Failed to detect your role. Please try reconnecting your wallet.
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}

function App() {
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);

  const wallets = useMemo(
    () => [new PhantomWalletAdapter()],
    []
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
              <div className="container flex h-16 items-center justify-between px-4 mx-auto max-w-7xl">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold bg-linear-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
                    TruChain
                  </h1>
                </div>
                <WalletButton />
              </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-6 max-w-7xl">
              <AppContent />
            </main>
          </div>
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}

export default App;
```

**Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: integrate SocialFeed for user role"
```

---

## Task 14: End-to-End Testing

**Files:**
- None (manual testing)

**Step 1: Start backend**

```bash
cd backend
npm run dev
```

Expected: "Backend server running on port 3001"

**Step 2: Start frontend**

In new terminal:
```bash
cd frontend
npm run dev
```

Expected: Vite dev server running

**Step 3: Test upload flow**

1. Open browser to frontend URL (usually http://localhost:5173)
2. Connect wallet with 'user' role
3. Should see "No videos yet" empty state
4. Click "Upload Video" button
5. Select a test video file
6. Enter title and description
7. Click "Upload"
8. Video should appear in feed

**Step 4: Test flagging**

1. Click one of the flag buttons (e.g., "Verified")
2. Badge should update to "Verified"
3. Click "View Details"
4. Should see flag breakdown with 1 verified vote

**Step 5: Test verification placeholder**

1. Click "Verify" button on a video
2. Should see placeholder page with "AI Verification Coming Soon"
3. Click "Back to Feed"
4. Should return to feed

**Step 6: Test mobile responsiveness**

1. Open browser dev tools
2. Switch to mobile viewport (375px width)
3. Verify:
   - Videos display in single column
   - Floating "+" button visible
   - Video controls are touch-friendly
   - Modals display correctly

**Step 7: Document any issues**

If issues found, create new tasks to fix them.

**Step 8: Final commit**

```bash
git add -A
git commit -m "test: verify end-to-end social feed functionality"
```

---

## Summary

**Completed Features:**
- ✅ SQLite database for social videos and flags
- ✅ Local filesystem video storage
- ✅ Backend API endpoints (upload, list, flag, get flags)
- ✅ Frontend VideoCard with HTML5 player
- ✅ Community flagging system (4 flag types)
- ✅ Dominant tag display with detail view
- ✅ Upload modal with preview
- ✅ Verification placeholder page
- ✅ Mobile-responsive design
- ✅ Floating action button for upload

**Ready for:**
- Future AI verification integration
- Cloud storage migration
- Auto-play video feature
- User authentication for flags

**Next Steps:**
- Use @superpowers:finishing-a-development-branch when ready to merge
- Test with hackathon judges and users
- Gather feedback for improvements
