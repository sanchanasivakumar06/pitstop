import React, { useEffect } from 'react';
import { useRaceStore } from './store/useRaceStore';
import { LeftPanel } from './components/LeftPanel';
import { RaceCanvas } from './canvas/RaceCanvas';
import { Timeline } from './components/Timeline';
import { ExplanationDrawer } from './components/ExplanationDrawer';
import { useKeyboard } from './hooks/useKeyboard';
import { usePlayback } from './hooks/usePlayback';
import { Flag, Activity, Radio } from 'lucide-react';

export const App: React.FC = () => {
  const { init, raceId, isOfflineMode, currentSnapshot } = useRaceStore();

  useKeyboard();
  usePlayback();

  useEffect(() => {
    init();
  }, [init]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', background: '#0a0c10' }}>
      {/* Top Header Bar */}
      <header
        style={{
          height: 48,
          background: '#12161f',
          borderBottom: '1px solid #262e3f',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 20px',
          zIndex: 20,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 18 }}>🏁</span>
          <h1 style={{ fontSize: 16, fontWeight: 700, letterSpacing: '0.5px', color: '#f8fafc' }}>
            THE IMPOSSIBLE PIT STOP <span style={{ color: '#06b6d4', fontWeight: 600 }}>// RACE STRATEGIST</span>
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {isOfflineMode ? (
            <span className="racing-badge" style={{ background: '#f59e0b', color: '#03141f' }}>
              OFFLINE DEMO MODE
            </span>
          ) : (
            <span className="racing-badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid #10b981' }}>
              <Radio size={12} /> LIVE SIMULATION ({raceId || 'CONNECTING'})
            </span>
          )}

          <div style={{ fontSize: 11, color: '#64748b' }}>
            Press <kbd style={{ background: '#222938', padding: '1px 5px', borderRadius: 3, color: '#f8fafc' }}>SPACE</kbd> Play/Pause | <kbd style={{ background: '#222938', padding: '1px 5px', borderRadius: 3, color: '#f8fafc' }}>I</kbd> Info
          </div>
        </div>
      </header>

      {/* Main Split Layout: 50% Dashboard (Left) and 50% Visualization (Right) */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* LEFT SIDE (50% width, scrollable details dashboard) */}
        <div style={{ width: '50%', minWidth: 0, height: '100%', overflow: 'hidden' }}>
          <LeftPanel />
        </div>

        {/* RIGHT SIDE (50% width: 2D Canvas Visualization + Timeline Scrubber) */}
        <div style={{ width: '50%', minWidth: 0, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <RaceCanvas />
          </div>
          <Timeline />
        </div>
      </div>

      {/* Math Explanation Popover Drawer */}
      <ExplanationDrawer />
    </div>
  );
};

export default App;
