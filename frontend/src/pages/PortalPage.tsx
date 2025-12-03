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
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl mb-2">TruChain Portal</CardTitle>
            <CardDescription className="text-base">
              Access for Officials & Endorsers
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-muted-foreground">
              Please connect your wallet to access the portal
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

  // If user has no special role, show unauthorized message
  if (role === 'user') {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <CardTitle>Access Restricted</CardTitle>
            <CardDescription>
              This portal is only available for registered Officials and Endorsers.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground text-sm">
              Connected wallet: {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="pb-8">
      {/* Role Info Banner */}
      {role && (
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
