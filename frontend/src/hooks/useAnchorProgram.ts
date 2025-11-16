import { useMemo } from 'react';
import { AnchorProvider, Program } from '@coral-xyz/anchor';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import type { Truchain } from '../anchor/idl';
import idl from '../anchor/idl';

/**
 * Hook to get initialized Anchor program instance
 * Returns null if wallet not connected
 */
export function useAnchorProgram() {
  const { connection } = useConnection();
  const wallet = useWallet();

  const program = useMemo(() => {
    // Check if wallet is connected with all required methods
    if (!wallet.publicKey || !wallet.connected) {
      return null;
    }

    // Create a wallet adapter that Anchor can use
    const anchorWallet = {
      publicKey: wallet.publicKey,
      signTransaction: wallet.signTransaction!,
      signAllTransactions: wallet.signAllTransactions!,
    };

    const provider = new AnchorProvider(
      connection,
      anchorWallet as any,
      { commitment: 'confirmed' }
    );

    return new Program<Truchain>(
      idl as any,
      provider
    );
  }, [connection, wallet, wallet.publicKey, wallet.connected]);

  return program;
}
