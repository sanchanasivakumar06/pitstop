import React from 'react';
import { ControlPanel } from './ControlPanel';
import { FuelDashboard } from './FuelDashboard';
import { TyreCard } from './TyreCard';
import { PitStopPanel } from './PitStopPanel';
import { DecisionCard } from './DecisionCard';
import { WeatherBelief } from './WeatherBelief';
import { MetricsPanel } from './MetricsPanel';
import { Charts } from './Charts';
import { ComparisonView } from './ComparisonView';
import { EventLog } from './EventLog';
import { ConfigForm } from './ConfigForm';
import { Legend } from './Legend';
import { OfflineLoader } from './OfflineLoader';

export const LeftPanel: React.FC = () => {
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        background: '#0d1017',
        borderRight: '1px solid #262e3f',
      }}
    >
      {/* 1. Race Controls */}
      <ControlPanel />

      {/* 2. Fuel & Tyre Dashboard */}
      <FuelDashboard />
      <TyreCard />
      <PitStopPanel />

      {/* 3. Current Decision */}
      <DecisionCard />

      {/* 4. Weather & Belief */}
      <WeatherBelief />

      {/* 5. Live Metrics */}
      <MetricsPanel />

      {/* Live Charts */}
      <Charts />

      {/* 6. Strategy Comparison */}
      <ComparisonView />

      {/* 7. Event Log */}
      <EventLog />

      {/* Setup & Tools */}
      <ConfigForm />
      <Legend />
      <OfflineLoader />
    </div>
  );
};
