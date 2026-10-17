import React from 'react';
import { Activity, Clock, Trophy } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { InfoButton } from './InfoButton';

export const MetricsPanel: React.FC = () => {
  const { currentSnapshot } = useRaceStore();
  const car = currentSnapshot?.car;
  const metrics = currentSnapshot?.metrics;

  const totalTime = metrics?.total_time || 0.0;
  const avgLap = metrics?.avg_lap_time || 0.0;
  const bestLap = car?.best_lap_time || 0.0;
  const position = car?.position || 1;
  const gapAhead = car?.gap_ahead_s || 0.0;
  const gapBehind = car?.gap_behind_s || 0.0;
  const replans = metrics?.replans || 0;
  const fuelUsed = metrics?.fuel_used || 0.0;

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Activity size={16} color="#06b6d4" />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Live Performance Metrics
          </h3>
          <InfoButton explanationId="lap_time_breakdown" title="How is lap time calculated?" />
        </div>
        <span
          className="racing-badge"
          style={{
            background: position === 1 ? 'rgba(234, 179, 8, 0.2)' : 'rgba(6, 182, 212, 0.2)',
            color: position === 1 ? '#eab308' : '#06b6d4',
            fontSize: 12,
          }}
        >
          <Trophy size={12} /> POSITION P{position}
        </span>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, textAlign: 'center' }}>
        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>TOTAL TIME</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>
            {totalTime.toFixed(1)}s
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>AVG LAP</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#06b6d4' }}>
            {avgLap.toFixed(2)}s
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>BEST LAP</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#10b981' }}>
            {bestLap > 0 ? `${bestLap.toFixed(2)}s` : '--'}
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>GAP AHEAD</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#94a3b8' }}>
            {position > 1 ? `+${gapAhead.toFixed(1)}s` : 'LEADER'}
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>REPLANS</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#f59e0b' }}>
            {replans}
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>TOTAL FUEL</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#cbd5e1' }}>
            {fuelUsed.toFixed(1)} kg
          </div>
        </div>
      </div>
    </div>
  );
};
