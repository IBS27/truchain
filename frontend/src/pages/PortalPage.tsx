import { useWallet } from '@solana/wallet-adapter-react';
import { useRoleDetection } from '../hooks/useRoleDetection';
import { AdminPanel } from '../components/AdminPanel';
import { OfficialPanel } from '../components/OfficialPanel';
import { EndorserPanel } from '../components/EndorserPanel';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { WalletButton } from '../components/WalletButton';

export function PortalPage() {
  const { publicKey } = useWallet();
  const { role, loading, officialAccount, assignedOfficials } = useRoleDetection(publicKey);

  if (!publicKey) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full glass-card border-0">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <CardTitle className="text-3xl mb-2 gradient-text-brand">TruChain Portal</CardTitle>
            <CardDescription className="text-base">
              Access for Officials & Endorsers
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-6 pt-4">
            <p className="text-muted-foreground">
              Connect your wallet to access the verification portal
            </p>
            <WalletButton />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full glass-card border-0">
          <CardHeader className="text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              <CardTitle>Detecting your role...</CardTitle>
              <CardDescription>
                Please wait while we check your permissions on-chain
              </CardDescription>
            </div>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (role === 'user') {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full glass-card border-0">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-destructive/10 flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <CardTitle>Access Restricted</CardTitle>
            <CardDescription>
              This portal is only available for registered Officials and Endorsers.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center pt-4">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary/50 text-sm">
              <span className="text-muted-foreground">Wallet:</span>
              <code className="font-mono text-foreground">
                {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
              </code>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="pb-8 animate-fade-in">
      {/* Role Info Banner */}
      {role && (
        <Card className="mb-8 glass-card border-0">
          <CardContent className="py-5">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className={`
                  w-10 h-10 rounded-xl flex items-center justify-center
                  ${role === 'admin' ? 'bg-primary/15' : role === 'official' ? 'bg-emerald-500/15' : 'bg-sky-500/15'}
                `}>
                  {role === 'admin' && (
                    <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  )}
                  {role === 'official' && (
                    <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  )}
                  {role === 'endorser' && (
                    <svg className="w-5 h-5 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                  )}
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Signed in as</span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Badge variant={role === 'admin' ? 'default' : role === 'official' ? 'success' : 'info'} className="capitalize">
                      {role}
                    </Badge>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-secondary/30">
                <svg className="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <code className="text-xs font-mono">
                  {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
                </code>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
        {role === 'admin' && <AdminPanel />}
        {role === 'official' && officialAccount && <OfficialPanel officialAccount={officialAccount} />}
        {role === 'endorser' && <EndorserPanel assignedOfficials={assignedOfficials} />}
        {!role && (
          <Card className="glass-card border-0">
            <CardHeader className="text-center">
              <CardTitle className="text-destructive">Error</CardTitle>
              <CardDescription>
                Failed to detect your role. Please try reconnecting your wallet.
              </CardDescription>
            </CardHeader>
          </Card>
        )}
      </div>
    </div>
  );
}
