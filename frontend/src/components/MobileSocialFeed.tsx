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
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);

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
          if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
            const index = Number(entry.target.getAttribute('data-index'));
            if (!isNaN(index) && index !== activeIndex) {
              setActiveIndex(index);
            }
          }
        });
      },
      {
        root: containerRef.current,
        threshold: [0.5, 0.75, 1.0],
        rootMargin: '0px',
      }
    );

    // Observe each item
    itemRefs.current.forEach((item) => {
      if (item) observer.observe(item);
    });

    return () => observer.disconnect();
  }, [videos, activeIndex]);

  const handleVideoUpdate = useCallback((updatedVideo: SocialVideo) => {
    setVideos(prev => prev.map(v => v.id === updatedVideo.id ? updatedVideo : v));
  }, []);

  const handleUploadSuccess = () => {
    loadVideos();
  };

  // Calculate viewport height for mobile (accounting for browser chrome)
  const feedHeight = 'calc(100vh - 56px)'; // 56px for compact header (h-14)

  if (loading) {
    return (
      <div className="fixed inset-0 top-14 bg-black">
        <VideoSkeleton />
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="fixed inset-0 top-14 bg-black flex flex-col items-center justify-center text-white p-4">
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
        className="mobile-feed-container fixed inset-0 top-14 bg-black"
        style={{ height: feedHeight }}
      >
        {videos.map((video, index) => (
          <div
            key={video.id}
            data-index={index}
            ref={(el) => { itemRefs.current[index] = el; }}
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
