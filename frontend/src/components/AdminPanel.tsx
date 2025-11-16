import { useState, useEffect } from 'react';
import { PublicKey } from '@solana/web3.js';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { registerOfficial, getAllOfficials } from '../services/solana';

export function AdminPanel() {
  const program = useAnchorProgram();
  const [officialId, setOfficialId] = useState('');
  const [name, setName] = useState('');
  const [authority, setAuthority] = useState('');
  const [endorser1, setEndorser1] = useState('');
  const [endorser2, setEndorser2] = useState('');
  const [endorser3, setEndorser3] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [officials, setOfficials] = useState<any[]>([]);

  const loadOfficials = async () => {
    if (!program) return;
    try {
      const allOfficials = await getAllOfficials(program);
      setOfficials(allOfficials);
    } catch (error) {
      console.error('Failed to load officials:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!program) {
      setMessage({ type: 'error', text: 'Program not initialized' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // Validate inputs
      const authorityPubkey = new PublicKey(authority);
      const endorser1Pubkey = new PublicKey(endorser1);
      const endorser2Pubkey = new PublicKey(endorser2);
      const endorser3Pubkey = new PublicKey(endorser3);

      // Check for duplicates
      const endorsers = [endorser1, endorser2, endorser3];
      if (new Set(endorsers).size !== endorsers.length) {
        throw new Error('Endorsers must be unique');
      }

      const tx = await registerOfficial(
        program,
        parseInt(officialId, 10),
        name,
        authorityPubkey,
        [endorser1Pubkey, endorser2Pubkey, endorser3Pubkey]
      );

      setMessage({ type: 'success', text: `Official registered! Transaction: ${tx}` });

      // Reset form
      setOfficialId('');
      setName('');
      setAuthority('');
      setEndorser1('');
      setEndorser2('');
      setEndorser3('');

      // Reload officials list
      await loadOfficials();
    } catch (error: any) {
      console.error('Registration error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to register official' });
    } finally {
      setLoading(false);
    }
  };

  // Load officials on mount
  useEffect(() => {
    loadOfficials();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <h2>Admin Panel - Register Official</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: '40px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label>
            Official ID:
            <input
              type="number"
              value={officialId}
              onChange={(e) => setOfficialId(e.target.value)}
              required
              style={{ marginLeft: '10px', padding: '5px', width: '200px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Name (max 32 bytes):
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={32}
              required
              style={{ marginLeft: '10px', padding: '5px', width: '300px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Authority Wallet:
            <input
              type="text"
              value={authority}
              onChange={(e) => setAuthority(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Endorser 1:
            <input
              type="text"
              value={endorser1}
              onChange={(e) => setEndorser1(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Endorser 2:
            <input
              type="text"
              value={endorser2}
              onChange={(e) => setEndorser2(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>
            Endorser 3:
            <input
              type="text"
              value={endorser3}
              onChange={(e) => setEndorser3(e.target.value)}
              required
              placeholder="Public key"
              style={{ marginLeft: '10px', padding: '5px', width: '400px' }}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Registering...' : 'Register Official'}
        </button>
      </form>

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

      <h3>Registered Officials</h3>
      {officials.length === 0 ? (
        <p>No officials registered yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>ID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Name</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Authority</th>
            </tr>
          </thead>
          <tbody>
            {officials.map((official, idx) => (
              <tr key={idx}>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {official.account.officialId.toString()}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {new TextDecoder().decode(new Uint8Array(official.account.name)).replace(/\0/g, '')}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '12px' }}>
                  {official.account.authority.toString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
