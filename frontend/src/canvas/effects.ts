/**
 * Dynamic visual effects: Tyre wear trailing particles, ghost baseline car marker, and puncture warnings.
 */

import { Point2D } from '../types/snapshot';
import { COLORS } from './colors';

interface TrailPoint {
  x: number;
  y: number;
  alpha: number;
  color: string;
}

const tyreTrail: TrailPoint[] = [];

export function updateAndDrawTyreTrail(
  ctx: CanvasRenderingContext2D,
  currentX: number,
  currentY: number,
  wearPct: number
): void {
  // Determine trail color based on wear %
  let color = 'rgba(6, 182, 212, ';   // Fresh: cyan
  if (wearPct > 65.0) {
    color = 'rgba(239, 68, 68, ';    // Past cliff: red
  } else if (wearPct > 45.0) {
    color = 'rgba(234, 179, 8, ';    // Worn: amber
  }

  // Push new point
  tyreTrail.push({ x: currentX, y: currentY, alpha: 0.6, color });

  // Draw and fade trail
  ctx.save();
  for (let i = tyreTrail.length - 1; i >= 0; i--) {
    const p = tyreTrail[i];
    p.alpha -= 0.035;
    if (p.alpha <= 0) {
      tyreTrail.splice(i, 1);
      continue;
    }
    ctx.fillStyle = `${p.color}${p.alpha})`;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

export function drawGhostBaselineCar(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  headingRad: number
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(headingRad);

  // Translucent ghost silhouette
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.45)';
  ctx.fillStyle = 'rgba(148, 163, 184, 0.18)';
  ctx.lineWidth = 1;
  ctx.setLineDash([3, 3]);

  ctx.beginPath();
  ctx.roundRect(-12, -7, 24, 14, 3);
  ctx.fill();
  ctx.stroke();

  ctx.restore();

  // Ghost label
  ctx.save();
  ctx.translate(x, y + 16);
  ctx.font = '8px "JetBrains Mono", monospace';
  ctx.fillStyle = 'rgba(148, 163, 184, 0.7)';
  ctx.textAlign = 'center';
  ctx.fillText('BASELINE GHOST', 0, 0);
  ctx.restore();
}
