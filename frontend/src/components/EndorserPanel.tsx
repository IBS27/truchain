import { useState, useEffect, useCallback } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { getVideosForOfficial, endorseVideo } from '../services/solana';
import { uploadVideo, getIPFSDownloadUrl } from '../services/api';

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
        const unvotedVideos = videos.filter(video => {
          const hasVoted = video.account.votes.some((v: any) =>
            v.endorser.equals(publicKey)
          );
          return !hasVoted;
        });

        allVideos.push(...unvotedVideos.map(v => ({
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
        allVideos.push(...videos.map(v => ({
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

  return (
    <div style={{ padding: '20px', maxWidth: '1200px' }}>
      <h2>Endorser Panel</h2>
      <p>You are an endorser for {assignedOfficials.length} official(s)</p>

      {/* Section 1: Pending Videos */}
      <div style={{ marginBottom: '40px' }}>
        <h3>Pending Videos (Need Your Vote)</h3>
        {pendingVideos.length === 0 ? (
          <p>No pending videos to vote on.</p>
        ) : (
          <div>
            {pendingVideos.map((video, idx) => {
              const cidString = new TextDecoder().decode(new Uint8Array(video.account.ipfsCid)).replace(/\0/g, '');
              const votes = video.account.votes || [];
              const authenticVotes = votes.filter((v: any) => v.isAuthentic).length;
              const fakeVotes = votes.length - authenticVotes;

              return (
                <div
                  key={idx}
                  style={{
                    border: '1px solid #ddd',
                    padding: '15px',
                    marginBottom: '15px',
                    borderRadius: '8px',
                  }}
                >
                  <h4>Video from {video.officialName}</h4>
                  <p>
                    <strong>IPFS CID:</strong>{' '}
                    <a href={getIPFSDownloadUrl(cidString)} target="_blank" rel="noopener noreferrer">
                      {cidString}
                    </a>
                  </p>
                  <p>
                    <strong>Status:</strong> {getStatusDisplay(video.account.status)}
                  </p>
                  <p>
                    <strong>Current Votes:</strong> ✓ {authenticVotes} / ✗ {fakeVotes}
                  </p>
                  <div>
                    <button
                      onClick={() => handleVote(video, true)}
                      disabled={loading}
                      style={{
                        padding: '8px 16px',
                        marginRight: '10px',
                        backgroundColor: loading ? '#ccc' : '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Vote Authentic
                    </button>
                    <button
                      onClick={() => handleVote(video, false)}
                      disabled={loading}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: loading ? '#ccc' : '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Vote Fake
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Section 2: Verify Uploaded File */}
      <div style={{ marginBottom: '40px' }}>
        <h3>Verify Uploaded File</h3>
        <p>Upload a video file to check if it matches any registered videos</p>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="file"
            accept="video/*"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setFile(e.target.files[0]);
                setMatchResult(null);
              }
            }}
            disabled={loading}
          />
        </div>
        <button
          onClick={handleFileVerify}
          disabled={!file || loading}
          style={{
            padding: '10px 20px',
            backgroundColor: !file || loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: !file || loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Verifying...' : 'Verify File'}
        </button>

        {matchResult && (
          <div
            style={{
              marginTop: '20px',
              border: '1px solid #28a745',
              padding: '15px',
              borderRadius: '8px',
              backgroundColor: '#d4edda',
            }}
          >
            <h4>Match Found!</h4>
            <p><strong>Official:</strong> {matchResult.officialName}</p>
            <p><strong>Status:</strong> {getStatusDisplay(matchResult.account.status)}</p>
            <div>
              <button
                onClick={() => handleVote(matchResult, true)}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  marginRight: '10px',
                  backgroundColor: loading ? '#ccc' : '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                Vote Authentic
              </button>
              <button
                onClick={() => handleVote(matchResult, false)}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  backgroundColor: loading ? '#ccc' : '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                Vote Fake
              </button>
            </div>
          </div>
        )}
      </div>

      {message && (
        <div
          style={{
            padding: '10px',
            marginBottom: '20px',
            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
            color: message.type === 'success' ? '#155724' : '#721c24',
            borderRadius: '4px',
          }}
        >
          {message.text}
        </div>
      )}
    </div>
  );
}
