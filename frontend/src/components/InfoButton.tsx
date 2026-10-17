import React from 'react';
import { Info } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { ExplanationBlock } from '../types/snapshot';

interface InfoButtonProps {
  explanationId?: string;
  fallbackExplanation?: ExplanationBlock;
  title?: string;
}

export const InfoButton: React.FC<InfoButtonProps> = ({
  explanationId,
  fallbackExplanation,
  title = 'How is this calculated?',
}) => {
  const { currentSnapshot, setExplanation } = useRaceStore();

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!currentSnapshot && !fallbackExplanation) return;

    // Search explanation in current snapshot decision explanations
    const matched = currentSnapshot?.decision?.explanation?.find(
      (expl) => expl.id === explanationId
    ) || fallbackExplanation;

    if (matched) {
      setExplanation(matched);
    }
  };

  return (
    <button
      onClick={handleClick}
      style={{
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        padding: '2px 4px',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#06b6d4',
        borderRadius: 4,
        transition: 'all 0.15s ease',
      }}
      title={title}
      aria-label={title}
    >
      <Info size={14} />
    </button>
  );
};
