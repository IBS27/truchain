import { useMemo } from 'react';
import {
  ConnectionProvider,
  WalletProvider,
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';
import { useWallet } from '@solana/wallet-adapter-react';

import { useRoleDetection } from './hooks/useRoleDetection';
import { AdminPanel } from './components/AdminPanel';
import { OfficialPanel } from './components/OfficialPanel';
import { EndorserPanel } from './components/EndorserPanel';
import { SocialFeed } from './components/SocialFeed';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { WalletButton } from './components/WalletButton';

function AppContent() {
  const { publicKey } = useWallet();
  const { role, loading, officialAccount, assignedOfficials } = useRoleDetection(publicKey);

  if (!publicKey) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl mb-2">TruChain</CardTitle>
            <CardDescription className="text-base">
              Video Authenticity Verification System
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground">
              Please connect your wallet to continue
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <CardTitle>Detecting your role...</CardTitle>
            <CardDescription>
              Please wait while we check your permissions on-chain
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="pb-8">
      {/* Role Info Banner - Only show for non-user roles */}
      {role && role !== 'user' && (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-muted-foreground">Role:</span>
                <Badge variant={role === 'admin' ? 'default' : role === 'official' ? 'success' : 'secondary'} className="text-sm">
                  {role}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">Wallet:</span>
                <code className="text-xs bg-muted px-2 py-1 rounded">
                  {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
                </code>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      {role === 'admin' && <AdminPanel />}
      {role === 'official' && officialAccount && <OfficialPanel officialAccount={officialAccount} />}
      {role === 'endorser' && <EndorserPanel assignedOfficials={assignedOfficials} />}
      {role === 'user' && <SocialFeed />}
      {!role && (
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-destructive">Error</CardTitle>
            <CardDescription>
              Failed to detect your role. Please try reconnecting your wallet.
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}

function App() {
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);

  const wallets = useMemo(
    () => [new PhantomWalletAdapter()],
    []
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
              <div className="container flex h-16 items-center justify-between px-4 mx-auto max-w-7xl">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold bg-linear-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
                    TruChain
                  </h1>
                </div>
                <WalletButton />
              </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-6 max-w-7xl">
              <AppContent />
            </main>
          </div>
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}

export default App;
