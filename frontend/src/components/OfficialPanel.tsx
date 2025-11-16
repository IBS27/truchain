import { useState, useEffect, useCallback } from 'react';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { registerVideo, getVideosForOfficial } from '../services/solana';
import { uploadOfficialVideo, getIPFSDownloadUrl } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';

interface OfficialPanelProps {
  officialAccount: any;
}

export function OfficialPanel({ officialAccount }: OfficialPanelProps) {
  const program = useAnchorProgram();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [videos, setVideos] = useState<any[]>([]);

  const loadVideos = useCallback(async () => {
    if (!program) return;
    try {
      const officialVideos = await getVideosForOfficial(program, officialAccount.publicKey);
      setVideos(officialVideos);
    } catch (error) {
      console.error('Failed to load videos:', error);
    }
  }, [program, officialAccount]);

  useEffect(() => {
    loadVideos();
  }, [loadVideos]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !program) return;

    setLoading(true);
    setMessage(null);

    try {
      // Step 1: Upload to backend (IPFS + hash + AI registration)
      setMessage({ type: 'success', text: 'Uploading to IPFS and registering with AI service...' });
      const officialName = new TextDecoder().decode(new Uint8Array(officialAccount.account.name)).replace(/\0/g, '');
      const { hash, cid, aiRegistered } = await uploadOfficialVideo(file, `${officialName} - ${file.name}`);

      if (aiRegistered) {
        setMessage({ type: 'success', text: 'Video uploaded and registered with AI. Registering on blockchain...' });
      } else {
        setMessage({ type: 'success', text: 'Video uploaded (AI registration failed). Registering on blockchain...' });
      }

      // Step 2: Register on-chain
      const tx = await registerVideo(
        program,
        officialAccount.publicKey,
        hash,
        cid
      );

      setMessage({ type: 'success', text: `Video registered! Transaction: ${tx}${aiRegistered ? ' | AI: ✓' : ' | AI: ✗'}` });
      setFile(null);

      // Reload videos
      await loadVideos();
    } catch (error: any) {
      console.error('Upload error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to upload video' });
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
        <h2 className="text-3xl font-bold tracking-tight">Official Panel</h2>
        <p className="text-muted-foreground">
          Upload and manage your official videos
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Official: <span className="font-medium">{new TextDecoder().decode(new Uint8Array(officialAccount.account.name)).replace(/\0/g, '')}</span>
        </p>
      </div>

      {/* Upload New Video */}
      <Card>
        <CardHeader>
          <CardTitle>Upload New Video</CardTitle>
          <CardDescription>
            Upload a video to IPFS and register it on the blockchain
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="video" className="text-sm font-medium block mb-3">Video File</Label>
            <Input
              id="video"
              type="file"
              accept="video/*"
              onChange={handleFileChange}
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
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full sm:w-auto"
          >
            {loading ? 'Uploading...' : 'Upload Video'}
          </Button>
        </CardContent>
      </Card>

      {/* Status Message */}
      {message && (
        <Alert variant={message.type === 'success' ? 'success' : 'destructive'}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* Registered Videos */}
      <Card>
        <CardHeader>
          <CardTitle>Registered Videos</CardTitle>
          <CardDescription>
            View all your videos registered on-chain
          </CardDescription>
        </CardHeader>
        <CardContent>
          {videos.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No videos registered yet.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>IPFS CID</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Votes</TableHead>
                  <TableHead>Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {videos.map((video, idx) => {
                  const cidString = new TextDecoder().decode(new Uint8Array(video.account.ipfsCid)).replace(/\0/g, '');
                  const status = video.account.status;
                  const votes = video.account.votes || [];
                  const authenticVotes = votes.filter((v: any) => v.isAuthentic).length;
                  const fakeVotes = votes.length - authenticVotes;

                  return (
                    <TableRow key={idx}>
                      <TableCell className="font-mono text-xs max-w-xs">
                        <div className="flex items-center gap-2">
                          <a
                            href={getIPFSDownloadUrl(cidString)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline break-all"
                          >
                            {cidString}
                          </a>
                          <Badge variant="outline" className="text-xs opacity-70 shrink-0">
                            On-chain
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          Note: Blockchain records are permanent. Video files may be deleted.
                        </p>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(status)}>
                          {getStatusDisplay(status)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-green-600 font-medium">✓ {authenticVotes}</span>
                        {' / '}
                        <span className="text-red-600 font-medium">✗ {fakeVotes}</span>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(video.account.timestamp.toNumber() * 1000).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
