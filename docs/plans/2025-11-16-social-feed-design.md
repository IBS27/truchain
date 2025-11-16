# Social Media Feed Design

**Date**: 2025-11-16
**Purpose**: Add TikTok/Instagram-style short-form video feed for regular users to browse, upload, and verify video clips.

---

## Overview

A social media platform accessible only to users with the 'user' role. Features include:
- Short-form video feed (newest first)
- Video upload with floating action button + modal
- Community flagging system (Verified/Misleading/Unverified/Fake)
- Placeholder verification page (for future AI integration)
- Mobile-responsive design matching existing app styling

---

## Backend Architecture

### New API Endpoints

**Base path**: `/api/social`

1. **POST /api/social/videos/upload**
   - Accepts: `multipart/form-data` with video file, title, description
   - Stores: Video to `/backend/uploads/social/{timestamp}-{randomId}.mp4`
   - Returns: `{ id, title, description, fileUrl, uploadedAt, dominantTag, flagCounts }`

2. **GET /api/social/videos**
   - Returns: Array of videos ordered by `uploaded_at DESC`
   - Response includes: metadata, file URL, dominant tag, total flag counts

3. **POST /api/social/videos/:id/flag**
   - Body: `{ flagType: 'verified' | 'misleading' | 'unverified' | 'fake' }`
   - Updates flag counts and recalculates dominant tag
   - Returns: Updated flag counts

4. **GET /api/social/videos/:id/flags**
   - Returns: Detailed breakdown of all flag types with counts

### Database Schema (SQLite)

```sql
CREATE TABLE social_videos (
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

CREATE TABLE social_flags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id INTEGER NOT NULL,
  flag_type TEXT NOT NULL,
  flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (video_id) REFERENCES social_videos(id)
);
```

### File Storage

- **Location**: `/backend/uploads/social/`
- **Serving**: Express static middleware: `app.use('/uploads', express.static('uploads'))`
- **URLs**: `http://localhost:3001/uploads/social/{filename}`

### Dominant Tag Logic

After each flag:
1. Count all flags for the video
2. Determine which flag type has the most votes
3. Update `dominant_tag` field to the winner
4. Default to 'unverified' if no flags exist

---

## Frontend Architecture

### Component Structure

**Location**: `/frontend/src/components/`

1. **SocialFeed.tsx** - Main feed container
   - Replaces placeholder for `role === 'user'`
   - Fetches videos on mount
   - Displays VideoCard list
   - Includes floating "+" button for upload
   - Responsive layout: single column mobile, centered max-width desktop

2. **VideoCard.tsx** - Individual video display
   - HTML5 `<video>` element with controls
   - Title and description overlay
   - Dominant status badge (top-right corner)
   - Action buttons:
     - "Verify" → navigates to placeholder
     - "View Details" → opens FlagDetailsModal
   - Flag voting buttons (4 buttons in row/grid)

3. **UploadVideoModal.tsx** - Video upload interface
   - File input with video preview
   - Title input (required)
   - Description textarea (optional)
   - Upload progress indicator
   - Success/error handling

4. **FlagDetailsModal.tsx** - Detailed flag breakdown
   - Shows all four flag types with counts and percentages
   - Visual representation (bars or simple list)
   - Close button

5. **VerifyPlaceholder.tsx** - Temporary verification page
   - "AI Verification Coming Soon" message
   - Video title and basic info
   - Back button to feed

### Styling

**Mobile-First**:
- CSS Grid: single column on mobile
- Video aspect ratio: 9:16 (portrait) on mobile, responsive on desktop
- Smooth scrolling: Native CSS `scroll-behavior: smooth`
- Touch-friendly: 44px minimum button size

**Design Consistency**:
- shadcn/ui components (Button, Badge, Card, Input, Label)
- Existing color scheme
- Status badge colors:
  - Verified: green (success)
  - Unverified: gray (secondary)
  - Misleading: yellow/orange (warning - may need new variant)
  - Fake: red (destructive)

---

## User Flows

### 1. Viewing the Feed
- User role sees SocialFeed component
- Videos load newest first
- Scroll through feed smoothly
- Each video shows: player, title, dominant badge, buttons

### 2. Uploading a Video
1. Click floating "+" button
2. UploadVideoModal opens
3. Select video file → preview appears
4. Enter title (required) and description (optional)
5. Click "Upload" → progress bar
6. Success: modal closes, feed refreshes, new video at top
7. Error: show message, allow retry

### 3. Flagging a Video
1. Click one of four flag buttons
2. API updates flag counts
3. Dominant badge updates immediately (optimistic update)
4. Button shows visual feedback

### 4. Viewing Flag Details
1. Click "View Details" link
2. Modal shows breakdown: "Verified: 45 (60%), Misleading: 15 (20%), ..."
3. Close to return

### 5. Verifying a Video
1. Click "Verify" button
2. Navigate to verification view
3. See placeholder message
4. Back button returns to feed

---

## Technical Implementation

### Video Player
- Native HTML5 `<video>` element
- Controls: play/pause overlay, progress bar, volume
- `preload="metadata"` for bandwidth efficiency
- Poster: first frame or placeholder

### State Management
- React useState (no Redux for MVP)
- Video list in SocialFeed state
- Optimistic updates for flags

### API Integration
- Extend `/frontend/src/services/api.ts`
- Functions: `getSocialVideos()`, `uploadSocialVideo()`, `flagVideo()`, `getVideoFlags()`
- Base URL: `http://localhost:3001`

### Routing
- Initial: conditional rendering with state (no router needed)
- Optional: add react-router-dom for cleaner verify page navigation

### Access Control
- Social feed only for `role === 'user'`
- Admin can access but not shown in navigation
- Wallet already connected via role detection

---

## MVP Scope

**Included**:
- Video upload and storage (local filesystem)
- Feed display with newest first
- Community flagging system
- Dominant tag display with detail view
- Mobile-responsive UI
- Placeholder verification page

**Not Included** (Future):
- Auto-play videos
- Video pagination
- User authentication for flags
- AI-based verification (placeholder only)
- Cloud storage (local filesystem for demo)
- Video compression/transcoding

---

## Next Steps

1. Setup backend database and routes
2. Create upload directory and static serving
3. Build frontend components
4. Integrate API calls
5. Test upload and flagging flows
6. Verify mobile responsiveness
