import React from 'react';
import { Play, Pause, SkipForward, RotateCcw, FastForward } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';

export const ControlPanel: React.FC = () => {
  const {
    isPlaying,
    playbackSpeed,
    currentLap,
    totalLaps,
    isOfflineMode,
    play,
    pause,
    step,
    setSpeed,
    startNewRace,
    trackGeometry,
  } = useRaceStore();

  const handleReset = () => {
    startNewRace({
      seed: 42,
      track_id: trackGeometry?.id || 'silverstone_classic',
      total_laps: totalLaps,
      strategy_id: 'mdp_agent',
      scenario_name: 'changing_weather',
    });
  };

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>Race Controls</h3>
          {isOfflineMode && (
            <span className="racing-badge" style={{ background: '#f59e0b', color: '#181d28' }}>
              OFFLINE REPLAY
            </span>
          )}
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: '#06b6d4', fontWeight: 700 }}>
          LAP {currentLap} / {totalLaps}
        </div>
      </div>

      {/* Main Buttons */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        {isPlaying ? (
          <button onClick={pause} className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
            <Pause size={16} /> PAUSE
          </button>
        ) : (
          <button onClick={play} className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
            <Play size={16} /> PLAY
          </button>
        )}

        <button onClick={step} className="btn-secondary" title="Step one single lap" style={{ padding: '8px 12px' }}>
          <SkipForward size={16} /> STEP
        </button>

        <button onClick={handleReset} className="btn-secondary" title="Reset race" style={{ padding: '8px 12px' }}>
          <RotateCcw size={16} />
        </button>
      </div>

      {/* Speed Slider Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
        <span style={{ fontSize: 12, color: '#94a3b8' }}>Playback Speed:</span>
        <div style={{ display: 'flex', gap: 4 }}>
          {[0.25, 0.5, 1, 2].map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              style={{
                background: playbackSpeed === s ? '#06b6d4' : '#222938',
                color: playbackSpeed === s ? '#03141f' : '#cbd5e1',
                border: 'none',
                borderRadius: 4,
                padding: '3px 8px',
                fontSize: 11,
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
