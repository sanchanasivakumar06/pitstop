import React from 'react';
import { HelpCircle } from 'lucide-react';
import { COLORS } from '../canvas/colors';

export const Legend: React.FC = () => {
  return (
    <div className="racing-card" style={{ fontSize: 11, color: '#94a3b8' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <HelpCircle size={14} color="#06b6d4" />
        <strong style={{ color: '#f8fafc' }}>Sim Key & Tyre Compounds</strong>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6, textAlign: 'center' }}>
        <div style={{ background: '#0a0c10', padding: '4px', borderRadius: 4 }}>
          <span style={{ color: COLORS.tyreSoft, fontWeight: 700 }}>● SOFT</span>
          <div style={{ fontSize: 9, color: '#64748b' }}>Dry Fast</div>
        </div>
        <div style={{ background: '#0a0c10', padding: '4px', borderRadius: 4 }}>
          <span style={{ color: COLORS.tyreMedium, fontWeight: 700 }}>● MEDIUM</span>
          <div style={{ fontSize: 9, color: '#64748b' }}>Balanced</div>
        </div>
        <div style={{ background: '#0a0c10', padding: '4px', borderRadius: 4 }}>
          <span style={{ color: COLORS.tyreHard, fontWeight: 700 }}>● HARD</span>
          <div style={{ fontSize: 9, color: '#64748b' }}>Durable</div>
        </div>
        <div style={{ background: '#0a0c10', padding: '4px', borderRadius: 4 }}>
          <span style={{ color: COLORS.tyreInter, fontWeight: 700 }}>● INTER</span>
          <div style={{ fontSize: 9, color: '#64748b' }}>Damp/Light</div>
        </div>
        <div style={{ background: '#0a0c10', padding: '4px', borderRadius: 4 }}>
          <span style={{ color: COLORS.tyreWet, fontWeight: 700 }}>● WET</span>
          <div style={{ fontSize: 9, color: '#64748b' }}>Heavy Rain</div>
        </div>
      </div>
    </div>
  );
};
