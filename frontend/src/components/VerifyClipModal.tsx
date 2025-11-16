import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { verificationApi, socialApi } from '../services/api';
import type { AIVerificationResult, SocialVideo } from '../services/api';

interface VerifyClipModalProps {
  video: SocialVideo;
  onBack: () => void;
}

export function VerifyClipModal({ video: initialVideo, onBack }: VerifyClipModalProps) {
  const [verifying, setVerifying] = useState(false);
  const [flagging, setFlagging] = useState(false);
  const [result, setResult] = useState<AIVerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [video, setVideo] = useState<SocialVideo>(initialVideo);

  const handleVerify = async () => {
    setVerifying(true);
    setError(null);
    setResult(null);

    try {
      // Fetch the video file
      const videoResponse = await fetch(`http://localhost:3001${video.file_url}`);
      const videoBlob = await videoResponse.blob();
      const videoFile = new File([videoBlob], video.title || 'clip.mp4', { type: 'video/mp4' });

      // Verify with AI service
      const verificationResult = await verificationApi.verifyClip(videoFile);
      setResult(verificationResult);
    } catch (err) {
      console.error('Verification error:', err);
      setError(err instanceof Error ? err.message : 'Failed to verify clip');
    } finally {
      setVerifying(false);
    }
  };

  const handleFlag = async (flagType: 'verified' | 'misleading' | 'unverified' | 'fake') => {
    setFlagging(true);
    try {
      const response = await socialApi.flagVideo(video.id, flagType);
      // Update local state with new video data including updated counts
      setVideo(response.video);
    } catch (error) {
      console.error('Failed to flag video:', error);
      alert('Failed to flag video. Please try again.');
    } finally {
      setFlagging(false);
    }
  };

  const getVerificationBadge = (verificationType: string) => {
    switch (verificationType) {
      case 'full':
        return (
          <Badge className="bg-green-600 text-white">
            ✓ VERIFIED - Content & Speaker Match
          </Badge>
        );
      case 'content_only':
        return (
          <Badge className="bg-orange-600 text-white">
            ⚠ CONTENT MATCH - Speaker Unverified (Possible Deepfake)
          </Badge>
        );
      case 'not_verified':
        return (
          <Badge className="bg-red-600 text-white">
            ✗ NOT VERIFIED - No Match Found
          </Badge>
        );
      default:
        return null;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>AI Verification</CardTitle>
          <CardDescription>Verifying: {video.title}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Video Preview */}
          <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
            <video
              src={`http://localhost:3001${video.file_url}`}
              className="w-full h-full object-contain"
              controls
              preload="metadata"
            />
          </div>

          {/* Verify Button */}
          {!result && !error && (
            <div className="text-center py-4">
              <Button
                onClick={handleVerify}
                disabled={verifying}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8"
              >
                {verifying ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Verifying with AI...
                  </>
                ) : (
                  <>
                    🔍 Verify with AI
                  </>
                )}
              </Button>
              <p className="text-sm text-muted-foreground mt-3">
                This will analyze the clip using AI to match it against official videos
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>
                <strong>Verification Failed:</strong> {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Verification Results */}
          {result && (
            <div className="space-y-6">
              {/* Verification Status */}
              <div className="text-center py-4 border rounded-lg bg-muted/30">
                <div className="mb-3">{getVerificationBadge(result.verification_type)}</div>
                <p className="text-sm text-muted-foreground">
                  Verification ID: {result.verification_id}
                </p>
              </div>

              {/* Clip Information */}
              <div className="border rounded-lg p-4 bg-muted/20">
                <h4 className="font-semibold mb-3">Clip Analysis</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-muted-foreground">Duration:</span>
                    <span className="ml-2 font-medium">{result.clip_info.duration.toFixed(1)}s</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Word Count:</span>
                    <span className="ml-2 font-medium">{result.clip_info.word_count}</span>
                  </div>
                </div>
                <div className="mt-3">
                  <span className="text-muted-foreground text-sm">Transcript:</span>
                  <p className="mt-1 text-sm italic">&quot;{result.clip_info.text}&quot;</p>
                </div>
              </div>

              {/* Best Match (if found) */}
              {result.best_match && (
                <div className="border rounded-lg p-4 bg-blue-50 dark:bg-blue-950/20">
                  <h4 className="font-semibold mb-3">Source Video Match</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Video:</span>
                      <span className="ml-2 font-mono text-xs break-all">{result.best_match.video_name}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <span className="text-muted-foreground">Timestamp:</span>
                        <span className="ml-2 font-medium">
                          {formatTime(result.best_match.start_time)} - {formatTime(result.best_match.end_time)}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Content Match:</span>
                        <span className="ml-2 font-medium text-green-600">
                          {(result.best_match.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t">
                      <span className="text-muted-foreground">Matched Text:</span>
                      <p className="mt-1 italic">&quot;{result.best_match.matched_text}&quot;</p>
                    </div>
                    <div className="mt-3 pt-3 border-t">
                      <Button
                        variant="default"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                        onClick={() => {
                          // Extract the filename from video_path
                          const filename = result.best_match!.video_path.split('/').pop() || result.best_match!.video_name;

                          // Extract CID from filename (format: "Qm...CID..._originalname.mp4")
                          // CIDv0 uses base58 encoding (alphanumeric except 0, O, I, l)
                          // The CID is everything before the first underscore or the entire name if no underscore
                          const underscoreIndex = filename.indexOf('_');
                          const cid = underscoreIndex > 0 ? filename.substring(0, underscoreIndex) : filename.replace(/\.[^/.]+$/, '');

                          // Use IPFS download endpoint if CID is found, otherwise fallback to direct file
                          const videoUrl = cid
                            ? `http://localhost:3001/api/ipfs/download/${cid}#t=${Math.floor(result.best_match!.start_time)}`
                            : `http://localhost:3001/official-videos/${encodeURIComponent(filename)}#t=${Math.floor(result.best_match!.start_time)}`;

                          window.open(videoUrl, '_blank');
                        }}
                      >
                        View Official Source Video
                      </Button>
                      <p className="text-xs text-muted-foreground mt-2 text-center">
                        Opens the full official video at the matched timestamp
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Speaker Verification */}
              {result.speaker_verification && (
                <div className="border rounded-lg p-4 bg-purple-50 dark:bg-purple-950/20">
                  <h4 className="font-semibold mb-3">Speaker Verification</h4>
                  <div className="space-y-2 text-sm">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <span className="text-muted-foreground">Status:</span>
                        <span className={`ml-2 font-medium ${result.speaker_verification.verified ? 'text-green-600' : 'text-orange-600'}`}>
                          {result.speaker_verification.message}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Similarity:</span>
                        <span className="ml-2 font-medium">
                          {(result.speaker_verification.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Threshold:</span>
                      <span className="ml-2">{(result.speaker_verification.threshold * 100)}%</span>
                    </div>
                    {!result.speaker_verification.verified && (
                      <Alert variant="warning" className="mt-3">
                        <AlertDescription className="text-xs">
                          ⚠ Voice does not match the original speaker. This could indicate a deepfake or voice clone.
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </div>
              )}

              {/* No Match Found */}
              {result.verification_type === 'not_verified' && (
                <Alert variant="destructive">
                  <AlertDescription>
                    This clip could not be matched to any official video in our database.
                    It may be from an unregistered source or potentially fabricated.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}

          {/* Voting Section */}
          <div className="border-t pt-6">
            <h4 className="font-semibold text-base mb-3">Community Feedback</h4>
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
                <span className="ml-1 text-xs opacity-70">({video.verified_count})</span>
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
                <span className="ml-1 text-xs opacity-70">({video.misleading_count})</span>
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
                <span className="ml-1 text-xs opacity-70">({video.unverified_count})</span>
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
                <span className="ml-1 text-xs opacity-70">({video.fake_count})</span>
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
