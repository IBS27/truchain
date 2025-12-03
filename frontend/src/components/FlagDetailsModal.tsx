import { useEffect, useState } from 'react';
import type { FlagCounts } from '../services/api';
import { socialApi } from '../services/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';

interface FlagDetailsModalProps {
  videoId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export function FlagDetailsModal({ videoId, isOpen, onClose }: FlagDetailsModalProps) {
  const [flagCounts, setFlagCounts] = useState<FlagCounts | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (videoId && isOpen) {
      setLoading(true);
      socialApi.getFlagCounts(videoId)
        .then(setFlagCounts)
        .catch(err => console.error('Failed to load flag counts:', err))
        .finally(() => setLoading(false));
    }
  }, [videoId, isOpen]);

  const total = flagCounts
    ? flagCounts.verified + flagCounts.misleading + flagCounts.unverified + flagCounts.fake
    : 0;

  const getPercentage = (count: number) => {
    return total > 0 ? Math.round((count / total) * 100) : 0;
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="px-8">
        <DialogHeader>
          <DialogTitle>Flag Details</DialogTitle>
          <DialogDescription>
            Community verification breakdown for this video
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex flex-col items-center gap-3 py-8">
            <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
            <span className="text-muted-foreground">Loading...</span>
          </div>
        ) : flagCounts ? (
          <div className="space-y-5">
            {/* Verified */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-semibold text-emerald-400">Verified</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.verified} ({getPercentage(flagCounts.verified)}%)
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-emerald-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${getPercentage(flagCounts.verified)}%` }}
                />
              </div>
            </div>

            {/* Misleading */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-semibold text-amber-400">Misleading</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.misleading} ({getPercentage(flagCounts.misleading)}%)
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-amber-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${getPercentage(flagCounts.misleading)}%` }}
                />
              </div>
            </div>

            {/* Unverified */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-semibold text-slate-400">Unverified</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.unverified} ({getPercentage(flagCounts.unverified)}%)
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-slate-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${getPercentage(flagCounts.unverified)}%` }}
                />
              </div>
            </div>

            {/* Fake */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-semibold text-red-400">Fake</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.fake} ({getPercentage(flagCounts.fake)}%)
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-red-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${getPercentage(flagCounts.fake)}%` }}
                />
              </div>
            </div>

            <div className="pt-4 border-t border-border/50 text-sm text-muted-foreground">
              Total votes: <span className="font-semibold text-foreground">{total}</span>
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
