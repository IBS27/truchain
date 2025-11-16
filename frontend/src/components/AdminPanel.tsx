import { useState, useEffect, useCallback } from 'react';
import { PublicKey } from '@solana/web3.js';
import { useAnchorProgram } from '../hooks/useAnchorProgram';
import { registerOfficial, getAllOfficials } from '../services/solana';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

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

  const loadOfficials = useCallback(async () => {
    if (!program) return;
    try {
      const allOfficials = await getAllOfficials(program);
      setOfficials(allOfficials);
    } catch (error) {
      console.error('Failed to load officials:', error);
    }
  }, [program]);

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

  // Load officials when program is ready
  useEffect(() => {
    loadOfficials();
  }, [loadOfficials]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Admin Panel</h2>
        <p className="text-muted-foreground">
          Register new officials and manage endorsers
        </p>
      </div>

      {/* Register Official Form */}
      <Card>
        <CardHeader>
          <CardTitle>Register New Official</CardTitle>
          <CardDescription>
            Create a new official account with assigned endorsers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="officialId">Official ID</Label>
                <Input
                  id="officialId"
                  type="number"
                  value={officialId}
                  onChange={(e) => setOfficialId(e.target.value)}
                  required
                  placeholder="Enter unique ID"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">Name (max 32 bytes)</Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={32}
                  required
                  placeholder="Official's name"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="authority">Authority Wallet</Label>
              <Input
                id="authority"
                type="text"
                value={authority}
                onChange={(e) => setAuthority(e.target.value)}
                required
                placeholder="Solana public key"
                className="font-mono text-sm"
              />
            </div>

            <div className="space-y-2">
              <Label>Endorsers</Label>
              <div className="space-y-3">
                <Input
                  type="text"
                  value={endorser1}
                  onChange={(e) => setEndorser1(e.target.value)}
                  required
                  placeholder="Endorser 1 public key"
                  className="font-mono text-sm"
                />
                <Input
                  type="text"
                  value={endorser2}
                  onChange={(e) => setEndorser2(e.target.value)}
                  required
                  placeholder="Endorser 2 public key"
                  className="font-mono text-sm"
                />
                <Input
                  type="text"
                  value={endorser3}
                  onChange={(e) => setEndorser3(e.target.value)}
                  required
                  placeholder="Endorser 3 public key"
                  className="font-mono text-sm"
                />
              </div>
            </div>

            <Button type="submit" disabled={loading} className="w-full md:w-auto">
              {loading ? 'Registering...' : 'Register Official'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Status Message */}
      {message && (
        <Alert variant={message.type === 'success' ? 'success' : 'destructive'}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* Registered Officials Table */}
      <Card>
        <CardHeader>
          <CardTitle>Registered Officials</CardTitle>
          <CardDescription>
            View all officials registered on-chain
          </CardDescription>
        </CardHeader>
        <CardContent>
          {officials.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No officials registered yet.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Authority</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {officials.map((official, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-medium">
                      {official.account.officialId.toString()}
                    </TableCell>
                    <TableCell>
                      {new TextDecoder().decode(new Uint8Array(official.account.name)).replace(/\0/g, '')}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {official.account.authority.toString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
