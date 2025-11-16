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
    if (!wallet.publicKey || !wallet.signTransaction || !wallet.signAllTransactions) {
      return null;
    }

    const provider = new AnchorProvider(
      connection,
      wallet as any,
      { commitment: 'confirmed' }
    );

    return new Program<Truchain>(
      idl as any,
      provider
    );
  }, [connection, wallet]);

  return program;
}
