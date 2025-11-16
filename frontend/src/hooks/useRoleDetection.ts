import { useState, useEffect } from 'react';
import { PublicKey } from '@solana/web3.js';
import { useAnchorProgram } from './useAnchorProgram';
import {
  checkIsAdmin,
  checkIsOfficialAuthority,
  checkIsEndorser,
} from '../services/solana';

export type Role = 'admin' | 'official' | 'endorser' | 'user' | null;

export interface RoleDetectionResult {
  role: Role;
  loading: boolean;
  officialAccount: any | null; // Official account if role is 'official'
  assignedOfficials: any[]; // Official accounts if role is 'endorser'
}

/**
 * Hook to detect wallet role based on on-chain data
 * Returns role, loading state, and relevant account data
 */
export function useRoleDetection(walletPubkey: PublicKey | null): RoleDetectionResult {
  const program = useAnchorProgram();
  const [result, setResult] = useState<RoleDetectionResult>({
    role: null,
    loading: true,
    officialAccount: null,
    assignedOfficials: [],
  });

  useEffect(() => {
    async function detectRole() {
      if (!walletPubkey || !program) {
        setResult({
          role: null,
          loading: false,
          officialAccount: null,
          assignedOfficials: [],
        });
        return;
      }

      setResult(prev => ({ ...prev, loading: true }));

      try {
        // Check admin first (cheapest check)
        if (checkIsAdmin(walletPubkey)) {
          setResult({
            role: 'admin',
            loading: false,
            officialAccount: null,
            assignedOfficials: [],
          });
          return;
        }

        // Check if official's authority
        const officialAccount = await checkIsOfficialAuthority(program, walletPubkey);
        if (officialAccount) {
          setResult({
            role: 'official',
            loading: false,
            officialAccount,
            assignedOfficials: [],
          });
          return;
        }

        // Check if endorser
        const assignedOfficials = await checkIsEndorser(program, walletPubkey);
        if (assignedOfficials.length > 0) {
          setResult({
            role: 'endorser',
            loading: false,
            officialAccount: null,
            assignedOfficials,
          });
          return;
        }

        // Default to user
        setResult({
          role: 'user',
          loading: false,
          officialAccount: null,
          assignedOfficials: [],
        });
      } catch (error) {
        console.error('Role detection error:', error);
        setResult({
          role: null,
          loading: false,
          officialAccount: null,
          assignedOfficials: [],
        });
      }
    }

    detectRole();
  }, [walletPubkey, program]);

  return result;
}
