import React from 'react';
import { useRaceStore } from '../store/useRaceStore';
import { Wrench, CloudRain, AlertTriangle } from 'lucide-react';

export const Timeline: React.FC = () => {
  const { allSnapshots, currentLap, totalLaps, seekLap } = useRaceStore();

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const targetLap = Number(e.target.value);
    seekLap(targetLap - 1);
  };

  return (
    <div
      style={{
        background: '#12161f',
        borderTop: '1px solid #262e3f',
        padding: '10px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
        <span style={{ color: '#94a3b8', fontWeight: 600 }}>RACE TIMELINE & LAP SCRUBBER</span>
        <span style={{ fontFamily: 'var(--font-mono)', color: '#06b6d4', fontWeight: 700 }}>
          LAP {currentLap} OF {totalLaps}
        </span>
      </div>

      {/* Scrubber slider and event markers */}
      <div style={{ position: 'relative', width: '100%', height: 26, display: 'flex', alignItems: 'center' }}>
        {/* Event Markers Overlay */}
        <div style={{ position: 'absolute', left: 0, right: 0, height: 16, pointerEvents: 'none' }}>
          {allSnapshots.map((s, idx) => {
            const pct = (idx / (totalLaps || 1)) * 100;
            const hadPit = s.pit?.in_progress;
            const hadSC = s.events?.some((e) => e.startsWith('safety_car'));
            const hadWeather = s.events?.some((e) => e.startsWith('weather_change'));

            if (!hadPit && !hadSC && !hadWeather) return null;

            return (
              <div
                key={idx}
                style={{
                  position: 'absolute',
                  left: `${pct}%`,
                  top: -2,
                  transform: 'translateX(-50%)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                {hadPit && (
                  <span style={{ color: '#06b6d4' }} title={`Lap ${s.lap}: Pit Stop`}>
                    ●
                  </span>
                )}
                {hadSC && (
                  <span style={{ color: '#eab308' }} title={`Lap ${s.lap}: Safety Car`}>
                    ▲
                  </span>
                )}
                {hadWeather && (
                  <span style={{ color: '#3b82f6' }} title={`Lap ${s.lap}: Weather Change`}>
                    ◆
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* Input Range */}
        <input
          type="range"
          min={1}
          max={Math.max(1, allSnapshots.length || totalLaps)}
          value={currentLap || 1}
          onChange={handleSliderChange}
          style={{
            width: '100%',
            accentColor: '#06b6d4',
            cursor: 'pointer',
            height: 6,
            background: '#222938',
            borderRadius: 3,
            zIndex: 5,
          }}
        />
      </div>

      {/* Markers Legend */}
      <div style={{ display: 'flex', gap: 14, fontSize: 10, color: '#64748b' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ color: '#06b6d4' }}>●</span> Pit Stop
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ color: '#eab308' }}>▲</span> Safety Car
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ color: '#3b82f6' }}>◆</span> Weather Transition
        </span>
      </div>
    </div>
  );
};
