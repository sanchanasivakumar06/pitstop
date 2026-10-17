import React, { useState } from 'react';
import { LineChart, BarChart2 } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';

type ChartTab = 'fuel' | 'wear' | 'laptime' | 'weather';

export const Charts: React.FC = () => {
  const { allSnapshots } = useRaceStore();
  const [activeTab, setActiveTab] = useState<ChartTab>('fuel');

  if (allSnapshots.length < 2) {
    return (
      <div className="racing-card" style={{ textAlign: 'center', padding: '20px 10px', color: '#64748b' }}>
        <LineChart size={24} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
        <p style={{ fontSize: 12 }}>Run or step laps to accumulate live telemetry curves</p>
      </div>
    );
  }

  const laps = allSnapshots.map((s) => s.lap);
  const width = 360;
  const height = 110;
  const padding = 20;

  // Render SVG polyline paths
  const renderPath = (data: number[], color: string, minVal?: number, maxVal?: number) => {
    const min = minVal ?? Math.min(...data);
    const max = maxVal ?? Math.max(...data);
    const range = max - min || 1;

    const points = data.map((val, idx) => {
      const x = padding + (idx / (data.length - 1 || 1)) * (width - 2 * padding);
      const y = height - padding - ((val - min) / range) * (height - 2 * padding);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    return (
      <g>
        <polyline fill="none" stroke={color} strokeWidth="2" points={points.join(' ')} />
        {/* Fill area below curve */}
        <polygon
          fill={`${color}18`}
          points={`${padding},${height - padding} ${points.join(' ')} ${width - padding},${height - padding}`}
        />
      </g>
    );
  };

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {/* Header with Tab Selectors */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: '#f8fafc' }}>Telemetry Trends</h3>
        <div style={{ display: 'flex', gap: 4 }}>
          {[
            { id: 'fuel', label: 'Fuel' },
            { id: 'wear', label: 'Tyre' },
            { id: 'laptime', label: 'Pace' },
            { id: 'weather', label: 'Rain' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ChartTab)}
              style={{
                background: activeTab === tab.id ? '#06b6d4' : '#222938',
                color: activeTab === tab.id ? '#03141f' : '#94a3b8',
                border: 'none',
                borderRadius: 4,
                padding: '2px 6px',
                fontSize: 10,
                fontFamily: 'var(--font-mono)',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Canvas Chart */}
      <div style={{ background: '#0a0c10', borderRadius: 6, padding: '6px 0', border: '1px solid #262e3f' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
          {/* Subtle grid lines */}
          <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke="#1e293b" strokeDasharray="2,2" />
          <line x1={padding} y1={height / 2} x2={width - padding} y2={height / 2} stroke="#1e293b" strokeDasharray="2,2" />
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#334155" />

          {/* Active Metric Path */}
          {activeTab === 'fuel' && renderPath(allSnapshots.map((s) => s.car.fuel_kg), '#06b6d4')}
          {activeTab === 'wear' && renderPath(allSnapshots.map((s) => s.car.tyre.wear_pct), '#ef4444', 0, 100)}
          {activeTab === 'laptime' && renderPath(allSnapshots.map((s) => s.car.last_lap_time), '#f59e0b')}
          {activeTab === 'weather' && renderPath(allSnapshots.map((s) => s.weather.belief.HEAVY_RAIN + s.weather.belief.LIGHT_RAIN), '#3b82f6', 0, 1)}
        </svg>

        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0 20px', fontSize: 9, color: '#64748b', fontFamily: 'var(--font-mono)' }}>
          <span>Lap 1</span>
          <span>
            Current: {activeTab === 'fuel' && `${allSnapshots[allSnapshots.length - 1].car.fuel_kg.toFixed(1)} kg`}
            {activeTab === 'wear' && `${allSnapshots[allSnapshots.length - 1].car.tyre.wear_pct.toFixed(1)}% wear`}
            {activeTab === 'laptime' && `${allSnapshots[allSnapshots.length - 1].car.last_lap_time.toFixed(1)}s`}
            {activeTab === 'weather' && `${((allSnapshots[allSnapshots.length - 1].weather.belief.HEAVY_RAIN + allSnapshots[allSnapshots.length - 1].weather.belief.LIGHT_RAIN) * 100).toFixed(0)}% rain risk`}
          </span>
          <span>Lap {laps[laps.length - 1]}</span>
        </div>
      </div>
    </div>
  );
};
