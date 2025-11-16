import { useState } from 'react';
import type { SocialVideo } from '../services/api';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface VideoCardProps {
  video: SocialVideo;
  onVerifyClick: (videoId: number) => void;
  onDetailsClick: (videoId: number) => void;
}

export function VideoCard({ video, onVerifyClick, onDetailsClick }: VideoCardProps) {
  const [isPlaying, setIsPlaying] = useState(false);

  const badgeVariant = {
    verified: 'success' as const,
    misleading: 'warning' as const,
    unverified: 'secondary' as const,
    fake: 'destructive' as const,
  }[video.dominant_tag];

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
    <div className="relative bg-black rounded-lg overflow-hidden aspect-[9/16] group">
      {/* Video Player - Full Container */}
      <video
        src={`http://localhost:3001${video.file_url}`}
        className="w-full h-full object-cover cursor-pointer"
        onClick={handlePlayPause}
        loop
        playsInline
        preload="metadata"
      />

      {/* Gradient Overlays for Better Text Visibility */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/60 pointer-events-none" />

      {/* Top Right - Status Badge */}
      <div className="absolute top-4 right-4 z-10">
        <div className={`
          px-3 py-1.5 rounded-full font-semibold text-sm shadow-lg backdrop-blur-md
          ${video.dominant_tag === 'verified' ? 'bg-green-600/95 text-white' : ''}
          ${video.dominant_tag === 'misleading' ? 'bg-orange-500/95 text-white' : ''}
          ${video.dominant_tag === 'unverified' ? 'bg-gray-700/95 text-white' : ''}
          ${video.dominant_tag === 'fake' ? 'bg-red-600/95 text-white' : ''}
        `}>
          {video.dominant_tag === 'verified' && '✓ '}
          {video.dominant_tag === 'misleading' && '⚠ '}
          {video.dominant_tag === 'unverified' && '? '}
          {video.dominant_tag === 'fake' && '✗ '}
          {video.dominant_tag.charAt(0).toUpperCase() + video.dominant_tag.slice(1)}
        </div>
      </div>

      {/* Bottom Overlay - Title, Description, Actions */}
      <div className="absolute bottom-0 left-0 right-0 p-4 text-white z-10">
        <div className="flex items-end justify-between gap-4">
          {/* Left Side - Title, Description, View Details */}
          <div className="flex-1 space-y-2">
            {/* Title */}
            <h3 className="font-bold text-lg leading-tight drop-shadow-lg">
              {video.title}
            </h3>

            {/* Description */}
            {video.description && (
              <p className="text-sm leading-tight drop-shadow-lg line-clamp-2 opacity-90">
                {video.description}
              </p>
            )}

            {/* View Details Link */}
            <button
              onClick={() => onDetailsClick(video.id)}
              className="text-sm text-white/90 hover:text-white underline underline-offset-2 drop-shadow-lg block"
            >
              View Details
            </button>
          </div>

          {/* Right Side - Verify Button */}
          <div className="flex-shrink-0">
            <Button
              onClick={() => onVerifyClick(video.id)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-lg"
              size="sm"
            >
              🔍 Verify
            </Button>
          </div>
        </div>
      </div>

      {/* Play/Pause Indicator - Shows on hover */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="bg-black/50 rounded-full p-4 backdrop-blur-sm">
            <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
}
