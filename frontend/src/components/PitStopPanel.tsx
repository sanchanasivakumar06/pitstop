import React from 'react';
import { Wrench, CheckCircle, ArrowRight } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { InfoButton } from './InfoButton';

const PIT_STAGES = ['ENTRY', 'BOX_STOP', 'TYRE_CHANGE', 'REFUEL', 'EXIT'];

export const PitStopPanel: React.FC = () => {
  const { currentSnapshot } = useRaceStore();
  const pit = currentSnapshot?.pit;

  const inProgress = pit?.in_progress || false;
  const currentStage = pit?.stage || 'NONE';
  const stopsDone = pit?.stops_done || 0;
  const timeLoss = pit?.time_loss_s || 0.0;

  return (
    <div
      className={`racing-card ${inProgress ? 'pulse-warning' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        border: inProgress ? '1px solid #06b6d4' : undefined,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Wrench size={16} color={inProgress ? '#06b6d4' : '#94a3b8'} />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Pit Stop Status & Stages
          </h3>
          <InfoButton explanationId="pit_stop_time" title="How is pit stop time calculated?" />
        </div>
        <span
          className="racing-badge"
          style={{
            background: inProgress ? 'rgba(6, 182, 212, 0.2)' : 'rgba(100, 116, 139, 0.2)',
            color: inProgress ? '#06b6d4' : '#94a3b8',
          }}
        >
          {inProgress ? 'BOXING THIS LAP' : 'ON TRACK'}
        </span>
      </div>

      {/* Stage Tracker Pipeline */}
      {inProgress && (
        <div style={{ background: '#0a0c10', padding: 10, borderRadius: 6 }}>
          <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', marginBottom: 8 }}>
            LIVE PIT STOP SERVICE SEQUENCE
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {PIT_STAGES.map((st, i) => {
              const isActive = st === currentStage;
              const isPassed = PIT_STAGES.indexOf(currentStage) > i;

              return (
                <React.Fragment key={st}>
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 4,
                    }}
                  >
                    <div
                      style={{
                        width: 18,
                        height: 18,
                        borderRadius: '50%',
                        background: isActive ? '#06b6d4' : isPassed ? '#10b981' : '#222938',
                        color: '#03141f',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 10,
                        fontWeight: 700,
                      }}
                    >
                      {isPassed ? '✓' : i + 1}
                    </div>
                    <span
                      style={{
                        fontSize: 9,
                        color: isActive ? '#06b6d4' : isPassed ? '#cbd5e1' : '#64748b',
                        fontWeight: isActive ? 700 : 500,
                      }}
                    >
                      {st.replace('_', ' ')}
                    </span>
                  </div>
                  {i < PIT_STAGES.length - 1 && (
                    <div
                      style={{
                        height: 2,
                        flex: 1,
                        background: isPassed ? '#10b981' : '#222938',
                        margin: '0 4px',
                        marginBottom: 14,
                      }}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}

      {/* Pit Stop Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, textAlign: 'center' }}>
        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>STOPS DONE</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 700, color: '#f8fafc' }}>
            {stopsDone}
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>TOTAL PIT LOSS</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 700, color: '#f59e0b' }}>
            {timeLoss.toFixed(1)}s
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>NEXT PLANNED</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 700, color: '#06b6d4' }}>
            {pit?.planned_next_pit_lap ? `LAP ${pit.planned_next_pit_lap}` : 'DYNAMIC'}
          </div>
        </div>
      </div>
    </div>
  );
};
