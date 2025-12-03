import { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';
import { Button } from './ui/button';
import { verificationApi, socialApi } from '../services/api';
import type { AIVerificationResult, SocialVideo } from '../services/api';

interface MobileVerifySheetProps {
  video: SocialVideo;
  isOpen: boolean;
  onClose: () => void;
  onVideoUpdate: (video: SocialVideo) => void;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export function MobileVerifySheet({ video, isOpen, onClose, onVideoUpdate }: MobileVerifySheetProps) {
  const [stage, setStage] = useState<'initial' | 'verifying' | 'results' | 'voting'>('initial');
  const [result, setResult] = useState<AIVerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [votingFor, setVotingFor] = useState<string | null>(null);

  const handleVerify = async () => {
    setStage('verifying');
    setError(null);

    try {
      const videoResponse = await fetch(`${BACKEND_URL}${video.file_url}`);
      const videoBlob = await videoResponse.blob();
      const videoFile = new File([videoBlob], video.title || 'clip.mp4', { type: 'video/mp4' });

      const verificationResult = await verificationApi.verifyClip(videoFile);
      setResult(verificationResult);
      setStage('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
      setStage('initial');
    }
  };

  const handleVote = async (flagType: 'verified' | 'misleading' | 'unverified' | 'fake') => {
    setVotingFor(flagType);
    try {
      const response = await socialApi.flagVideo(video.id, flagType);
      onVideoUpdate(response.video);
      onClose();
    } catch (err) {
      setError('Failed to submit vote');
    } finally {
      setVotingFor(null);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getResultColor = () => {
    if (!result) return 'border-border/50 bg-secondary/30';
    switch (result.verification_type) {
      case 'full': return 'border-emerald-500/30 bg-emerald-500/10';
      case 'content_only': return 'border-amber-500/30 bg-amber-500/10';
      default: return 'border-red-500/30 bg-red-500/10';
    }
  };

  const getResultIcon = () => {
    if (!result) return null;
    switch (result.verification_type) {
      case 'full':
        return (
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center ring-2 ring-emerald-500/30">
            <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'content_only':
        return (
          <div className="w-16 h-16 rounded-full bg-amber-500/20 flex items-center justify-center ring-2 ring-amber-500/30">
            <svg className="w-8 h-8 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center ring-2 ring-red-500/30">
            <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
    }
  };

  const getResultTitle = () => {
    if (!result) return '';
    switch (result.verification_type) {
      case 'full': return 'Verified Authentic';
      case 'content_only': return 'Content Match Only';
      default: return 'Not Verified';
    }
  };

  const getResultTitleColor = () => {
    if (!result) return '';
    switch (result.verification_type) {
      case 'full': return 'text-emerald-400';
      case 'content_only': return 'text-amber-400';
      default: return 'text-red-400';
    }
  };

  const getResultDescription = () => {
    if (!result) return '';
    switch (result.verification_type) {
      case 'full': return 'Content and speaker voice match an official source.';
      case 'content_only': return 'Words match but voice differs. Possible deepfake.';
      default: return 'No matching official source found.';
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="bottom" className="max-h-[85vh] overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="text-center">
            {stage === 'initial' && 'Verify This Clip'}
            {stage === 'verifying' && 'Analyzing...'}
            {stage === 'results' && 'Verification Result'}
            {stage === 'voting' && 'Submit Your Vote'}
          </SheetTitle>
        </SheetHeader>

        <div className="px-4 pb-8 space-y-6">
          {/* Initial State */}
          {stage === 'initial' && (
            <>
              <p className="text-center text-muted-foreground text-sm">
                Our AI will analyze this clip against official government video sources to verify authenticity.
              </p>

              <Button
                onClick={handleVerify}
                variant="glow"
                className="w-full h-14 text-lg"
              >
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Start AI Verification
              </Button>

              {error && (
                <p className="text-center text-red-400 text-sm">{error}</p>
              )}
            </>
          )}

          {/* Verifying State */}
          {stage === 'verifying' && (
            <div className="py-8 flex flex-col items-center gap-4">
              <div className="relative w-20 h-20">
                <div className="w-20 h-20 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              </div>
              <div className="text-center">
                <p className="font-medium">Analyzing video...</p>
                <p className="text-sm text-muted-foreground mt-1">Matching speech and verifying speaker</p>
              </div>
            </div>
          )}

          {/* Results State */}
          {stage === 'results' && result && (
            <>
              {/* Result Card */}
              <div className={`rounded-2xl border-2 p-6 ${getResultColor()}`}>
                <div className="flex flex-col items-center text-center gap-3">
                  {getResultIcon()}
                  <h3 className={`text-xl font-bold ${getResultTitleColor()}`}>{getResultTitle()}</h3>
                  <p className="text-sm text-muted-foreground">{getResultDescription()}</p>
                </div>
              </div>

              {/* Match Details */}
              {result.best_match && (
                <div className="bg-secondary/30 rounded-xl p-4 space-y-3 border border-border/50">
                  <h4 className="font-semibold text-sm flex items-center gap-2">
                    <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Source Match
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="px-3 py-2 rounded-lg bg-secondary/50">
                      <span className="text-muted-foreground">Timestamp:</span>
                      <span className="ml-1 font-medium">
                        {formatTime(result.best_match.start_time)} - {formatTime(result.best_match.end_time)}
                      </span>
                    </div>
                    <div className="px-3 py-2 rounded-lg bg-secondary/50">
                      <span className="text-muted-foreground">Match:</span>
                      <span className="ml-1 font-semibold text-emerald-400">
                        {(result.best_match.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    className="w-full mt-2"
                    onClick={() => {
                      const filename = result.best_match!.video_path.split('/').pop() || result.best_match!.video_name;
                      const underscoreIndex = filename.indexOf('_');
                      const cid = underscoreIndex > 0 ? filename.substring(0, underscoreIndex) : filename.replace(/\.[^/.]+$/, '');
                      const videoUrl = cid
                        ? `${BACKEND_URL}/api/ipfs/download/${cid}#t=${Math.floor(result.best_match!.start_time)}`
                        : `${BACKEND_URL}/official-videos/${encodeURIComponent(filename)}#t=${Math.floor(result.best_match!.start_time)}`;
                      window.open(videoUrl, '_blank');
                    }}
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    View Official Source
                  </Button>
                </div>
              )}

              {/* Speaker Verification */}
              {result.speaker_verification && (
                <div className={`rounded-xl p-4 border ${result.speaker_verification.verified ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-amber-500/30 bg-amber-500/10'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-sm flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                        </svg>
                        Voice Match
                      </h4>
                      <p className="text-xs text-muted-foreground">{result.speaker_verification.message}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-lg font-bold ${result.speaker_verification.verified ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {(result.speaker_verification.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Vote Section */}
              <div className="pt-4 border-t border-border/50">
                <h4 className="font-semibold mb-3 text-center">Cast Your Vote</h4>
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    onClick={() => handleVote('verified')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-xs">Verified ({video.verified_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('misleading')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <span className="text-xs">Misleading ({video.misleading_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('unverified')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-slate-500/30 text-slate-400 hover:bg-slate-500/10"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-xs">Unsure ({video.unverified_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('fake')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-red-500/30 text-red-400 hover:bg-red-500/10"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    <span className="text-xs">Fake ({video.fake_count})</span>
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
