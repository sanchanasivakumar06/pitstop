import React, { useRef, useEffect, useState } from 'react';
import { useRaceStore } from '../store/useRaceStore';
import { RaceRenderer } from './renderer';
import { Ghost, Eye, EyeOff } from 'lucide-react';

export const RaceCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const rendererRef = useRef<RaceRenderer>(new RaceRenderer());
  const [showGhost, setShowGhost] = useState(true);

  const {
    currentSnapshot,
    trackGeometry,
    isPlaying,
    animationProgress,
  } = useRaceStore();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    rendererRef.current.init(canvas.width, canvas.height);

    let animationFrameId: number;

    const renderLoop = () => {
      if (trackGeometry) {
        rendererRef.current.render(
          ctx,
          trackGeometry,
          currentSnapshot,
          animationProgress,
          showGhost
        );
      }
      animationFrameId = requestAnimationFrame(renderLoop);
    };

    animationFrameId = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(animationFrameId);
  }, [trackGeometry, currentSnapshot, animationProgress, showGhost]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Top Canvas HUD overlay */}
      <div
        style={{
          position: 'absolute',
          top: 12,
          left: 16,
          right: 16,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          pointerEvents: 'none',
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <span className="racing-badge" style={{ background: 'rgba(6, 182, 212, 0.2)', color: '#06b6d4', border: '1px solid #06b6d4' }}>
            CIRCUIT: {trackGeometry?.name || 'Silverstone Classic'}
          </span>
          <span className="racing-badge" style={{ background: 'rgba(15, 23, 42, 0.8)', color: '#f8fafc', border: '1px solid #334155' }}>
            TRACK TEMP: {currentSnapshot?.weather?.track_temp_c.toFixed(1) || 28.0}°C
          </span>
          <span className="racing-badge" style={{ background: 'rgba(15, 23, 42, 0.8)', color: '#f8fafc', border: '1px solid #334155' }}>
            GRIP: {((currentSnapshot?.weather?.grip || 0.95) * 100).toFixed(0)}%
          </span>
        </div>

        {/* Ghost toggle */}
        <button
          onClick={() => setShowGhost(!showGhost)}
          className="btn-secondary"
          style={{ pointerEvents: 'auto', padding: '4px 10px', fontSize: 12 }}
          title="Toggle baseline ghost car comparison"
        >
          <Ghost size={14} color={showGhost ? '#06b6d4' : '#64748b'} />
          {showGhost ? 'Ghost ON' : 'Ghost OFF'}
        </button>
      </div>

      {/* 2D Race Canvas */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#07090e' }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={500}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
            borderRadius: 8,
            boxShadow: '0 8px 30px rgba(0,0,0,0.6)',
          }}
        />
      </div>
    </div>
  );
};
