import { useState } from 'react';
import type { SocialVideo } from '../services/api';
import { socialApi } from '../services/api';
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
