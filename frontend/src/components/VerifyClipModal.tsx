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
          <Badge variant="success" className="text-sm px-4 py-1.5">
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            VERIFIED - Content & Speaker Match
          </Badge>
        );
      case 'content_only':
        return (
          <Badge variant="warning" className="text-sm px-4 py-1.5">
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            CONTENT MATCH - Speaker Unverified
          </Badge>
        );
      case 'not_verified':
        return (
          <Badge variant="destructive" className="text-sm px-4 py-1.5">
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            NOT VERIFIED - No Match Found
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
    <div className="max-w-5xl mx-auto animate-fade-in">
      <Card className="glass-card border-0">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <CardTitle>AI Verification</CardTitle>
              <CardDescription>Verifying: {video.title}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Video Preview */}
          <div className="relative bg-black rounded-xl overflow-hidden aspect-video ring-1 ring-white/10">
            <video
              src={`http://localhost:3001${video.file_url}`}
              className="w-full h-full object-contain"
              controls
              preload="metadata"
            />
          </div>

          {/* Verify Button */}
          {!result && !error && (
            <div className="text-center py-6">
              <Button
                onClick={handleVerify}
                disabled={verifying}
                size="lg"
                variant="glow"
                className="px-8"
              >
                {verifying ? (
                  <>
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Verifying with AI...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    Verify with AI
                  </>
                )}
              </Button>
              <p className="text-sm text-muted-foreground mt-4">
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
              <div className="text-center py-6 border border-border/50 rounded-xl bg-secondary/30">
                <div className="mb-3">{getVerificationBadge(result.verification_type)}</div>
                <p className="text-sm text-muted-foreground font-mono">
                  ID: {result.verification_id}
                </p>
              </div>

              {/* Clip Information */}
              <div className="border border-border/50 rounded-xl p-5 bg-secondary/20">
                <h4 className="font-semibold mb-4 flex items-center gap-2">
                  <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                  Clip Analysis
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between px-3 py-2 rounded-lg bg-secondary/50">
                    <span className="text-muted-foreground">Duration:</span>
                    <span className="font-semibold">{result.clip_info.duration.toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between px-3 py-2 rounded-lg bg-secondary/50">
                    <span className="text-muted-foreground">Word Count:</span>
                    <span className="font-semibold">{result.clip_info.word_count}</span>
                  </div>
                </div>
                <div className="mt-4">
                  <span className="text-muted-foreground text-sm">Transcript:</span>
                  <p className="mt-2 text-sm italic px-3 py-2 rounded-lg bg-secondary/50">&quot;{result.clip_info.text}&quot;</p>
                </div>
              </div>

              {/* Best Match (if found) */}
              {result.best_match && (
                <div className="border border-primary/30 rounded-xl p-5 bg-primary/5">
                  <h4 className="font-semibold mb-4 flex items-center gap-2 text-primary">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Source Video Match
                  </h4>
                  <div className="space-y-3 text-sm">
                    <div className="px-3 py-2 rounded-lg bg-secondary/30">
                      <span className="text-muted-foreground">Video:</span>
                      <span className="ml-2 font-mono text-xs break-all">{result.best_match.video_name}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="px-3 py-2 rounded-lg bg-secondary/30">
                        <span className="text-muted-foreground">Timestamp:</span>
                        <span className="ml-2 font-semibold">
                          {formatTime(result.best_match.start_time)} - {formatTime(result.best_match.end_time)}
                        </span>
                      </div>
                      <div className="px-3 py-2 rounded-lg bg-secondary/30">
                        <span className="text-muted-foreground">Content Match:</span>
                        <span className="ml-2 font-semibold text-emerald-400">
                          {(result.best_match.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="pt-3 border-t border-border/30">
                      <span className="text-muted-foreground">Matched Text:</span>
                      <p className="mt-2 italic px-3 py-2 rounded-lg bg-secondary/30">&quot;{result.best_match.matched_text}&quot;</p>
                    </div>
                    <div className="pt-3">
                      <Button
                        variant="glow"
                        className="w-full"
                        onClick={() => {
                          const filename = result.best_match!.video_path.split('/').pop() || result.best_match!.video_name;
                          const underscoreIndex = filename.indexOf('_');
                          const cid = underscoreIndex > 0 ? filename.substring(0, underscoreIndex) : filename.replace(/\.[^/.]+$/, '');
                          const videoUrl = cid
                            ? `http://localhost:3001/api/ipfs/download/${cid}#t=${Math.floor(result.best_match!.start_time)}`
                            : `http://localhost:3001/official-videos/${encodeURIComponent(filename)}#t=${Math.floor(result.best_match!.start_time)}`;
                          window.open(videoUrl, '_blank');
                        }}
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
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
                <div className={`border rounded-xl p-5 ${result.speaker_verification.verified ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-amber-500/30 bg-amber-500/5'}`}>
                  <h4 className={`font-semibold mb-4 flex items-center gap-2 ${result.speaker_verification.verified ? 'text-emerald-400' : 'text-amber-400'}`}>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    Speaker Verification
                  </h4>
                  <div className="space-y-3 text-sm">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="px-3 py-2 rounded-lg bg-secondary/30">
                        <span className="text-muted-foreground">Status:</span>
                        <span className={`ml-2 font-semibold ${result.speaker_verification.verified ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {result.speaker_verification.message}
                        </span>
                      </div>
                      <div className="px-3 py-2 rounded-lg bg-secondary/30">
                        <span className="text-muted-foreground">Similarity:</span>
                        <span className="ml-2 font-semibold">
                          {(result.speaker_verification.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="px-3 py-2 rounded-lg bg-secondary/30">
                      <span className="text-muted-foreground">Threshold:</span>
                      <span className="ml-2">{(result.speaker_verification.threshold * 100)}%</span>
                    </div>
                    {!result.speaker_verification.verified && (
                      <Alert variant="warning" className="mt-3">
                        <AlertDescription className="text-xs">
                          Voice does not match the original speaker. This could indicate a deepfake or voice clone.
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
          <div className="border-t border-border/50 pt-6">
            <h4 className="font-semibold text-base mb-4 flex items-center gap-2">
              <svg className="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Community Feedback
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="outline"
                onClick={() => handleFlag('verified')}
                disabled={flagging}
                className="border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/50"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                Verified
                <span className="ml-1 text-xs opacity-70">({video.verified_count})</span>
              </Button>

              <Button
                variant="outline"
                onClick={() => handleFlag('misleading')}
                disabled={flagging}
                className="border-amber-500/30 text-amber-400 hover:bg-amber-500/10 hover:border-amber-500/50"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Misleading
                <span className="ml-1 text-xs opacity-70">({video.misleading_count})</span>
              </Button>

              <Button
                variant="outline"
                onClick={() => handleFlag('unverified')}
                disabled={flagging}
                className="border-slate-500/30 text-slate-400 hover:bg-slate-500/10 hover:border-slate-500/50"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Unverified
                <span className="ml-1 text-xs opacity-70">({video.unverified_count})</span>
              </Button>

              <Button
                variant="outline"
                onClick={() => handleFlag('fake')}
                disabled={flagging}
                className="border-red-500/30 text-red-400 hover:bg-red-500/10 hover:border-red-500/50"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Fake
                <span className="ml-1 text-xs opacity-70">({video.fake_count})</span>
              </Button>
            </div>
          </div>

          {/* Back Button */}
          <Button onClick={onBack} variant="outline" className="w-full">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Feed
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
