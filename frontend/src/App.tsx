import { useMemo } from 'react';
import {
  ConnectionProvider,
  WalletProvider,
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets';
import {
  WalletModalProvider,
  WalletMultiButton,
} from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';
import { useWallet } from '@solana/wallet-adapter-react';

import { useRoleDetection } from './hooks/useRoleDetection';
import { AdminPanel } from './components/AdminPanel';
import { OfficialPanel } from './components/OfficialPanel';
import { EndorserPanel } from './components/EndorserPanel';

import './App.css';
import '@solana/wallet-adapter-react-ui/styles.css';

function AppContent() {
  const { publicKey } = useWallet();
  const { role, loading, officialAccount, assignedOfficials } = useRoleDetection(publicKey);

  if (!publicKey) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h1>TruChain - Video Authenticity Verification</h1>
        <p>Please connect your wallet to continue</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2>Detecting your role...</h2>
        <p>Please wait while we check your permissions on-chain</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h1>TruChain</h1>
        <p>
          <strong>Role:</strong> {role || 'Unknown'} | <strong>Wallet:</strong>{' '}
          {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
        </p>
      </div>

      {role === 'admin' && <AdminPanel />}
      {role === 'official' && officialAccount && <OfficialPanel officialAccount={officialAccount} />}
      {role === 'endorser' && <EndorserPanel assignedOfficials={assignedOfficials} />}
      {role === 'user' && (
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <h2>User View</h2>
          <p>You don't have admin, official, or endorser privileges.</p>
          <p>Social feed functionality coming soon!</p>
        </div>
      )}
      {!role && (
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <h2>Error</h2>
          <p>Failed to detect your role. Please try reconnecting your wallet.</p>
        </div>
      )}
    </div>
  );
}

function App() {
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);

  const wallets = useMemo(
    () => [new PhantomWalletAdapter()],
    [network]
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <div style={{ padding: '20px', textAlign: 'right' }}>
            <WalletMultiButton />
          </div>
          <AppContent />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}

export default App;
