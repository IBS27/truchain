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
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Flag Details</DialogTitle>
          <DialogDescription>
            Community verification breakdown for this video
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : flagCounts ? (
          <div className="space-y-4">
            {/* Verified */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-green-600">Verified</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.verified} ({getPercentage(flagCounts.verified)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.verified)}%` }}
                />
              </div>
            </div>

            {/* Misleading */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-orange-600">Misleading</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.misleading} ({getPercentage(flagCounts.misleading)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.misleading)}%` }}
                />
              </div>
            </div>

            {/* Unverified */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-600">Unverified</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.unverified} ({getPercentage(flagCounts.unverified)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.unverified)}%` }}
                />
              </div>
            </div>

            {/* Fake */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-red-600">Fake</span>
                <span className="text-sm text-muted-foreground">
                  {flagCounts.fake} ({getPercentage(flagCounts.fake)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full transition-all"
                  style={{ width: `${getPercentage(flagCounts.fake)}%` }}
                />
              </div>
            </div>

            <div className="pt-2 border-t text-sm text-muted-foreground">
              Total votes: {total}
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
