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
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold gradient-text tracking-tight">For You</h2>
          <p className="text-muted-foreground text-sm mt-1">Discover and verify video authenticity</p>
        </div>
        <Button
          onClick={() => setUploadModalOpen(true)}
          variant="glow"
          size="default"
          className="font-semibold"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Upload Video
        </Button>
      </div>

      {loading ? (
        <Card className="glass-card border-0">
          <CardContent className="py-16 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              <div className="text-muted-foreground">Loading videos...</div>
            </div>
          </CardContent>
        </Card>
      ) : videos.length === 0 ? (
        <Card className="glass-card border-0">
          <CardContent className="py-16 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="w-20 h-20 rounded-2xl bg-secondary/50 flex items-center justify-center">
                <svg className="w-10 h-10 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">No videos yet</h3>
                <p className="text-muted-foreground mb-6">
                  Be the first to upload a video to the feed!
                </p>
              </div>
              <Button onClick={() => setUploadModalOpen(true)} variant="glow">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Upload Video
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video, index) => (
            <div
              key={video.id}
              className="animate-slide-up opacity-0"
              style={{ animationDelay: `${index * 75}ms`, animationFillMode: 'forwards' }}
            >
              <VideoCard
                video={video}
                onVerifyClick={handleVerifyClick}
                onDetailsClick={handleDetailsClick}
              />
            </div>
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
