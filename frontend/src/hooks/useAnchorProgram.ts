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
    console.log('[useAnchorProgram] Checking wallet state:', {
      publicKey: wallet.publicKey?.toString(),
      connected: wallet.connected,
      signTransaction: !!wallet.signTransaction,
      signAllTransactions: !!wallet.signAllTransactions,
    });

    // Check if wallet is connected with all required methods
    if (!wallet.publicKey || !wallet.signTransaction || !wallet.signAllTransactions) {
      console.log('[useAnchorProgram] Wallet not ready, returning null');
      return null;
    }

    console.log('[useAnchorProgram] Creating Anchor program instance');

    try {
      // Create a wallet adapter that Anchor can use
      const anchorWallet = {
        publicKey: wallet.publicKey,
        signTransaction: wallet.signTransaction,
        signAllTransactions: wallet.signAllTransactions,
      };

      const provider = new AnchorProvider(
        connection,
        anchorWallet as any,
        { commitment: 'confirmed' }
      );

      const programInstance = new Program<Truchain>(
        idl as any,
        provider
      );

      console.log('[useAnchorProgram] Program created successfully:', programInstance.programId.toString());
      console.log('[useAnchorProgram] Program.account:', programInstance.account);
      console.log('[useAnchorProgram] Program.account keys:', Object.keys(programInstance.account || {}));
      return programInstance;
    } catch (error) {
      console.error('[useAnchorProgram] Error creating program:', error);
      return null;
    }
  }, [connection, wallet.publicKey, wallet.connected]);

  return program;
}
