import React, { useRef } from 'react';
import { Upload, FileText } from 'lucide-react';
import { useRaceStore } from '../store/useRaceStore';

export const OfflineLoader: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { loadOfflineSnapshots, isOfflineMode } = useRaceStore();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result as string;
        const parsed = JSON.parse(text);
        const snapshots = Array.isArray(parsed) ? parsed : parsed.snapshots;
        if (snapshots && snapshots.length > 0) {
          loadOfflineSnapshots(snapshots);
        }
      } catch (err) {
        alert('Invalid snapshots.json file format');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="racing-card" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Upload size={14} color="#06b6d4" />
          <h4 style={{ fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>
            Offline Replay Mode
          </h4>
        </div>
        {isOfflineMode && (
          <span className="racing-badge" style={{ background: '#f59e0b', color: '#03141f', fontSize: 10 }}>
            ACTIVE
          </span>
        )}
      </div>

      <p style={{ fontSize: 11, color: '#94a3b8' }}>
        Load an exported <code>snapshots.json</code> file to scrub, inspect, and evaluate full telemetry offline.
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        className="btn-secondary"
        style={{ fontSize: 12, justifyContent: 'center' }}
      >
        <FileText size={14} /> Upload snapshots.json
      </button>
    </div>
  );
};
