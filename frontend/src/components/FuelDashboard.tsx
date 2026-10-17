import React from 'react';
import { Fuel, Gauge, Award, ArrowUp, ArrowDown } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { InfoButton } from './InfoButton';

export const FuelDashboard: React.FC = () => {
  const { currentSnapshot, totalLaps } = useRaceStore();
  const car = currentSnapshot?.car;

  const fuelKg = car?.fuel_kg ?? 65.0;
  const capacityKg = car?.fuel_capacity_kg ?? 105.0;
  const fuelPct = Math.min(100, Math.max(0, (fuelKg / capacityKg) * 100));
  const burnRate = car?.fuel_per_lap ?? 1.75;
  const lapsRemaining = car?.fuel_laps_remaining ?? (fuelKg / burnRate);
  const remainingRaceLaps = Math.max(0, totalLaps - (currentSnapshot?.lap || 0));
  const minFuelNeededToFinish = remainingRaceLaps * burnRate;
  const isFuelLow = fuelKg < 7.0 || lapsRemaining < 3.0;

  return (
    <div
      className={`racing-card ${isFuelLow ? 'pulse-warning' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        border: isFuelLow ? '1px solid #ef4444' : undefined,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Fuel size={16} color={isFuelLow ? '#ef4444' : '#06b6d4'} />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Fuel Telemetry & Stint Range
          </h3>
          <InfoButton explanationId="fuel_calculation" title="How is remaining fuel calculated?" />
        </div>
        <span
          className="racing-badge"
          style={{
            background: isFuelLow ? 'rgba(239, 68, 68, 0.2)' : 'rgba(6, 182, 212, 0.15)',
            color: isFuelLow ? '#ef4444' : '#06b6d4',
          }}
        >
          {isFuelLow ? 'LOW FUEL WARNING' : 'STINT SAFE'}
        </span>
      </div>

      {/* Fuel Gauge Bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
          <span style={{ color: '#94a3b8' }}>Usable Fuel:</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#f8fafc' }}>
            {fuelKg.toFixed(2)} kg / {capacityKg} kg ({fuelPct.toFixed(1)}%)
          </span>
        </div>
        {/* Progress track */}
        <div style={{ height: 10, background: '#0a0c10', borderRadius: 5, overflow: 'hidden', position: 'relative' }}>
          <div
            style={{
              height: '100%',
              width: `${fuelPct}%`,
              background: isFuelLow
                ? 'linear-gradient(90deg, #ef4444, #f87171)'
                : 'linear-gradient(90deg, #0284c7, #06b6d4)',
              transition: 'width 0.3s ease',
            }}
          />
          {/* Minimum fuel marker to finish race */}
          <div
            style={{
              position: 'absolute',
              left: `${Math.min(100, (minFuelNeededToFinish / capacityKg) * 100)}%`,
              top: 0,
              bottom: 0,
              width: 2,
              background: '#f59e0b',
              zIndex: 2,
            }}
            title={`Minimum fuel to finish: ${minFuelNeededToFinish.toFixed(1)} kg`}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b', marginTop: 3 }}>
          <span>Empty (0 kg)</span>
          <span style={{ color: '#f59e0b' }}>▲ Min to Finish ({minFuelNeededToFinish.toFixed(1)} kg)</span>
          <span>Full ({capacityKg} kg)</span>
        </div>
      </div>

      {/* Numerical Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, textAlign: 'center' }}>
        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>BURN / LAP</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>
            {burnRate.toFixed(2)} kg
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>FUEL RANGE</div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 13,
              fontWeight: 700,
              color: isFuelLow ? '#ef4444' : '#10b981',
            }}
          >
            {lapsRemaining.toFixed(1)} LAPS
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>WEIGHT LOSS</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: '#06b6d4' }}>
            +{(fuelKg * 0.033).toFixed(2)}s
          </div>
        </div>

        <div style={{ background: '#0a0c10', padding: '6px 4px', borderRadius: 4 }}>
          <div style={{ fontSize: 10, color: '#64748b' }}>PACE MODE</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 700, color: '#f59e0b' }}>
            {car?.pace_mode || 'NORMAL'}
          </div>
        </div>
      </div>
    </div>
  );
};
