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
    if (!result) return 'bg-gray-100';
    switch (result.verification_type) {
      case 'full': return 'bg-green-50 border-green-200';
      case 'content_only': return 'bg-orange-50 border-orange-200';
      default: return 'bg-red-50 border-red-200';
    }
  };

  const getResultIcon = () => {
    if (!result) return null;
    switch (result.verification_type) {
      case 'full': return <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center text-white text-3xl">✓</div>;
      case 'content_only': return <div className="w-16 h-16 rounded-full bg-orange-500 flex items-center justify-center text-white text-3xl">⚠</div>;
      default: return <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center text-white text-3xl">✗</div>;
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
                className="w-full h-14 text-lg bg-blue-600 hover:bg-blue-700"
              >
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Start AI Verification
              </Button>

              {error && (
                <p className="text-center text-red-500 text-sm">{error}</p>
              )}
            </>
          )}

          {/* Verifying State */}
          {stage === 'verifying' && (
            <div className="py-8 flex flex-col items-center gap-4">
              <div className="relative w-20 h-20">
                <svg className="w-20 h-20 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
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
                  <h3 className="text-xl font-bold">{getResultTitle()}</h3>
                  <p className="text-sm text-muted-foreground">{getResultDescription()}</p>
                </div>
              </div>

              {/* Match Details */}
              {result.best_match && (
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <h4 className="font-semibold text-sm">Source Match</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Timestamp:</span>
                      <span className="ml-1 font-medium">
                        {formatTime(result.best_match.start_time)} - {formatTime(result.best_match.end_time)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Match:</span>
                      <span className="ml-1 font-medium text-green-600">
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
                    View Official Source
                  </Button>
                </div>
              )}

              {/* Speaker Verification */}
              {result.speaker_verification && (
                <div className={`rounded-xl p-4 ${result.speaker_verification.verified ? 'bg-green-50' : 'bg-orange-50'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-sm">Voice Match</h4>
                      <p className="text-xs text-muted-foreground">{result.speaker_verification.message}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-lg font-bold ${result.speaker_verification.verified ? 'text-green-600' : 'text-orange-600'}`}>
                        {(result.speaker_verification.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Vote Section */}
              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-3 text-center">Cast Your Vote</h4>
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    onClick={() => handleVote('verified')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-green-300 text-green-700 hover:bg-green-50"
                  >
                    <span className="text-lg">✓</span>
                    <span className="text-xs">Verified ({video.verified_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('misleading')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-orange-300 text-orange-700 hover:bg-orange-50"
                  >
                    <span className="text-lg">⚠</span>
                    <span className="text-xs">Misleading ({video.misleading_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('unverified')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    <span className="text-lg">?</span>
                    <span className="text-xs">Unsure ({video.unverified_count})</span>
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleVote('fake')}
                    disabled={votingFor !== null}
                    className="h-14 flex-col gap-1 border-red-300 text-red-700 hover:bg-red-50"
                  >
                    <span className="text-lg">✗</span>
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
