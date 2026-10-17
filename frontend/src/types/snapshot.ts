/**
 * Snapshot & Simulation Schema Types.
 * Exact mirror of the backend Pydantic models.
 */

export interface TyreSnapshot {
  compound: string;
  age_laps: int_or_number;
  wear_pct: number;
  grip_pct: number;
  temp_c: number;
}

export interface CarSnapshot {
  progress: number;
  speed_kmh: number;
  fuel_kg: number;
  fuel_capacity_kg: number;
  fuel_per_lap: number;
  fuel_laps_remaining: number;
  tyre: TyreSnapshot;
  pace_mode: 'PUSH' | 'NORMAL' | 'CONSERVE';
  position: number;
  gap_ahead_s: number;
  gap_behind_s: number;
  last_lap_time: number;
  best_lap_time: number;
  total_time: number;
}

export interface RivalSnapshot {
  id: string;
  progress: number;
  position: number;
  tyre: string;
  color: string;
}

export interface WeatherSnapshot {
  true_state: string;
  belief: {
    DRY: number;
    LIGHT_RAIN: number;
    HEAVY_RAIN: number;
    [key: string]: number;
  };
  track_temp_c: number;
  grip: number;
}

export interface PitSnapshot {
  in_progress: boolean;
  stage: 'ENTRY' | 'BOX_STOP' | 'TYRE_CHANGE' | 'REFUEL' | 'EXIT' | 'NONE';
  stage_progress: number;
  planned_next_pit_lap: number | null;
  stops_done: number;
  time_loss_s: number;
}

export interface ExplanationBlock {
  id: string;
  title: string;
  formula: string;
  inputs: Record<string, any>;
  steps: string[];
  result: string;
  plain_english: string;
}

export interface DecisionSnapshot {
  action: string;
  reason: string;
  utilities: Record<string, number>;
  q_values: Record<string, number>;
  replanned: boolean;
  explanation: ExplanationBlock[];
}

export interface MetricsSnapshot {
  total_time: number;
  pit_stops: number;
  replans: number;
  fuel_used: number;
  avg_lap_time: number;
}

export interface Snapshot {
  lap: number;
  total_laps: number;
  sim_time: number;
  phase: 'RACING' | 'PIT_ENTRY' | 'PIT_BOX' | 'PIT_EXIT' | 'SAFETY_CAR' | 'FINISHED';
  car: CarSnapshot;
  rivals: RivalSnapshot[];
  weather: WeatherSnapshot;
  pit: PitSnapshot;
  decision: DecisionSnapshot;
  events: string[];
  metrics: MetricsSnapshot;
}

export interface Point2D {
  x: number;
  y: number;
}

export interface TrackGeometry {
  id: string;
  name: string;
  length_km: number;
  corners: number;
  base_lap_time_s: number;
  pit_lane_loss_s: number;
  default_laps: number;
  pit_entry_progress: number;
  pit_box_progress: number;
  pit_exit_progress: number;
  centerline: Point2D[];
  pit_lane: Point2D[];
}

type int_or_number = number;
