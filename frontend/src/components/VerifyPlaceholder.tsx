import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { socialApi } from '../services/api';
import type { SocialVideo } from '../services/api';

interface VerifyPlaceholderProps {
  videoId: number;
  videoTitle: string;
  onBack: () => void;
}

export function VerifyPlaceholder({ videoId, videoTitle, onBack }: VerifyPlaceholderProps) {
  const [flagging, setFlagging] = useState(false);
  const [video, setVideo] = useState<SocialVideo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVideo();
  }, [videoId]);

  const loadVideo = async () => {
    try {
      const videos = await socialApi.getAllVideos();
      const foundVideo = videos.find(v => v.id === videoId);
      setVideo(foundVideo || null);
    } catch (error) {
      console.error('Failed to load video:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFlag = async (flagType: 'verified' | 'misleading' | 'unverified' | 'fake') => {
    setFlagging(true);
    try {
      await socialApi.flagVideo(videoId, flagType);
      await loadVideo(); // Reload to get updated stats
    } catch (error) {
      console.error('Failed to flag video:', error);
      alert('Failed to flag video. Please try again.');
    } finally {
      setFlagging(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>AI Verification</CardTitle>
          <CardDescription>
            Verifying: {videoTitle}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Video Preview */}
          {video && (
            <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
              <video
                src={`http://localhost:3001${video.file_url}`}
                className="w-full h-full object-contain"
                controls
                preload="metadata"
              />
            </div>
          )}

          {/* AI Verification Section */}
          <div className="text-center py-8">
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

          {/* Voting Section */}
          <div className="border-t pt-4">
            <h4 className="font-semibold text-base mb-3">Cast Your Vote</h4>

            <div className="flex gap-2 flex-wrap">
              <Button
                variant="outline"
                onClick={() => handleFlag('verified')}
                disabled={flagging}
                className="flex-1 min-w-[120px] text-green-600 border-green-600 hover:bg-green-50 hover:text-green-700"
                size="sm"
              >
                <span className="mr-1">✓</span>
                Verified
                {video && <span className="ml-1 text-xs opacity-70">({video.verified_count})</span>}
              </Button>

              <Button
                variant="outline"
                onClick={() => handleFlag('misleading')}
                disabled={flagging}
                className="flex-1 min-w-[120px] text-orange-600 border-orange-600 hover:bg-orange-50 hover:text-orange-700"
                size="sm"
              >
                <span className="mr-1">⚠</span>
                Misleading
                {video && <span className="ml-1 text-xs opacity-70">({video.misleading_count})</span>}
              </Button>

              <Button
                variant="outline"
                onClick={() => handleFlag('unverified')}
                disabled={flagging}
                className="flex-1 min-w-[120px] text-gray-600 border-gray-600 hover:bg-gray-50 hover:text-gray-700"
                size="sm"
              >
                <span className="mr-1">?</span>
                Unverified
                {video && <span className="ml-1 text-xs opacity-70">({video.unverified_count})</span>}
              </Button>

              <Button
                variant="outline"
                onClick={() => handleFlag('fake')}
                disabled={flagging}
                className="flex-1 min-w-[120px] text-red-600 border-red-600 hover:bg-red-50 hover:text-red-700"
                size="sm"
              >
                <span className="mr-1">✗</span>
                Fake
                {video && <span className="ml-1 text-xs opacity-70">({video.fake_count})</span>}
              </Button>
            </div>
          </div>

          {/* Back Button */}
          <Button onClick={onBack} variant="outline" className="w-full">
            Back to Feed
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
