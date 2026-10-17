import React from 'react';
import { ListFilter, AlertCircle, Wrench, CloudRain } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';

export const EventLog: React.FC = () => {
  const { allSnapshots, seekLap } = useRaceStore();

  const events = allSnapshots
    .slice()
    .reverse()
    .filter((s) => s.events?.length > 0 || s.decision?.action !== 'STAY_OUT');

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <ListFilter size={16} color="#06b6d4" />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
            Tactical Decision & Event Log
          </h3>
        </div>
        <span style={{ fontSize: 11, color: '#64748b' }}>
          {events.length} Entries
        </span>
      </div>

      <div
        style={{
          maxHeight: 180,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
          paddingRight: 4,
        }}
      >
        {events.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#64748b', fontSize: 11, padding: 12 }}>
            No major race incidents or strategic pit decisions yet.
          </div>
        ) : (
          events.map((s, idx) => {
            const didPit = s.decision?.action !== 'STAY_OUT';
            const isReplan = s.events?.includes('replan');
            const isRain = s.events?.some((e) => e.startsWith('weather_change'));
            const isSC = s.events?.some((e) => e.startsWith('safety_car'));

            return (
              <div
                key={idx}
                onClick={() => seekLap(s.lap - 1)}
                style={{
                  background: didPit ? 'rgba(6, 182, 212, 0.08)' : '#0a0c10',
                  borderLeft: didPit
                    ? '3px solid #06b6d4'
                    : isSC
                    ? '3px solid #eab308'
                    : '3px solid #334155',
                  borderRadius: 4,
                  padding: '6px 10px',
                  cursor: 'pointer',
                  transition: 'background 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 700, color: '#f8fafc' }}>
                      LAP {s.lap}
                    </span>
                    {didPit && (
                      <span className="racing-badge" style={{ background: '#06b6d4', color: '#03141f', fontSize: 9 }}>
                        {s.decision.action}
                      </span>
                    )}
                    {isReplan && (
                      <span className="racing-badge" style={{ background: '#f59e0b', color: '#03141f', fontSize: 9 }}>
                        REPLAN
                      </span>
                    )}
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#64748b' }}>
                    {s.sim_time.toFixed(1)}s
                  </span>
                </div>
                <div style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.3 }}>
                  {s.decision?.reason || s.events.join(', ')}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
