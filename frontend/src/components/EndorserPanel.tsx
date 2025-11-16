import { useState, useEffect, useCallback } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { getVideosForOfficial, endorseVideo } from '../services/solana';
import { uploadVideo, getIPFSDownloadUrl } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';

interface EndorserPanelProps {
  assignedOfficials: any[];
}

export function EndorserPanel({ assignedOfficials }: EndorserPanelProps) {
  const program = useAnchorProgram();
  const { publicKey } = useWallet();
  const [pendingVideos, setPendingVideos] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [matchResult, setMatchResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadPendingVideos = useCallback(async () => {
    if (!program || !publicKey) return;

    try {
      const allVideos = [];
      for (const official of assignedOfficials) {
        const videos = await getVideosForOfficial(program, official.publicKey);

        // Filter videos where this endorser hasn't voted yet
        const unvotedVideos = videos.filter((video: any) => {
          const hasVoted = video.account.votes.some((v: any) =>
            v.endorser.equals(publicKey)
          );
          return !hasVoted;
        });

        allVideos.push(...unvotedVideos.map((v: any) => ({
          ...v,
          officialName: new TextDecoder().decode(new Uint8Array(official.account.name)).replace(/\0/g, ''),
          officialPubkey: official.publicKey,
        })));
      }

      setPendingVideos(allVideos);
    } catch (error) {
      console.error('Failed to load pending videos:', error);
    }
  }, [program, publicKey, assignedOfficials]);

  useEffect(() => {
    loadPendingVideos();
  }, [loadPendingVideos]);

  const handleVote = async (video: any, isAuthentic: boolean) => {
    if (!program) return;

    setLoading(true);
    setMessage(null);

    try {
      const tx = await endorseVideo(
        program,
        video.officialPubkey,
        Array.from(video.account.videoHash),
        isAuthentic
      );

      setMessage({
        type: 'success',
        text: `Vote submitted! Transaction: ${tx}`,
      });

      // Reload pending videos
      await loadPendingVideos();
    } catch (error: any) {
      console.error('Vote error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to submit vote' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileVerify = async () => {
    if (!file || !program) return;

    setLoading(true);
    setMessage(null);
    setMatchResult(null);

    try {
      // Upload file to get hash
      const { hash } = await uploadVideo(file);

      // Search for matching video on-chain
      const allVideos = [];
      for (const official of assignedOfficials) {
        const videos = await getVideosForOfficial(program, official.publicKey);
        allVideos.push(...videos.map((v: any) => ({
          ...v,
          officialName: new TextDecoder().decode(new Uint8Array(official.account.name)).replace(/\0/g, ''),
          officialPubkey: official.publicKey,
        })));
      }

      const hashString = hash.join(',');
      const match = allVideos.find(v =>
        Array.from(v.account.videoHash).join(',') === hashString
      );

      if (match) {
        setMatchResult(match);
        setMessage({ type: 'success', text: 'Match found! You can vote below.' });
      } else {
        setMessage({ type: 'error', text: 'No matching video found on-chain.' });
      }
    } catch (error: any) {
      console.error('Verify error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to verify file' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: any) => {
    if (status.unverified !== undefined) return 'Unverified';
    if (status.authentic !== undefined) return 'Authentic';
    if (status.disputed !== undefined) return 'Disputed';
    return 'Unknown';
  };

  const getStatusVariant = (status: any): 'warning' | 'success' | 'destructive' | 'secondary' => {
    if (status.unverified !== undefined) return 'warning';
    if (status.authentic !== undefined) return 'success';
    if (status.disputed !== undefined) return 'destructive';
    return 'secondary';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Endorser Panel</h2>
        <p className="text-muted-foreground">
          You are an endorser for {assignedOfficials.length} official(s)
        </p>
      </div>

      {/* Pending Videos Section */}
      <Card>
        <CardHeader>
          <CardTitle>Pending Videos</CardTitle>
          <CardDescription>
            Videos waiting for your vote
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pendingVideos.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No pending videos to vote on.
            </p>
          ) : (
            <div className="space-y-2">
              {pendingVideos.map((video, idx) => {
                const cidString = new TextDecoder().decode(new Uint8Array(video.account.ipfsCid)).replace(/\0/g, '');
                const votes = video.account.votes || [];
                const authenticVotes = votes.filter((v: any) => v.isAuthentic).length;
                const fakeVotes = votes.length - authenticVotes;

                return (
                  <div key={idx} className="border rounded-lg p-3 bg-card hover:bg-accent/5 transition-colors">
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <span className="font-medium text-sm truncate">{video.officialName}</span>
                        <Badge variant={getStatusVariant(video.account.status)} className="text-xs shrink-0">
                          {getStatusDisplay(video.account.status)}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-sm shrink-0">
                        <span className="text-green-600 font-medium">✓ {authenticVotes}</span>
                        <span className="text-red-600 font-medium">✗ {fakeVotes}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-muted-foreground shrink-0">IPFS:</span>
                      <a
                        href={getIPFSDownloadUrl(cidString)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-mono text-blue-600 hover:underline truncate"
                        title={cidString}
                      >
                        {cidString}
                      </a>
                    </div>
                  </div>
                );
              })}
              <p className="text-xs text-muted-foreground italic pt-2 pb-1">
                To vote on these videos, upload them using the "Verify Uploaded File" section below.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Verify Uploaded File Section */}
      <Card>
        <CardHeader>
          <CardTitle>Verify Uploaded File</CardTitle>
          <CardDescription>
            Upload a video file to check if it matches any registered videos
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="verifyFile" className="text-sm font-medium block mb-3">Video File</Label>
            <Input
              id="verifyFile"
              type="file"
              accept="video/*"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0]);
                  setMatchResult(null);
                }
              }}
              disabled={loading}
              className="cursor-pointer h-10 py-0 flex items-center file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 file:cursor-pointer"
            />
            {file && (
              <p className="text-sm text-muted-foreground mt-3">
                Selected: <span className="font-medium">{file.name}</span> ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
          </div>
          <Button
            onClick={handleFileVerify}
            disabled={!file || loading}
            className="w-full sm:w-auto"
          >
            {loading ? 'Verifying...' : 'Verify File'}
          </Button>

          {matchResult && (
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="text-lg text-green-900">Match Found!</CardTitle>
                <CardDescription>
                  Official: {matchResult.officialName}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Badge variant={getStatusVariant(matchResult.account.status)}>
                    {getStatusDisplay(matchResult.account.status)}
                  </Badge>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleVote(matchResult, true)}
                    disabled={loading}
                    variant="default"
                    className="flex-1"
                  >
                    Vote Authentic
                  </Button>
                  <Button
                    onClick={() => handleVote(matchResult, false)}
                    disabled={loading}
                    variant="destructive"
                    className="flex-1"
                  >
                    Vote Fake
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Status Message */}
      {message && (
        <Alert variant={message.type === 'success' ? 'success' : 'destructive'}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}
