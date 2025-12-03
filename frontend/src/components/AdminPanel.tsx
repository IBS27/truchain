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
      const authorityPubkey = new PublicKey(authority);
      const endorser1Pubkey = new PublicKey(endorser1);
      const endorser2Pubkey = new PublicKey(endorser2);
      const endorser3Pubkey = new PublicKey(endorser3);

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

      setOfficialId('');
      setName('');
      setAuthority('');
      setEndorser1('');
      setEndorser2('');
      setEndorser3('');

      await loadOfficials();
    } catch (error: any) {
      console.error('Registration error:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to register official' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOfficials();
  }, [loadOfficials]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight gradient-text">Admin Panel</h2>
        <p className="text-muted-foreground mt-1">
          Register new officials and manage endorsers
        </p>
      </div>

      {/* Register Official Form */}
      <Card className="glass-card border-0">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <div>
              <CardTitle>Register New Official</CardTitle>
              <CardDescription>
                Create a new official account with assigned endorsers
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
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

            <div className="space-y-3">
              <Label>Endorsers</Label>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center text-xs font-medium text-muted-foreground">1</span>
                  <Input
                    type="text"
                    value={endorser1}
                    onChange={(e) => setEndorser1(e.target.value)}
                    required
                    placeholder="Endorser 1 public key"
                    className="font-mono text-sm"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center text-xs font-medium text-muted-foreground">2</span>
                  <Input
                    type="text"
                    value={endorser2}
                    onChange={(e) => setEndorser2(e.target.value)}
                    required
                    placeholder="Endorser 2 public key"
                    className="font-mono text-sm"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center text-xs font-medium text-muted-foreground">3</span>
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
            </div>

            <Button type="submit" disabled={loading} variant="glow" className="w-full md:w-auto">
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Registering...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Register Official
                </>
              )}
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
      <Card className="glass-card border-0">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <CardTitle>Registered Officials</CardTitle>
              <CardDescription>
                View all officials registered on-chain
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {officials.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl bg-secondary/50 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <p className="text-muted-foreground">No officials registered yet.</p>
            </div>
          ) : (
            <div className="rounded-xl overflow-hidden border border-border/30">
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
                      <TableCell className="font-semibold text-primary">
                        #{official.account.officialId.toString()}
                      </TableCell>
                      <TableCell className="font-medium">
                        {new TextDecoder().decode(new Uint8Array(official.account.name)).replace(/\0/g, '')}
                      </TableCell>
                      <TableCell>
                        <code className="font-mono text-xs px-2 py-1 rounded-md bg-secondary/50">
                          {official.account.authority.toString().slice(0, 8)}...{official.account.authority.toString().slice(-8)}
                        </code>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
