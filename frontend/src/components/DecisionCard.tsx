import React from 'react';
import { Cpu, Zap, ArrowRightCircle } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { InfoButton } from './InfoButton';

export const DecisionCard: React.FC = () => {
  const { currentSnapshot, strategies, setDrawerTab } = useRaceStore();
  const decision = currentSnapshot?.decision;

  const action = decision?.action || 'STAY_OUT';
  const reason = decision?.reason || 'Circulating on track according to policy.';
  const qValues = decision?.q_values || {};
  const replanned = decision?.replanned || false;

  // Find strategy info
  const activeStrategy = strategies.find(
    (s) => s.id === 'mdp_agent'
  ) || { ai_concept: 'MDP Backward Induction + Bayesian HMM' };

  // Sort Q-values ascending (lower expected time = better)
  const sortedActions = Object.entries(qValues).sort((a, b) => a[1] - b[1]);

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Card Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Cpu size={16} color="#06b6d4" />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Current Strategy Decision
          </h3>
          <InfoButton explanationId="strategy_decision" title="Why this decision?" />
        </div>

        {replanned && (
          <span
            className="racing-badge pulse-warning"
            style={{ background: 'rgba(245, 158, 11, 0.25)', color: '#f59e0b', border: '1px solid #f59e0b' }}
          >
            ⚡ DYNAMIC REPLAN
          </span>
        )}
      </div>

      {/* AI Concept Banner */}
      <div style={{ fontSize: 11, color: '#94a3b8' }}>
        CORE AI CONCEPT: <strong style={{ color: '#06b6d4' }}>{activeStrategy.ai_concept}</strong>
      </div>

      {/* Action and Rationale */}
      <div
        style={{
          background: '#0a0c10',
          border: '1px solid #262e3f',
          borderRadius: 6,
          padding: '10px 12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <span
            className="racing-badge"
            style={{
              background: action === 'STAY_OUT' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(6, 182, 212, 0.25)',
              color: action === 'STAY_OUT' ? '#10b981' : '#06b6d4',
              border: action === 'STAY_OUT' ? '1px solid #10b981' : '1px solid #06b6d4',
              fontSize: 12,
            }}
          >
            ACTION: {action}
          </span>
        </div>
        <p style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.4 }}>
          {reason}
        </p>
      </div>

      {/* Ranked Action Q-values Bars */}
      {sortedActions.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b', marginBottom: 6 }}>
            <span>EVALUATED ACTIONS</span>
            <span>EXP. REMAINING TIME</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {sortedActions.slice(0, 4).map(([act, qVal], rank) => {
              const isChosen = act === action;
              const minVal = sortedActions[0][1];
              const delta = qVal - minVal;

              return (
                <div
                  key={act}
                  style={{
                    background: isChosen ? 'rgba(6, 182, 212, 0.12)' : '#181d28',
                    border: isChosen ? '1px solid #06b6d4' : '1px solid #262e3f',
                    borderRadius: 4,
                    padding: '6px 10px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: 11,
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ color: isChosen ? '#06b6d4' : '#64748b' }}>#{rank + 1}</span>
                    <strong style={{ color: isChosen ? '#06b6d4' : '#f8fafc' }}>{act}</strong>
                  </div>
                  <div>
                    <span style={{ color: delta === 0 ? '#10b981' : '#ef4444' }}>
                      {delta === 0 ? `${qVal.toFixed(1)}s (BEST)` : `+${delta.toFixed(1)}s`}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
