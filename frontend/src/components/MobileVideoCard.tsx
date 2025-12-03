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
  const [isMuted, setIsMuted] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [needsInteraction, setNeedsInteraction] = useState(false);

  // Auto-play when card becomes active, pause when inactive
  useEffect(() => {
    const videoEl = videoRef.current;
    if (!videoEl) return;

    if (isActive) {
      // Reset state
      setIsPaused(false);
      videoEl.currentTime = 0;

      // Try to play with sound first
      videoEl.muted = false;
      setIsMuted(false);

      const playPromise = videoEl.play();

      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            // Autoplay with sound worked!
            setNeedsInteraction(false);
          })
          .catch(() => {
            // Autoplay with sound blocked, try muted
            videoEl.muted = true;
            setIsMuted(true);
            videoEl.play()
              .then(() => {
                // Playing muted, show indicator to tap for sound
                setNeedsInteraction(true);
              })
              .catch(() => {
                // Even muted autoplay failed
                setNeedsInteraction(true);
              });
          });
      }
    } else {
      // Pause and reset when scrolling away
      videoEl.pause();
      videoEl.currentTime = 0;
      setIsPaused(false);
      setNeedsInteraction(false);
    }
  }, [isActive]);

  // Handle tap on video - toggle play/pause or enable sound
  const handleVideoTap = () => {
    const videoEl = videoRef.current;
    if (!videoEl) return;

    // If needs interaction (muted due to autoplay policy), unmute on tap
    if (needsInteraction && isMuted) {
      videoEl.muted = false;
      setIsMuted(false);
      setNeedsInteraction(false);
      if (videoEl.paused) {
        videoEl.play();
        setIsPaused(false);
      }
      return;
    }

    // Otherwise toggle play/pause
    if (videoEl.paused) {
      videoEl.play();
      setIsPaused(false);
    } else {
      videoEl.pause();
      setIsPaused(true);
    }
  };

  // Handle mute/unmute toggle
  const handleMuteToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    const videoEl = videoRef.current;
    if (!videoEl) return;

    const newMuted = !isMuted;
    videoEl.muted = newMuted;
    setIsMuted(newMuted);
    setNeedsInteraction(false);
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
        preload="auto"
        onClick={handleVideoTap}
      />

      {/* Paused Indicator - only show when manually paused */}
      {isPaused && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-20 h-20 bg-black/40 backdrop-blur-sm rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}

      {/* Tap for sound indicator - shown when muted due to autoplay policy */}
      {needsInteraction && isMuted && !isPaused && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-black/60 backdrop-blur-sm rounded-full px-4 py-2 flex items-center gap-2">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
            <span className="text-white text-sm font-medium">Tap for sound</span>
          </div>
        </div>
      )}

      {/* Top Gradient */}
      <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-black/50 to-transparent pointer-events-none safe-area-top" />

      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-black/80 via-black/40 to-transparent pointer-events-none" />

      {/* Mute/Unmute Button - Top Right */}
      <button
        onClick={handleMuteToggle}
        className="absolute top-20 right-4 w-10 h-10 bg-black/40 backdrop-blur-sm rounded-full flex items-center justify-center text-white z-10"
      >
        {isMuted ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
        )}
      </button>

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
