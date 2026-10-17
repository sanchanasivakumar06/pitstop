import { useEffect } from 'react';
import { useRaceStore } from '../store/useRaceStore';

export function usePlayback() {
  const { isPlaying, isOfflineMode, step, playbackSpeed } = useRaceStore();

  useEffect(() => {
    if (!isPlaying || !isOfflineMode) return;

    const interval = setInterval(() => {
      step();
    }, 1000 / (1.5 * playbackSpeed));

    return () => clearInterval(interval);
  }, [isPlaying, isOfflineMode, playbackSpeed, step]);
}
