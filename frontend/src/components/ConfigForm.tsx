import React, { useState } from 'react';
import { Settings2, PlayCircle } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';

export const ConfigForm: React.FC = () => {
  const {
    tracks,
    strategies,
    scenarios,
    startNewRace,
    trackGeometry,
  } = useRaceStore();

  const [seed, setSeed] = useState(42);
  const [trackId, setTrackId] = useState('silverstone_classic');
  const [laps, setLaps] = useState(50);
  const [strategyId, setStrategyId] = useState('mdp_agent');
  const [scenarioName, setScenarioName] = useState('changing_weather');
  const [startFuel, setStartFuel] = useState(65);
  const [startTyre, setStartTyre] = useState('MEDIUM');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    startNewRace({
      seed,
      track_id: trackId,
      total_laps: laps,
      strategy_id: strategyId,
      scenario_name: scenarioName,
      start_fuel_kg: startFuel,
      start_tyre_compound: startTyre,
    });
  };

  return (
    <div className="racing-card">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <Settings2 size={16} color="#06b6d4" />
        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
          Race Configuration
        </h3>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {/* Strategy Selector */}
        <div>
          <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
            AI Strategy Algorithm
          </label>
          <select
            value={strategyId}
            onChange={(e) => setStrategyId(e.target.value)}
            style={{
              width: '100%',
              background: '#0a0c10',
              border: '1px solid #262e3f',
              color: '#f8fafc',
              padding: '6px 8px',
              borderRadius: 4,
              fontSize: 12,
              marginTop: 4,
            }}
          >
            {strategies.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.ai_concept?.split('(')[0]})
              </option>
            ))}
          </select>
        </div>

        {/* Scenario Preset */}
        <div>
          <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
            Scenario Condition Preset
          </label>
          <select
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            style={{
              width: '100%',
              background: '#0a0c10',
              border: '1px solid #262e3f',
              color: '#f8fafc',
              padding: '6px 8px',
              borderRadius: 4,
              fontSize: 12,
              marginTop: 4,
            }}
          >
            {scenarios.map((sc) => (
              <option key={sc.id} value={sc.id}>
                {sc.name}
              </option>
            ))}
          </select>
        </div>

        {/* Track & Laps */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 8 }}>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Track
            </label>
            <select
              value={trackId}
              onChange={(e) => setTrackId(e.target.value)}
              style={{
                width: '100%',
                background: '#0a0c10',
                border: '1px solid #262e3f',
                color: '#f8fafc',
                padding: '6px 8px',
                borderRadius: 4,
                fontSize: 12,
                marginTop: 4,
              }}
            >
              {tracks.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Laps
            </label>
            <input
              type="number"
              min={10}
              max={150}
              value={laps}
              onChange={(e) => setLaps(Number(e.target.value))}
              style={{
                width: '100%',
                background: '#0a0c10',
                border: '1px solid #262e3f',
                color: '#f8fafc',
                padding: '6px 8px',
                borderRadius: 4,
                fontSize: 12,
                marginTop: 4,
                fontFamily: 'var(--font-mono)',
              }}
            />
          </div>
        </div>

        {/* Start Fuel & Tyre */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Start Fuel (kg)
            </label>
            <input
              type="number"
              min={20}
              max={105}
              value={startFuel}
              onChange={(e) => setStartFuel(Number(e.target.value))}
              style={{
                width: '100%',
                background: '#0a0c10',
                border: '1px solid #262e3f',
                color: '#f8fafc',
                padding: '6px 8px',
                borderRadius: 4,
                fontSize: 12,
                marginTop: 4,
                fontFamily: 'var(--font-mono)',
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Start Tyre
            </label>
            <select
              value={startTyre}
              onChange={(e) => setStartTyre(e.target.value)}
              style={{
                width: '100%',
                background: '#0a0c10',
                border: '1px solid #262e3f',
                color: '#f8fafc',
                padding: '6px 8px',
                borderRadius: 4,
                fontSize: 12,
                marginTop: 4,
              }}
            >
              <option value="SOFT">SOFT (Red)</option>
              <option value="MEDIUM">MEDIUM (Yellow)</option>
              <option value="HARD">HARD (White)</option>
              <option value="INTERMEDIATE">INTER (Green)</option>
              <option value="WET">WET (Blue)</option>
            </select>
          </div>
        </div>

        {/* Seed & Launch */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', marginTop: 4 }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              RNG Seed
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              style={{
                width: '100%',
                background: '#0a0c10',
                border: '1px solid #262e3f',
                color: '#f8fafc',
                padding: '6px 8px',
                borderRadius: 4,
                fontSize: 12,
                marginTop: 4,
                fontFamily: 'var(--font-mono)',
              }}
            />
          </div>
          <button type="submit" className="btn-primary" style={{ padding: '7px 14px' }}>
            <PlayCircle size={16} /> New Race
          </button>
        </div>
      </form>
    </div>
  );
};
