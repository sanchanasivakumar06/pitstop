import React from 'react';
import { Disc, AlertTriangle } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { getCompoundColor } from '../canvas/colors';
import { InfoButton } from './InfoButton';

export const TyreCard: React.FC = () => {
  const { currentSnapshot } = useRaceStore();
  const tyre = currentSnapshot?.car?.tyre;

  const compound = tyre?.compound || 'MEDIUM';
  const compoundColor = getCompoundColor(compound);
  const wearPct = tyre?.wear_pct || 0.0;
  const gripPct = tyre?.grip_pct || 100.0;
  const ageLaps = tyre?.age_laps || 0;
  const tempC = tyre?.temp_c || 30.0;

  // Approximate cliff thresholds
  const cliffThreshold = compound.includes('SOFT') ? 60.0 : compound.includes('HARD') ? 78.0 : 70.0;
  const isPastCliff = wearPct >= cliffThreshold;

  return (
    <div
      className={`racing-card ${isPastCliff ? 'pulse-warning' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        border: isPastCliff ? '1px solid #ef4444' : undefined,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Disc size={16} color={compoundColor} />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Tyre Degradation & Grip
          </h3>
          <InfoButton explanationId="tyre_wear_calculation" title="How is tyre wear calculated?" />
        </div>

        {/* Compound Badge */}
        <span
          className="racing-badge"
          style={{
            background: `${compoundColor}25`,
            color: compoundColor,
            border: `1px solid ${compoundColor}`,
          }}
        >
          {compound} ({ageLaps} LAPS OLD)
        </span>
      </div>

      {/* Degradation Bar with Shaded Cliff Zone */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
          <span style={{ color: '#94a3b8' }}>Accumulated Wear:</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: isPastCliff ? '#ef4444' : '#f8fafc' }}>
            {wearPct.toFixed(1)}% {isPastCliff ? '(PAST CLIFF!)' : ''}
          </span>
        </div>

        <div style={{ height: 10, background: '#0a0c10', borderRadius: 5, overflow: 'hidden', position: 'relative' }}>
          {/* Shaded Cliff Hazard Zone */}
          <div
            style={{
              position: 'absolute',
              left: `${cliffThreshold}%`,
              right: 0,
              top: 0,
              bottom: 0,
              background: 'rgba(239, 68, 68, 0.25)',
              borderLeft: '1.5px dashed #ef4444',
              zIndex: 1,
            }}
            title={`Degradation Cliff Zone (> ${cliffThreshold}% wear)`}
          />

          {/* Active wear level */}
          <div
            style={{
              height: '100%',
              width: `${Math.min(100, wearPct)}%`,
              background: isPastCliff
                ? 'linear-gradient(90deg, #f59e0b, #ef4444)'
                : 'linear-gradient(90deg, #06b6d4, #f59e0b)',
              transition: 'width 0.3s ease',
            }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b', marginTop: 3 }}>
          <span>0% (New)</span>
          <span style={{ color: '#ef4444' }}>▲ Cliff Zone ({cliffThreshold}%)</span>
          <span>100% (Destroyed)</span>
        </div>
      </div>

      {/* Telemetry Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, textAlign: 'center' }}>
        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>MECHANICAL GRIP</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#10b981' }}>
            {gripPct.toFixed(1)}%
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>TYRE TEMP</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#f59e0b' }}>
            {tempC.toFixed(1)}°C
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>CLIFF BUFFER</div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 13,
              fontWeight: 700,
              color: isPastCliff ? '#ef4444' : '#06b6d4',
            }}
          >
            {isPastCliff ? 'EXCEEDED' : `+${(cliffThreshold - wearPct).toFixed(1)}%`}
          </div>
        </div>
      </div>
    </div>
  );
};
