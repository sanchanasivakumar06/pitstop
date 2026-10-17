import { useEffect } from 'react';
import { useRaceStore } from '../store/useRaceStore';

export function useKeyboard() {
  const { isPlaying, play, pause, step, currentSnapshot, setExplanation, activeExplanation } = useRaceStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept typing in inputs
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        if (isPlaying) pause();
        else play();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        step();
      } else if (e.key === 'i' || e.key === 'I') {
        e.preventDefault();
        if (activeExplanation) {
          setExplanation(null);
        } else if (currentSnapshot?.decision?.explanation?.[0]) {
          setExplanation(currentSnapshot.decision.explanation[0]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isPlaying, play, pause, step, currentSnapshot, activeExplanation, setExplanation]);
}
