import React from 'react';
import { X, Calculator, HelpCircle, CheckCircle2 } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';

export const ExplanationDrawer: React.FC = () => {
  const {
    activeExplanation,
    activeDrawerTab,
    currentSnapshot,
    setExplanation,
    setDrawerTab,
  } = useRaceStore();

  if (!activeExplanation && activeDrawerTab !== 'ranking') {
    return null;
  }

  const decision = currentSnapshot?.decision;
  const qValues = decision?.q_values || {};
  const sortedQ = Object.entries(qValues).sort((a, b) => a[1] - b[1]);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: 440,
        background: '#12161f',
        borderLeft: '1px solid #262e3f',
        boxShadow: '-8px 0 30px rgba(0,0,0,0.7)',
        zIndex: 100,
        display: 'flex',
        flexDirection: 'column',
        animation: 'slideIn 0.2s ease-out',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid #262e3f',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#181d28',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Calculator size={18} color="#06b6d4" />
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc' }}>
            Mathematical Explanation
          </h3>
        </div>
        <button
          onClick={() => {
            setExplanation(null);
            setDrawerTab(null);
          }}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: 4,
          }}
        >
          <X size={18} />
        </button>
      </div>

      {/* Content Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>
        {activeExplanation && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Title & Plain English */}
            <div>
              <span className="racing-badge" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4', marginBottom: 6 }}>
                EXPLANATION ID: {activeExplanation.id}
              </span>
              <h4 style={{ fontSize: 18, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>
                {activeExplanation.title}
              </h4>
              <p style={{ fontSize: 13, color: '#94a3b8', marginTop: 6, lineHeight: 1.4 }}>
                {activeExplanation.plain_english}
              </p>
            </div>

            {/* Formula Block */}
            <div
              style={{
                background: '#0a0c10',
                border: '1px solid #262e3f',
                borderRadius: 6,
                padding: '12px 14px',
              }}
            >
              <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
                MATHEMATICAL FORMULA
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 12,
                  color: '#06b6d4',
                  marginTop: 6,
                  wordBreak: 'break-all',
                }}
              >
                {activeExplanation.formula}
              </div>
            </div>

            {/* Inputs Plugged In */}
            <div
              style={{
                background: '#181d28',
                border: '1px solid #262e3f',
                borderRadius: 6,
                padding: '12px 14px',
              }}
            >
              <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', fontWeight: 600, marginBottom: 8 }}>
                LIVE INPUT VALUES
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                {Object.entries(activeExplanation.inputs || {}).map(([k, v]) => (
                  <div key={k} style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                    <span style={{ color: '#94a3b8' }}>{k}: </span>
                    <strong style={{ color: '#f8fafc' }}>{String(v)}</strong>
                  </div>
                ))}
              </div>
            </div>

            {/* Step-by-Step Arithmetic */}
            <div
              style={{
                background: '#181d28',
                border: '1px solid #262e3f',
                borderRadius: 6,
                padding: '12px 14px',
              }}
            >
              <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', fontWeight: 600, marginBottom: 8 }}>
                STEP-BY-STEP CALCULATION
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {activeExplanation.steps?.map((step, idx) => (
                  <div
                    key={idx}
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: 11,
                      color: '#cbd5e1',
                      padding: '4px 6px',
                      background: 'rgba(0,0,0,0.2)',
                      borderRadius: 4,
                    }}
                  >
                    {step}
                  </div>
                ))}
              </div>
            </div>

            {/* Result */}
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(2, 132, 199, 0.05))',
                border: '1px solid #06b6d4',
                borderRadius: 6,
                padding: '12px 14px',
              }}
            >
              <div style={{ fontSize: 11, color: '#06b6d4', textTransform: 'uppercase', fontWeight: 700 }}>
                FINAL RESULT
              </div>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>
                {activeExplanation.result}
              </div>
            </div>
          </div>
        )}

        {/* Why this decision? Ranked Action Comparison */}
        {sortedQ.length > 0 && (
          <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid #262e3f' }}>
            <h4 style={{ fontSize: 14, fontWeight: 700, color: '#f8fafc', marginBottom: 12 }}>
              Why this decision? Ranked Action Values
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {sortedQ.map(([act, qVal], rank) => {
                const isChosen = act === decision?.action;
                const minVal = sortedQ[0][1];
                const delta = qVal - minVal;

                return (
                  <div
                    key={act}
                    style={{
                      padding: '8px 12px',
                      borderRadius: 6,
                      background: isChosen ? 'rgba(6, 182, 212, 0.15)' : '#181d28',
                      border: isChosen ? '1px solid #06b6d4' : '1px solid #262e3f',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontSize: 11, color: isChosen ? '#06b6d4' : '#64748b' }}>
                          #{rank + 1}
                        </span>
                        <strong style={{ fontSize: 13, color: isChosen ? '#06b6d4' : '#f8fafc' }}>
                          {act}
                        </strong>
                        {isChosen && (
                          <span
                            className="racing-badge"
                            style={{ background: '#06b6d4', color: '#03141f', fontSize: 9 }}
                          >
                            CHOSEN
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
                        Expected Remaining: {qVal.toFixed(1)}s
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                      <span style={{ color: delta === 0 ? '#10b981' : '#ef4444' }}>
                        {delta === 0 ? 'OPTIMAL' : `+${delta.toFixed(1)}s`}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
