/**
 * Layered 2D Canvas Orchestrator.
 * Coordinates static background caching, vehicle movement interpolation, pit stop animation,
 * weather particles, and overlay rendering at 60 FPS.
 */

import { Snapshot, TrackGeometry, Point2D } from '../types/snapshot';
import { createStaticTrackCanvas } from './drawTrack';
import { drawPitLane } from './drawPitLane';
import { drawCarShape } from './drawCar';
import { drawPitStopChoreography } from './drawPitStop';
import { drawWeatherAndCautionOverlays } from './drawWeather';
import { updateAndDrawTyreTrail, drawGhostBaselineCar } from './effects';
import { COLORS } from './colors';

export class RaceRenderer {
  private staticTrackCanvas: HTMLCanvasElement | null = null;
  private currentTrackId: string = '';
  private width: number = 800;
  private height: number = 500;

  public init(width: number, height: number): void {
    this.width = width;
    this.height = height;
  }

  public render(
    ctx: CanvasRenderingContext2D,
    track: TrackGeometry,
    snapshot: Snapshot | null,
    subLapProgress: number,
    showGhost: boolean = true
  ): void {
    if (!track) return;

    // Cache static track layer on first render or when track changes
    if (!this.staticTrackCanvas || this.currentTrackId !== track.id) {
      this.staticTrackCanvas = createStaticTrackCanvas(track, this.width, this.height);
      this.currentTrackId = track.id;
    }

    // 1. Clear & Draw Pre-rendered Track
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.drawImage(this.staticTrackCanvas, 0, 0);

    // 2. Draw Pit Lane & Boxes
    drawPitLane(ctx, track);

    if (!snapshot) return;

    const inPit = snapshot.pit?.in_progress;
    const pts = inPit ? track.pit_lane : track.centerline;
    const progress = inPit ? (snapshot.pit?.stage_progress || 0.5) : subLapProgress;

    // 3. Interpolate Car Position
    const carPos = this.interpolatePolyline(pts, progress);

    // 4. Draw Tyre Degradation Trail
    if (!inPit) {
      updateAndDrawTyreTrail(ctx, carPos.x, carPos.y, snapshot.car.tyre.wear_pct);
    }

    // 5. Draw Ghost Baseline Car (simulating baseline lagging slightly behind)
    if (showGhost && !inPit && track.centerline.length > 0) {
      const ghostProg = Math.max(0.0, (subLapProgress - 0.035) % 1.0);
      const ghostPos = this.interpolatePolyline(track.centerline, ghostProg);
      drawGhostBaselineCar(ctx, ghostPos.x, ghostPos.y, ghostPos.heading);
    }

    // 6. Draw Rivals
    if (snapshot.rivals) {
      for (const rival of snapshot.rivals) {
        const rivProg = (subLapProgress + (rival.position * 0.05)) % 1.0;
        const rivPos = this.interpolatePolyline(track.centerline, rivProg);
        drawCarShape(
          ctx,
          rivPos.x,
          rivPos.y,
          rivPos.heading,
          rival.color || COLORS.carRival1,
          rival.tyre || 'MEDIUM',
          `P${rival.position}`,
          false
        );
      }
    }

    // 7. Draw Player Car or Pit Stop Choreography
    if (inPit) {
      // Car is stationary in pit box
      const boxIdx = Math.floor(track.pit_lane.length / 2);
      const boxPt = track.pit_lane[boxIdx] || carPos;
      drawCarShape(
        ctx,
        boxPt.x,
        boxPt.y,
        0,
        COLORS.carPlayer,
        snapshot.car.tyre.compound,
        `P${snapshot.car.position}`,
        true
      );
      drawPitStopChoreography(
        ctx,
        boxPt.x,
        boxPt.y,
        snapshot.pit.stage,
        snapshot.pit.stage_progress,
        snapshot.car.tyre.compound,
        snapshot.decision?.action ? 32 : 0,
        snapshot.pit.time_loss_s
      );
    } else {
      drawCarShape(
        ctx,
        carPos.x,
        carPos.y,
        carPos.heading,
        COLORS.carPlayer,
        snapshot.car.tyre.compound,
        `P${snapshot.car.position}`,
        true
      );
    }

    // 8. Weather & Safety Car Overlays
    const isSC = snapshot.phase === 'SAFETY_CAR' || snapshot.events?.some((e) => e.startsWith('safety_car'));
    const isVSC = snapshot.events?.some((e) => e.startsWith('vsc'));
    drawWeatherAndCautionOverlays(
      ctx,
      this.width,
      this.height,
      snapshot.weather?.true_state || 'DRY',
      isSC,
      isVSC
    );
  }

  private interpolatePolyline(
    points: Point2D[],
    progress: number
  ): { x: number; y: number; heading: number } {
    if (!points || points.length === 0) return { x: 400, y: 250, heading: 0 };
    if (points.length === 1) return { x: points[0].x, y: points[0].y, heading: 0 };

    const n = points.length;
    const t = Math.abs(progress % 1.0);
    const raw = t * n;
    const idx = Math.floor(raw) % n;
    const frac = raw - Math.floor(raw);

    const p0 = points[idx];
    const p1 = points[(idx + 1) % n];

    const x = p0.x + frac * (p1.x - p0.x);
    const y = p0.y + frac * (p1.y - p0.y);

    const dx = p1.x - p0.x;
    const dy = p1.y - p0.y;
    const heading = Math.atan2(dy, dx);

    return { x, y, heading };
  }
}
