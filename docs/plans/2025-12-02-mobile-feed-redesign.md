# Mobile Feed Redesign - TikTok-Style Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the social feed into a professional TikTok-style full-screen vertical scroll experience on mobile, with an immersive verification flow.

**Architecture:** Mobile-first approach using CSS snap-scroll for native-feeling swipe navigation. Desktop keeps enhanced grid layout. Verification uses bottom sheet pattern on mobile, modal on desktop. All interactions optimized for touch with proper loading states and animations.

**Tech Stack:** React 19, Tailwind CSS 4, Radix UI primitives, CSS scroll-snap, tailwindcss-animate

---

## Task 1: Add Bottom Sheet UI Component

**Files:**
- Create: `frontend/src/components/ui/sheet.tsx`

**Step 1: Install Radix Dialog dependency (already installed)**

Radix Dialog is already in package.json - we'll build the sheet on top of it.

**Step 2: Create the Sheet component**

```tsx
import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { cn } from "@/lib/utils"

const Sheet = DialogPrimitive.Root
const SheetTrigger = DialogPrimitive.Trigger
const SheetClose = DialogPrimitive.Close
const SheetPortal = DialogPrimitive.Portal

const SheetOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    className={cn(
      "fixed inset-0 z-50 bg-black/60 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
    ref={ref}
  />
))
SheetOverlay.displayName = DialogPrimitive.Overlay.displayName

const SheetContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & {
    side?: "top" | "bottom" | "left" | "right"
  }
>(({ side = "bottom", className, children, ...props }, ref) => (
  <SheetPortal>
    <SheetOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed z-50 bg-white shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:duration-300",
        side === "bottom" && "inset-x-0 bottom-0 border-t data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom rounded-t-2xl max-h-[90vh]",
        side === "top" && "inset-x-0 top-0 border-b data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top",
        side === "left" && "inset-y-0 left-0 h-full w-3/4 border-r data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left sm:max-w-sm",
        side === "right" && "inset-y-0 right-0 h-full w-3/4 border-r data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right sm:max-w-sm",
        className
      )}
      {...props}
    >
      {/* Drag Handle for mobile */}
      {side === "bottom" && (
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>
      )}
      {children}
    </DialogPrimitive.Content>
  </SheetPortal>
))
SheetContent.displayName = DialogPrimitive.Content.displayName

const SheetHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("flex flex-col space-y-2 px-4 pb-4", className)}
    {...props}
  />
)
SheetHeader.displayName = "SheetHeader"

const SheetTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn("text-lg font-semibold text-foreground", className)}
    {...props}
  />
))
SheetTitle.displayName = DialogPrimitive.Title.displayName

const SheetDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
SheetDescription.displayName = DialogPrimitive.Description.displayName

export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
}
```

**Step 3: Verify component compiles**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build 2>&1 | head -20`
Expected: No TypeScript errors related to sheet.tsx

---

## Task 2: Add Custom CSS for Scroll Snap and Mobile Animations

**Files:**
- Modify: `frontend/src/index.css`

**Step 1: Add scroll-snap and mobile feed styles**

Add the following at the end of index.css:

```css
/* TikTok-style Mobile Feed */
.mobile-feed-container {
  scroll-snap-type: y mandatory;
  overflow-y: scroll;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.mobile-feed-container::-webkit-scrollbar {
  display: none;
}

.mobile-feed-item {
  scroll-snap-align: start;
  scroll-snap-stop: always;
}

/* Video loading skeleton pulse */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.skeleton-pulse {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

/* Slide up animation for action buttons */
@keyframes slide-up-fade {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slide-up-fade 0.3s ease-out forwards;
}

/* Staggered animation delays for action buttons */
.animate-delay-100 { animation-delay: 100ms; }
.animate-delay-200 { animation-delay: 200ms; }
.animate-delay-300 { animation-delay: 300ms; }

/* Progress ring animation */
@keyframes progress-ring {
  0% { stroke-dashoffset: 100; }
  100% { stroke-dashoffset: 0; }
}

/* Safe area insets for notched phones */
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 20px);
}

.safe-area-top {
  padding-top: env(safe-area-inset-top, 0px);
}
```

**Step 2: Verify styles are applied**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build`
Expected: Build succeeds

---

## Task 3: Create TikTok-Style Video Card Component

**Files:**
- Create: `frontend/src/components/MobileVideoCard.tsx`

**Step 1: Create the immersive video card**

```tsx
import { useState, useRef, useEffect } from 'react';
import type { SocialVideo } from '../services/api';

interface MobileVideoCardProps {
  video: SocialVideo;
  isActive: boolean;
  onVerifyClick: () => void;
  onDetailsClick: () => void;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export function MobileVideoCard({ video, isActive, onVerifyClick, onDetailsClick }: MobileVideoCardProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showPlayButton, setShowPlayButton] = useState(true);

  // Auto-play when card becomes active, pause when inactive
  useEffect(() => {
    if (!videoRef.current) return;

    if (isActive) {
      videoRef.current.play().then(() => {
        setIsPlaying(true);
        setShowPlayButton(false);
      }).catch(() => {
        // Autoplay blocked, show play button
        setShowPlayButton(true);
      });
    } else {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  }, [isActive]);

  const handleVideoTap = () => {
    if (!videoRef.current) return;

    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
      setShowPlayButton(false);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
      setShowPlayButton(true);
    }
  };

  const getStatusConfig = () => {
    switch (video.dominant_tag) {
      case 'verified':
        return { icon: '✓', label: 'Verified', bg: 'bg-green-500', ring: 'ring-green-400' };
      case 'misleading':
        return { icon: '⚠', label: 'Misleading', bg: 'bg-orange-500', ring: 'ring-orange-400' };
      case 'fake':
        return { icon: '✗', label: 'Fake', bg: 'bg-red-500', ring: 'ring-red-400' };
      default:
        return { icon: '?', label: 'Unverified', bg: 'bg-gray-500', ring: 'ring-gray-400' };
    }
  };

  const status = getStatusConfig();

  return (
    <div className="mobile-feed-item relative w-full h-full bg-black flex items-center justify-center">
      {/* Video Player - Full Screen */}
      <video
        ref={videoRef}
        src={`${BACKEND_URL}${video.file_url}`}
        className="w-full h-full object-contain"
        loop
        playsInline
        muted={false}
        preload="auto"
        onClick={handleVideoTap}
      />

      {/* Play Button Overlay */}
      {showPlayButton && (
        <button
          onClick={handleVideoTap}
          className="absolute inset-0 flex items-center justify-center bg-black/20"
        >
          <div className="w-20 h-20 bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </button>
      )}

      {/* Top Gradient */}
      <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-black/50 to-transparent pointer-events-none safe-area-top" />

      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-black/80 via-black/40 to-transparent pointer-events-none" />

      {/* Right Side Action Buttons */}
      <div className="absolute right-3 bottom-32 flex flex-col items-center gap-5 safe-area-bottom">
        {/* Status Badge */}
        <button
          onClick={onDetailsClick}
          className={`flex flex-col items-center animate-slide-up opacity-0 animate-delay-100`}
        >
          <div className={`w-12 h-12 rounded-full ${status.bg} flex items-center justify-center text-white text-xl shadow-lg ring-2 ${status.ring} ring-offset-2 ring-offset-black/50`}>
            {status.icon}
          </div>
          <span className="text-white text-xs mt-1 font-medium drop-shadow-lg">{status.label}</span>
        </button>

        {/* Verify Button */}
        <button
          onClick={onVerifyClick}
          className="flex flex-col items-center animate-slide-up opacity-0 animate-delay-200"
        >
          <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white shadow-lg ring-2 ring-blue-400 ring-offset-2 ring-offset-black/50 active:scale-95 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span className="text-white text-xs mt-1 font-medium drop-shadow-lg">Verify</span>
        </button>

        {/* Share Button */}
        <button className="flex flex-col items-center animate-slide-up opacity-0 animate-delay-300">
          <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white shadow-lg active:scale-95 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </div>
          <span className="text-white text-xs mt-1 font-medium drop-shadow-lg">Share</span>
        </button>
      </div>

      {/* Bottom Info */}
      <div className="absolute bottom-6 left-4 right-20 safe-area-bottom">
        <h3 className="text-white font-bold text-lg drop-shadow-lg line-clamp-2">
          {video.title}
        </h3>
        {video.description && (
          <p className="text-white/90 text-sm mt-1 drop-shadow-lg line-clamp-2">
            {video.description}
          </p>
        )}

        {/* Vote counts row */}
        <div className="flex items-center gap-3 mt-3">
          <span className="text-green-400 text-xs font-medium">
            ✓ {video.verified_count}
          </span>
          <span className="text-orange-400 text-xs font-medium">
            ⚠ {video.misleading_count}
          </span>
          <span className="text-red-400 text-xs font-medium">
            ✗ {video.fake_count}
          </span>
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build 2>&1 | head -30`
Expected: No TypeScript errors

---

## Task 4: Create Mobile Verification Sheet Component

**Files:**
- Create: `frontend/src/components/MobileVerifySheet.tsx`

**Step 1: Create the professional verification sheet**

```tsx
import { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';
import { Button } from './ui/button';
import { verificationApi, socialApi } from '../services/api';
import type { AIVerificationResult, SocialVideo } from '../services/api';

interface MobileVerifySheetProps {
  video: SocialVideo;
  isOpen: boolean;
  onClose: () => void;
  onVideoUpdate: (video: SocialVideo) => void;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export function MobileVerifySheet({ video, isOpen, onClose, onVideoUpdate }: MobileVerifySheetProps) {
  const [stage, setStage] = useState<'initial' | 'verifying' | 'results' | 'voting'>('initial');
  const [result, setResult] = useState<AIVerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [votingFor, setVotingFor] = useState<string | null>(null);

  const handleVerify = async () => {
    setStage('verifying');
    setError(null);

    try {
      const videoResponse = await fetch(`${BACKEND_URL}${video.file_url}`);
      const videoBlob = await videoResponse.blob();
      const videoFile = new File([videoBlob], video.title || 'clip.mp4', { type: 'video/mp4' });

      const verificationResult = await verificationApi.verifyClip(videoFile);
      setResult(verificationResult);
      setStage('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
      setStage('initial');
    }
  };

  const handleVote = async (flagType: 'verified' | 'misleading' | 'unverified' | 'fake') => {
    setVotingFor(flagType);
    try {
      const response = await socialApi.flagVideo(video.id, flagType);
      onVideoUpdate(response.video);
      onClose();
    } catch (err) {
      setError('Failed to submit vote');
    } finally {
      setVotingFor(null);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getResultColor = () => {
    if (!result) return 'bg-gray-100';
    switch (result.verification_type) {
      case 'full': return 'bg-green-50 border-green-200';
      case 'content_only': return 'bg-orange-50 border-orange-200';
      default: return 'bg-red-50 border-red-200';
    }
  };

  const getResultIcon = () => {
    if (!result) return null;
    switch (result.verification_type) {
      case 'full': return <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center text-white text-3xl">✓</div>;
      case 'content_only': return <div className="w-16 h-16 rounded-full bg-orange-500 flex items-center justify-center text-white text-3xl">⚠</div>;
      default: return <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center text-white text-3xl">✗</div>;
    }
  };

  const getResultTitle = () => {
    if (!result) return '';
    switch (result.verification_type) {
      case 'full': return 'Verified Authentic';
      case 'content_only': return 'Content Match Only';
      default: return 'Not Verified';
    }
  };

  const getResultDescription = () => {
    if (!result) return '';
    switch (result.verification_type) {
      case 'full': return 'Content and speaker voice match an official source.';
      case 'content_only': return 'Words match but voice differs. Possible deepfake.';
      default: return 'No matching official source found.';
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="bottom" className="max-h-[85vh] overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="text-center">
            {stage === 'initial' && 'Verify This Clip'}
            {stage === 'verifying' && 'Analyzing...'}
            {stage === 'results' && 'Verification Result'}
            {stage === 'voting' && 'Submit Your Vote'}
          </SheetTitle>
        </SheetHeader>

        <div className="px-4 pb-8 space-y-6">
          {/* Initial State */}
          {stage === 'initial' && (
            <>
              <p className="text-center text-muted-foreground text-sm">
                Our AI will analyze this clip against official government video sources to verify authenticity.
              </p>

              <Button
                onClick={handleVerify}
                className="w-full h-14 text-lg bg-blue-600 hover:bg-blue-700"
              >
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Start AI Verification
              </Button>

              {error && (
                <p className="text-center text-red-500 text-sm">{error}</p>
              )}
            </>
          )}

          {/* Verifying State */}
          {stage === 'verifying' && (
            <div className="py-8 flex flex-col items-center gap-4">
              <div className="relative w-20 h-20">
                <svg className="w-20 h-20 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
              <div className="text-center">
                <p className="font-medium">Analyzing video...</p>
                <p className="text-sm text-muted-foreground mt-1">Matching speech and verifying speaker</p>
              </div>
            </div>
          )}

          {/* Results State */}
          {stage === 'results' && result && (
            <>
              {/* Result Card */}
              <div className={`rounded-2xl border-2 p-6 ${getResultColor()}`}>
                <div className="flex flex-col items-center text-center gap-3">
                  {getResultIcon()}
                  <h3 className="text-xl font-bold">{getResultTitle()}</h3>
                  <p className="text-sm text-muted-foreground">{getResultDescription()}</p>
                </div>
              </div>

              {/* Match Details */}
              {result.best_match && (
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <h4 className="font-semibold text-sm">Source Match</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Timestamp:</span>
                      <span className="ml-1 font-medium">
                        {formatTime(result.best_match.start_time)} - {formatTime(result.best_match.end_time)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Match:</span>
                      <span className="ml-1 font-medium text-green-600">
                        {(result.best_match.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    className="w-full mt-2"
                    onClick={() => {
                      const filename = result.best_match!.video_path.split('/').pop() || result.best_match!.video_name;
                      const underscoreIndex = filename.indexOf('_');
                      const cid = underscoreIndex > 0 ? filename.substring(0, underscoreIndex) : filename.replace(/\.[^/.]+$/, '');
                      const videoUrl = cid
                        ? `${BACKEND_URL}/api/ipfs/download/${cid}#t=${Math.floor(result.best_match!.start_time)}`
                        : `${BACKEND_URL}/official-videos/${encodeURIComponent(filename)}#t=${Math.floor(result.best_match!.start_time)}`;
                      window.open(videoUrl, '_blank');
                    }}
                  >
                    View Official Source
                  </Button>
                </div>
              )}

              {/* Speaker Verification */}
              {result.speaker_verification && (
                <div className={`rounded-xl p-4 ${result.speaker_verification.verified ? 'bg-green-50' : 'bg-orange-50'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-sm">Voice Match</h4>
                      <p className="text-xs text-muted-foreground">{result.speaker_verification.message}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-lg font-bold ${result.speaker_verification.verified ? 'text-green-600' : 'text-orange-600'}`}>
                        {(result.speaker_verification.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Vote Section */}
              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-3 text-center">Cast Your Vote</h4>
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    onClick={() => handleVote('verified')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-green-300 text-green-700 hover:bg-green-50"
                  >
                    <span className="text-lg">✓</span>
                    <span className="text-xs">Verified ({video.verified_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('misleading')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-orange-300 text-orange-700 hover:bg-orange-50"
                  >
                    <span className="text-lg">⚠</span>
                    <span className="text-xs">Misleading ({video.misleading_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('unverified')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    <span className="text-lg">?</span>
                    <span className="text-xs">Unsure ({video.unverified_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('fake')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-red-300 text-red-700 hover:bg-red-50"
                  >
                    <span className="text-lg">✗</span>
                    <span className="text-xs">Fake ({video.fake_count})</span>
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build 2>&1 | head -30`
Expected: No TypeScript errors

---

## Task 5: Create Loading Skeleton Component

**Files:**
- Create: `frontend/src/components/VideoSkeleton.tsx`

**Step 1: Create the skeleton loader**

```tsx
export function VideoSkeleton() {
  return (
    <div className="mobile-feed-item relative w-full h-full bg-gray-900 flex items-center justify-center">
      {/* Pulsing background */}
      <div className="absolute inset-0 skeleton-pulse bg-gray-800" />

      {/* Fake action buttons on right */}
      <div className="absolute right-3 bottom-32 flex flex-col items-center gap-5">
        <div className="w-12 h-12 rounded-full bg-gray-700 skeleton-pulse" />
        <div className="w-12 h-12 rounded-full bg-gray-700 skeleton-pulse" />
        <div className="w-12 h-12 rounded-full bg-gray-700 skeleton-pulse" />
      </div>

      {/* Fake bottom info */}
      <div className="absolute bottom-6 left-4 right-20 space-y-3">
        <div className="h-6 w-3/4 bg-gray-700 rounded skeleton-pulse" />
        <div className="h-4 w-1/2 bg-gray-700 rounded skeleton-pulse" />
        <div className="flex gap-3">
          <div className="h-4 w-12 bg-gray-700 rounded skeleton-pulse" />
          <div className="h-4 w-12 bg-gray-700 rounded skeleton-pulse" />
          <div className="h-4 w-12 bg-gray-700 rounded skeleton-pulse" />
        </div>
      </div>

      {/* Center loading indicator */}
      <div className="relative z-10 flex flex-col items-center gap-3">
        <div className="w-16 h-16 rounded-full border-4 border-gray-600 border-t-blue-500 animate-spin" />
        <span className="text-gray-400 text-sm">Loading videos...</span>
      </div>
    </div>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build 2>&1 | head -20`
Expected: No errors

---

## Task 6: Create New Mobile-First Social Feed

**Files:**
- Create: `frontend/src/components/MobileSocialFeed.tsx`

**Step 1: Create the TikTok-style feed container**

```tsx
import { useEffect, useState, useRef, useCallback } from 'react';
import type { SocialVideo } from '../services/api';
import { socialApi } from '../services/api';
import { MobileVideoCard } from './MobileVideoCard';
import { MobileVerifySheet } from './MobileVerifySheet';
import { FlagDetailsModal } from './FlagDetailsModal';
import { UploadVideoModal } from './UploadVideoModal';
import { VideoSkeleton } from './VideoSkeleton';

export function MobileSocialFeed() {
  const [videos, setVideos] = useState<SocialVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const [verifyingVideo, setVerifyingVideo] = useState<SocialVideo | null>(null);
  const [detailsVideoId, setDetailsVideoId] = useState<number | null>(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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

  // Track which video is in view using Intersection Observer
  useEffect(() => {
    if (!containerRef.current || videos.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const index = Number(entry.target.getAttribute('data-index'));
            if (!isNaN(index)) {
              setActiveIndex(index);
            }
          }
        });
      },
      {
        root: containerRef.current,
        threshold: 0.6,
      }
    );

    const items = containerRef.current.querySelectorAll('.mobile-feed-item');
    items.forEach((item) => observer.observe(item));

    return () => observer.disconnect();
  }, [videos]);

  const handleVideoUpdate = useCallback((updatedVideo: SocialVideo) => {
    setVideos(prev => prev.map(v => v.id === updatedVideo.id ? updatedVideo : v));
  }, []);

  const handleUploadSuccess = () => {
    loadVideos();
  };

  // Calculate viewport height for mobile (accounting for browser chrome)
  const feedHeight = 'calc(100vh - 64px)'; // 64px for header

  if (loading) {
    return (
      <div className="fixed inset-0 top-16 bg-black">
        <VideoSkeleton />
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="fixed inset-0 top-16 bg-black flex flex-col items-center justify-center text-white p-4">
        <div className="text-6xl mb-4">📹</div>
        <h3 className="text-xl font-semibold mb-2">No videos yet</h3>
        <p className="text-gray-400 mb-6 text-center">
          Be the first to upload a video to the feed!
        </p>
        <button
          onClick={() => setUploadModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-full"
        >
          Upload Video
        </button>

        <UploadVideoModal
          isOpen={uploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
          onUploadSuccess={handleUploadSuccess}
        />
      </div>
    );
  }

  return (
    <>
      {/* Full-screen feed container */}
      <div
        ref={containerRef}
        className="mobile-feed-container fixed inset-0 top-16 bg-black"
        style={{ height: feedHeight }}
      >
        {videos.map((video, index) => (
          <div
            key={video.id}
            data-index={index}
            className="mobile-feed-item"
            style={{ height: feedHeight }}
          >
            <MobileVideoCard
              video={video}
              isActive={index === activeIndex}
              onVerifyClick={() => setVerifyingVideo(video)}
              onDetailsClick={() => setDetailsVideoId(video.id)}
            />
          </div>
        ))}
      </div>

      {/* Floating Upload Button */}
      <button
        onClick={() => setUploadModalOpen(true)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 bg-blue-600 hover:bg-blue-700 rounded-full shadow-lg flex items-center justify-center text-white active:scale-95 transition-transform safe-area-bottom"
      >
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </button>

      {/* Video indicator dots */}
      <div className="fixed right-2 top-1/2 -translate-y-1/2 z-40 flex flex-col gap-1.5">
        {videos.slice(0, 10).map((_, index) => (
          <div
            key={index}
            className={`w-1.5 h-1.5 rounded-full transition-all ${
              index === activeIndex ? 'bg-white scale-125' : 'bg-white/40'
            }`}
          />
        ))}
        {videos.length > 10 && (
          <div className="text-white/60 text-xs text-center">...</div>
        )}
      </div>

      {/* Modals */}
      {verifyingVideo && (
        <MobileVerifySheet
          video={verifyingVideo}
          isOpen={true}
          onClose={() => setVerifyingVideo(null)}
          onVideoUpdate={handleVideoUpdate}
        />
      )}

      <FlagDetailsModal
        videoId={detailsVideoId}
        isOpen={detailsVideoId !== null}
        onClose={() => setDetailsVideoId(null)}
      />

      <UploadVideoModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build 2>&1 | head -30`
Expected: No TypeScript errors

---

## Task 7: Update SocialFeed to Switch Between Mobile and Desktop

**Files:**
- Modify: `frontend/src/components/SocialFeed.tsx`

**Step 1: Add responsive switching logic**

Replace the entire SocialFeed.tsx content with:

```tsx
import { useEffect, useState } from 'react';
import type { SocialVideo } from '../services/api';
import { socialApi } from '../services/api';
import { VideoCard } from './VideoCard';
import { UploadVideoModal } from './UploadVideoModal';
import { FlagDetailsModal } from './FlagDetailsModal';
import { VerifyClipModal } from './VerifyClipModal';
import { MobileSocialFeed } from './MobileSocialFeed';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return isMobile;
}

export function SocialFeed() {
  const isMobile = useIsMobile();
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

  // Use mobile feed on small screens
  if (isMobile) {
    return <MobileSocialFeed />;
  }

  // Desktop: Original grid layout (kept for larger screens)
  const handleUploadSuccess = () => {
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
    loadVideos();
  };

  if (verifyingVideoId !== null) {
    const video = videos.find(v => v.id === verifyingVideoId);
    if (!video) return null;
    return (
      <VerifyClipModal
        video={video}
        onBack={handleBackFromVerify}
      />
    );
  }

  return (
    <div className="relative">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">For You</h2>
        <Button
          onClick={() => setUploadModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-md"
          size="sm"
        >
          + Upload Video
        </Button>
      </div>

      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <div className="text-muted-foreground">Loading videos...</div>
          </CardContent>
        </Card>
      ) : videos.length === 0 ? (
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map(video => (
            <VideoCard
              key={video.id}
              video={video}
              onVerifyClick={handleVerifyClick}
              onDetailsClick={handleDetailsClick}
            />
          ))}
        </div>
      )}

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

**Step 2: Verify build succeeds**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build`
Expected: Build completes successfully

---

## Task 8: Hide Header on Mobile Feed

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: Add state for hiding header on mobile feed**

Find the header section (around line 118) and update it to be conditionally visible. The mobile feed already handles its own spacing, so we need to make the header more compact or hide it when in full-screen feed mode.

Replace the header section with:

```tsx
{/* Header - Compact on mobile */}
<header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
  <div className="container flex h-14 md:h-16 items-center justify-between px-4 mx-auto max-w-7xl">
    <div className="flex items-center gap-2">
      <h1 className="text-xl md:text-2xl font-bold bg-linear-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
        TruChain
      </h1>
    </div>
    <WalletButton />
  </div>
</header>
```

Also update the main content area (around line 130):

```tsx
{/* Main Content */}
<main className="md:container md:mx-auto md:px-4 md:py-6 md:max-w-7xl">
  <AppContent />
</main>
```

**Step 2: Verify build succeeds**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build`
Expected: Build completes

---

## Task 9: Final Build and Manual Test

**Step 1: Run final build**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run build`
Expected: Build completes with no errors

**Step 2: Start dev server for testing**

Run: `cd /Users/srinivasib/Developer/truchain/frontend && npm run dev`
Expected: Dev server starts

**Step 3: Manual testing checklist**

Open browser dev tools, toggle mobile view (iPhone 14 Pro recommended):

- [ ] Videos fill entire screen height
- [ ] Swipe up/down snaps to next video
- [ ] Active video auto-plays
- [ ] Inactive videos are paused
- [ ] Verify button opens bottom sheet
- [ ] Bottom sheet has drag handle
- [ ] Verification flow works (verify -> results -> vote)
- [ ] Action buttons animate in with stagger
- [ ] Status badge shows correct color/icon
- [ ] Upload FAB is visible and works
- [ ] Video indicator dots show position

**Step 4: Commit changes**

```bash
git add frontend/src/components/ui/sheet.tsx \
        frontend/src/components/MobileVideoCard.tsx \
        frontend/src/components/MobileVerifySheet.tsx \
        frontend/src/components/VideoSkeleton.tsx \
        frontend/src/components/MobileSocialFeed.tsx \
        frontend/src/components/SocialFeed.tsx \
        frontend/src/index.css \
        frontend/src/App.tsx

git commit -m "feat: add TikTok-style mobile feed with professional verification UI

- Add full-screen vertical scroll with snap behavior
- Create immersive video cards with side action buttons
- Add bottom sheet verification flow
- Add skeleton loading states
- Make header compact on mobile
- Keep grid layout for desktop"
```

---

## Summary

This plan creates a professional TikTok-style mobile experience with:

1. **Full-screen vertical scroll** - Videos fill the viewport with snap-scroll
2. **Auto-play behavior** - Active video plays, others pause
3. **TikTok-style action buttons** - Right-side floating buttons with animations
4. **Professional verification sheet** - Bottom sheet with stages (initial -> verifying -> results -> voting)
5. **Loading skeletons** - Professional loading states
6. **Responsive switching** - Mobile gets immersive feed, desktop keeps grid
7. **Safe area handling** - Proper insets for notched phones

Total: 9 tasks, approximately 30-45 minutes of implementation time.
