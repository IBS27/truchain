import { useEffect, useState } from 'react';
import type { SocialVideo } from '../services/api';
import { socialApi } from '../services/api';
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
    // Reload videos to get updated tags/counts after voting
    loadVideos();
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
      {/* Header with Title and Upload Button */}
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
              onVerifyClick={handleVerifyClick}
              onDetailsClick={handleDetailsClick}
            />
          ))}
        </div>
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
