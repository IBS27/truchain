import { useState } from 'react';
import type { SocialVideo } from '../services/api';
import { Button } from './ui/button';

interface VideoCardProps {
  video: SocialVideo;
  onVerifyClick: (videoId: number) => void;
  onDetailsClick: (videoId: number) => void;
}

export function VideoCard({ video, onVerifyClick, onDetailsClick }: VideoCardProps) {
  const [isPlaying, setIsPlaying] = useState(false);

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

  const getStatusConfig = (tag: string) => {
    switch (tag) {
      case 'verified':
        return {
          bg: 'bg-emerald-500/90',
          icon: (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          ),
          label: 'Verified'
        };
      case 'misleading':
        return {
          bg: 'bg-amber-500/90',
          icon: (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          ),
          label: 'Misleading'
        };
      case 'fake':
        return {
          bg: 'bg-red-500/90',
          icon: (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          ),
          label: 'Fake'
        };
      default:
        return {
          bg: 'bg-slate-600/90',
          icon: (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          label: 'Unverified'
        };
    }
  };

  const status = getStatusConfig(video.dominant_tag);

  return (
    <div className="relative bg-black rounded-2xl overflow-hidden aspect-[9/16] group shadow-2xl shadow-black/30 ring-1 ring-white/5 transition-all duration-300 hover:ring-primary/20 hover:shadow-primary/5">
      {/* Video Player */}
      <video
        src={`http://localhost:3001${video.file_url}`}
        className="w-full h-full object-cover cursor-pointer"
        onClick={handlePlayPause}
        loop
        playsInline
        preload="metadata"
      />

      {/* Gradient Overlays */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/80 pointer-events-none" />

      {/* Status Badge - Top Right */}
      <div className="absolute top-4 right-4 z-10">
        <div className={`
          flex items-center gap-1.5 px-3 py-1.5 rounded-full font-semibold text-sm text-white
          backdrop-blur-md shadow-lg ${status.bg}
        `}>
          {status.icon}
          <span>{status.label}</span>
        </div>
      </div>

      {/* Bottom Content */}
      <div className="absolute bottom-0 left-0 right-0 p-5 text-white z-10">
        <div className="flex items-end justify-between gap-4">
          {/* Left - Title & Description */}
          <div className="flex-1 space-y-2">
            <h3 className="font-bold text-lg leading-tight drop-shadow-lg line-clamp-2">
              {video.title}
            </h3>
            {video.description && (
              <p className="text-sm leading-tight drop-shadow-lg line-clamp-2 text-white/80">
                {video.description}
              </p>
            )}
            <button
              onClick={() => onDetailsClick(video.id)}
              className="text-sm text-primary hover:text-primary/80 font-medium transition-colors flex items-center gap-1 group/link"
            >
              <span>View Details</span>
              <svg
                className="w-4 h-4 transition-transform group-hover/link:translate-x-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {/* Right - Verify Button */}
          <div className="flex-shrink-0">
            <Button
              onClick={() => onVerifyClick(video.id)}
              variant="glow"
              size="sm"
              className="font-semibold"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Verify
            </Button>
          </div>
        </div>
      </div>

      {/* Play/Pause Indicator */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-all duration-300">
          <div className="bg-black/40 rounded-full p-5 backdrop-blur-md ring-1 ring-white/10 transform scale-90 group-hover:scale-100 transition-transform">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
}
