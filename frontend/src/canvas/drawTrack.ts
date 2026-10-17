/**
 * Track rendering module.
 * Draws racetrack asphalt, borders, red/white kerbs, and checkered start/finish line.
 * Uses an offscreen canvas for high performance 60 FPS caching.
 */

import { Point2D, TrackGeometry } from '../types/snapshot';
import { COLORS } from './colors';

export function createStaticTrackCanvas(
  track: TrackGeometry,
  width: number,
  height: number
): HTMLCanvasElement {
  const offscreen = document.createElement('canvas');
  offscreen.width = width;
  offscreen.height = height;
  const ctx = offscreen.getContext('2d');
  if (!ctx) return offscreen;

  const pts = track.centerline;
  if (!pts || pts.length < 3) return offscreen;

  // 1. Draw outer asphalt runoffs / background gravel
  ctx.save();

  // 2. Draw Kerbs (red and white dashes underneath the asphalt border)
  ctx.lineWidth = 44;
  ctx.strokeStyle = COLORS.kerbRed;
  ctx.setLineDash([18, 18]);
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    ctx.lineTo(pts[i].x, pts[i].y);
  }
  ctx.closePath();
  ctx.stroke();

  ctx.strokeStyle = COLORS.kerbWhite;
  ctx.lineDashOffset = 18;
  ctx.stroke();
  ctx.setLineDash([]);

  // 3. Draw Main Asphalt Surface
  ctx.lineWidth = 36;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.strokeStyle = COLORS.asphalt;
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    ctx.lineTo(pts[i].x, pts[i].y);
  }
  ctx.closePath();
  ctx.stroke();

  // 4. Track inner and outer guide lines
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)';
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    ctx.lineTo(pts[i].x, pts[i].y);
  }
  ctx.closePath();
  ctx.stroke();

  // 5. Start / Finish Line (checkered stripe)
  if (pts.length > 0) {
    const p0 = pts[0];
    const p1 = pts[1];
    const angle = Math.atan2(p1.y - p0.y, p1.x - p0.x) + Math.PI / 2;

    ctx.save();
    ctx.translate(p0.x, p0.y);
    ctx.rotate(angle);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-18, -3, 36, 6);
    ctx.fillStyle = '#000000';
    for (let x = -18; x < 18; x += 6) {
      ctx.fillRect(x, -3, 3, 3);
      ctx.fillRect(x + 3, 0, 3, 3);
    }
    ctx.restore();
  }

  ctx.restore();
  return offscreen;
}
