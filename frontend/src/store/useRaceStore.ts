/**
 * Global Zustand Store for race telemetry, playback state, and explanations.
 */

import { create } from 'zustand';
import { Snapshot, TrackGeometry, ExplanationBlock } from '../types/snapshot';
import { RaceWebSocketClient } from '../api/socket';
import { fetchTracks, fetchStrategies, fetchScenarios, createRace, runEvaluation } from '../api/client';

interface RaceStoreState {
  raceId: string;
  currentLap: number;
  totalLaps: number;
  isPlaying: boolean;
  playbackSpeed: number;
  currentSnapshot: Snapshot | null;
  allSnapshots: Snapshot[];
  trackGeometry: TrackGeometry | null;
  animationProgress: number;

  // Metadata
  tracks: any[];
  strategies: any[];
  scenarios: any[];

  // Modal / Drawer state for "i" Info Buttons
  activeExplanation: ExplanationBlock | null;
  activeDrawerTab: 'explanation' | 'ranking' | 'comparison' | null;

  // Offline replay mode
  isOfflineMode: boolean;

  // Batch evaluation results
  evaluationResults: any | null;
  isEvaluating: boolean;

  // WebSocket
  wsClient: RaceWebSocketClient | null;

  // Actions
  init: () => Promise<void>;
  startNewRace: (config: any) => Promise<void>;
  play: () => void;
  pause: () => void;
  step: () => void;
  setSpeed: (speed: number) => void;
  seekLap: (lapIndex: number) => void;
  setExplanation: (expl: ExplanationBlock | null) => void;
  setDrawerTab: (tab: 'explanation' | 'ranking' | 'comparison' | null) => void;
  loadOfflineSnapshots: (snapshots: Snapshot[], track?: TrackGeometry) => void;
  executeBatchEvaluation: (payload: any) => Promise<void>;
}

export const useRaceStore = create<RaceStoreState>((set, get) => ({
  raceId: '',
  currentLap: 0,
  totalLaps: 50,
  isPlaying: false,
  playbackSpeed: 1.0,
  currentSnapshot: null,
  allSnapshots: [],
  trackGeometry: null,
  animationProgress: 0.0,

  tracks: [],
  strategies: [],
  scenarios: [],

  activeExplanation: null,
  activeDrawerTab: null,
  isOfflineMode: false,

  evaluationResults: null,
  isEvaluating: false,
  wsClient: null,

  init: async () => {
    try {
      const [tracks, strats, scens] = await Promise.all([
        fetchTracks(),
        fetchStrategies(),
        fetchScenarios(),
      ]);
      set({
        tracks,
        strategies: strats,
        scenarios: scens,
        trackGeometry: tracks[0] || null,
      });

      // Automatically launch default race
      await get().startNewRace({
        seed: 42,
        track_id: tracks[0]?.id || 'silverstone_classic',
        total_laps: 50,
        strategy_id: 'mdp_agent',
        scenario_name: 'changing_weather',
      });
    } catch (e) {
      console.warn('Backend not available, running in offline fallback mode:', e);
      set({ isOfflineMode: true });
    }
  },

  startNewRace: async (config: any) => {
    try {
      get().wsClient?.disconnect();
      const res = await createRace(config);
      const newRaceId = res.race_id;

      // Select track geometry
      const track = get().tracks.find((t) => t.id === config.track_id) || get().tracks[0];

      set({
        raceId: newRaceId,
        totalLaps: config.total_laps || 50,
        currentLap: 0,
        allSnapshots: [],
        currentSnapshot: null,
        animationProgress: 0.0,
        isPlaying: false,
        isOfflineMode: false,
        trackGeometry: track,
      });

      // Initialize WebSocket streaming
      const ws = new RaceWebSocketClient((data) => {
        if (data.type === 'init') {
          set({ trackGeometry: data.track, totalLaps: data.total_laps });
        } else if (data.type === 'lap_snapshot') {
          const snap: Snapshot = data.snapshot;
          set((state) => ({
            currentSnapshot: snap,
            currentLap: snap.lap,
            animationProgress: 0.0,
            allSnapshots: [...state.allSnapshots, snap],
          }));
        } else if (data.type === 'tick') {
          set({ animationProgress: data.progress });
        } else if (data.type === 'finished') {
          set({ isPlaying: false });
        }
      });

      ws.connect(newRaceId);
      set({ wsClient: ws });
    } catch (err) {
      console.error('Failed to start race:', err);
    }
  },

  play: () => {
    const { isOfflineMode, allSnapshots, currentLap } = get();
    if (isOfflineMode) {
      set({ isPlaying: true });
      return;
    }
    get().wsClient?.send('play');
    set({ isPlaying: true });
  },

  pause: () => {
    const { isOfflineMode } = get();
    if (isOfflineMode) {
      set({ isPlaying: false });
      return;
    }
    get().wsClient?.send('pause');
    set({ isPlaying: false });
  },

  step: () => {
    const { isOfflineMode, allSnapshots, currentLap } = get();
    if (isOfflineMode) {
      const nextIndex = currentLap;
      if (nextIndex < allSnapshots.length) {
        set({
          currentSnapshot: allSnapshots[nextIndex],
          currentLap: nextIndex + 1,
          animationProgress: 0.0,
        });
      }
      return;
    }
    get().wsClient?.send('step');
  },

  setSpeed: (speed: number) => {
    set({ playbackSpeed: speed });
    get().wsClient?.send('speed', speed);
  },

  seekLap: (lapIndex: number) => {
    const { allSnapshots } = get();
    if (lapIndex >= 0 && lapIndex < allSnapshots.length) {
      set({
        currentSnapshot: allSnapshots[lapIndex],
        currentLap: lapIndex + 1,
        animationProgress: 0.0,
      });
    }
  },

  setExplanation: (expl: ExplanationBlock | null) => {
    set({ activeExplanation: expl, activeDrawerTab: expl ? 'explanation' : null });
  },

  setDrawerTab: (tab: 'explanation' | 'ranking' | 'comparison' | null) => {
    set({ activeDrawerTab: tab });
  },

  loadOfflineSnapshots: (snapshots: Snapshot[], track?: TrackGeometry) => {
    if (!snapshots || snapshots.length === 0) return;
    set({
      isOfflineMode: true,
      isPlaying: false,
      allSnapshots: snapshots,
      currentSnapshot: snapshots[0],
      currentLap: 1,
      totalLaps: snapshots[0].total_laps || snapshots.length,
      trackGeometry: track || get().trackGeometry,
    });
  },

  executeBatchEvaluation: async (payload: any) => {
    set({ isEvaluating: true });
    try {
      const results = await runEvaluation(payload);
      set({ evaluationResults: results, isEvaluating: false, activeDrawerTab: 'comparison' });
    } catch (e) {
      console.error('Batch evaluation failed:', e);
      set({ isEvaluating: false });
    }
  },
}));
