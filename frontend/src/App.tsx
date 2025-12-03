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
    <header className="sticky top-0 z-50 w-full border-b border-border/40 glass">
      <div className="container flex h-14 md:h-16 items-center justify-between px-4 mx-auto max-w-7xl">
        <div className="flex items-center gap-8">
          <Link to="/feed" className="flex items-center gap-3 group">
            {/* Logo Icon */}
            <div className="relative w-8 h-8 flex items-center justify-center">
              <div className="absolute inset-0 bg-primary/20 rounded-lg blur-md group-hover:bg-primary/30 transition-colors" />
              <svg
                viewBox="0 0 24 24"
                className="w-6 h-6 text-primary relative z-10"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <h1 className="text-xl md:text-2xl font-bold gradient-text-brand tracking-tight">
              TruChain
            </h1>
          </Link>
          <nav className="hidden md:flex items-center gap-1">
            <Link
              to="/feed"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                !isPortal
                  ? 'text-foreground bg-secondary/50'
                  : 'text-muted-foreground hover:text-foreground hover:bg-secondary/30'
              }`}
            >
              Feed
            </Link>
            <Link
              to="/portal"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isPortal
                  ? 'text-foreground bg-secondary/50'
                  : 'text-muted-foreground hover:text-foreground hover:bg-secondary/30'
              }`}
            >
              Portal
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          {/* Mobile nav */}
          <nav className="flex md:hidden items-center gap-1">
            <Link
              to="/feed"
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                !isPortal
                  ? 'text-foreground bg-secondary/50'
                  : 'text-muted-foreground'
              }`}
            >
              Feed
            </Link>
            <Link
              to="/portal"
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                isPortal
                  ? 'text-foreground bg-secondary/50'
                  : 'text-muted-foreground'
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
    <div className="min-h-screen bg-mesh">
      <Header />
      <main className="md:container md:mx-auto md:px-4 md:py-8 md:max-w-7xl animate-fade-in">
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
