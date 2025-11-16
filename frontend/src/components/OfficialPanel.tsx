import { useState, useEffect, useCallback } from 'react';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { registerVideo, getVideosForOfficial } from '../services/solana';
import { uploadVideo, getIPFSDownloadUrl } from '../services/api';

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
      // Step 1: Upload to backend (IPFS + hash)
      setMessage({ type: 'success', text: 'Uploading to IPFS...' });
      const { hash, cid } = await uploadVideo(file);

      // Step 2: Register on-chain
      setMessage({ type: 'success', text: 'Registering on blockchain...' });
      const tx = await registerVideo(
        program,
        officialAccount.publicKey,
        hash,
        cid
      );

      setMessage({ type: 'success', text: `Video registered! Transaction: ${tx}` });
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

  const getStatusColor = (status: any) => {
    if (status.unverified !== undefined) return '#ffc107';
    if (status.authentic !== undefined) return '#28a745';
    if (status.disputed !== undefined) return '#dc3545';
    return '#6c757d';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1000px' }}>
      <h2>Official Panel - Upload Videos</h2>
      <p>Official: {new TextDecoder().decode(new Uint8Array(officialAccount.account.name)).replace(/\0/g, '')}</p>

      <div style={{ marginBottom: '40px' }}>
        <h3>Upload New Video</h3>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            disabled={loading}
          />
        </div>
        <button
          onClick={handleUpload}
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
          {loading ? 'Uploading...' : 'Upload Video'}
        </button>
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

      <h3>Registered Videos</h3>
      {videos.length === 0 ? (
        <p>No videos registered yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>IPFS CID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Status</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Votes</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {videos.map((video, idx) => {
              const cidString = new TextDecoder().decode(new Uint8Array(video.account.ipfsCid)).replace(/\0/g, '');
              const status = video.account.status;
              const votes = video.account.votes || [];
              const authenticVotes = votes.filter((v: any) => v.isAuthentic).length;
              const fakeVotes = votes.length - authenticVotes;

              return (
                <tr key={idx}>
                  <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '12px' }}>
                    <a href={getIPFSDownloadUrl(cidString)} target="_blank" rel="noopener noreferrer">
                      {cidString}
                    </a>
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: getStatusColor(status),
                        color: 'white',
                        fontSize: '12px',
                      }}
                    >
                      {getStatusDisplay(status)}
                    </span>
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    ✓ {authenticVotes} / ✗ {fakeVotes}
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    {new Date(video.account.timestamp.toNumber() * 1000).toLocaleString()}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
