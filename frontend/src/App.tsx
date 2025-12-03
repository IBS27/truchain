import { useMemo } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import {
  ConnectionProvider,
  WalletProvider,
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';

import { FeedPage } from './pages/FeedPage';
import { PortalPage } from './pages/PortalPage';
import { WalletButton } from './components/WalletButton';

function Header() {
  const location = useLocation();
  const isPortal = location.pathname.startsWith('/portal');

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="container flex h-14 md:h-16 items-center justify-between px-4 mx-auto max-w-7xl">
        <div className="flex items-center gap-6">
          <Link to="/feed" className="flex items-center gap-2">
            <h1 className="text-xl md:text-2xl font-bold bg-linear-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
              TruChain
            </h1>
          </Link>
          <nav className="hidden md:flex items-center gap-4">
            <Link
              to="/feed"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                !isPortal ? 'text-foreground' : 'text-muted-foreground'
              }`}
            >
              Feed
            </Link>
            <Link
              to="/portal"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isPortal ? 'text-foreground' : 'text-muted-foreground'
              }`}
            >
              Portal
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          {/* Mobile nav */}
          <nav className="flex md:hidden items-center gap-3">
            <Link
              to="/feed"
              className={`text-xs font-medium transition-colors ${
                !isPortal ? 'text-foreground' : 'text-muted-foreground'
              }`}
            >
              Feed
            </Link>
            <Link
              to="/portal"
              className={`text-xs font-medium transition-colors ${
                isPortal ? 'text-foreground' : 'text-muted-foreground'
              }`}
            >
              Portal
            </Link>
          </nav>
          {isPortal && <WalletButton />}
        </div>
      </div>
    </header>
  );
}

function AppRoutes() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main className="md:container md:mx-auto md:px-4 md:py-6 md:max-w-7xl">
        <Routes>
          <Route path="/feed" element={<FeedPage />} />
          <Route path="/portal" element={<PortalPage />} />
          <Route path="/" element={<Navigate to="/feed" replace />} />
          <Route path="*" element={<Navigate to="/feed" replace />} />
        </Routes>
      </main>
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
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}

export default App;
