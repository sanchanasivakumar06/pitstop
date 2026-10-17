import React from 'react';
import { CloudRain, Sun, CloudLightning } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';
import { InfoButton } from './InfoButton';

export const WeatherBelief: React.FC = () => {
  const { currentSnapshot } = useRaceStore();
  const weather = currentSnapshot?.weather;

  const belief = weather?.belief || { DRY: 0.9, LIGHT_RAIN: 0.08, HEAVY_RAIN: 0.02 };
  const trueState = weather?.true_state || 'DRY';
  const trackGrip = weather?.grip || 0.96;

  const states = [
    { key: 'DRY', label: 'Dry Track', color: '#10b981', icon: Sun },
    { key: 'LIGHT_RAIN', label: 'Light Rain / Drizzle', color: '#06b6d4', icon: CloudRain },
    { key: 'HEAVY_RAIN', label: 'Heavy Monsoon Rain', color: '#3b82f6', icon: CloudLightning },
  ];

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <CloudRain size={16} color="#06b6d4" />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Weather & Bayesian Belief
          </h3>
          <InfoButton explanationId="weather_belief" title="How is the weather belief updated?" />
        </div>
        <span className="racing-badge" style={{ background: '#222938', color: '#f8fafc' }}>
          TRUE: {trueState}
        </span>
      </div>

      <div style={{ fontSize: 11, color: '#94a3b8' }}>
        Sensor Grip Estimate: <strong style={{ color: '#f8fafc' }}>{(trackGrip * 100).toFixed(0)}%</strong>
        {' '}| HMM Forward Update Distribution:
      </div>

      {/* Probability Bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {states.map(({ key, label, color, icon: Icon }) => {
          const prob = belief[key] || 0.0;
          const pct = Math.round(prob * 100);

          return (
            <div key={key}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 3 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#cbd5e1' }}>
                  <Icon size={12} color={color} /> {label}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color }}>
                  {pct}% ({prob.toFixed(3)})
                </span>
              </div>
              <div style={{ height: 6, background: '#0a0c10', borderRadius: 3, overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${pct}%`,
                    background: color,
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
