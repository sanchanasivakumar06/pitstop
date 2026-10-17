/**
 * Pit lane and pit box rendering module.
 * Draws pit lane asphalt, pit wall, pit speed limiter entry/exit line, and pit boxes.
 */

import { Point2D, TrackGeometry } from '../types/snapshot';
import { COLORS } from './colors';

export function drawPitLane(
  ctx: CanvasRenderingContext2D,
  track: TrackGeometry
): void {
  const pitPts = track.pit_lane;
  if (!pitPts || pitPts.length < 2) return;

  ctx.save();

  // 1. Pit lane surface
  ctx.lineWidth = 22;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.strokeStyle = COLORS.pitAsphalt;
  ctx.beginPath();
  ctx.moveTo(pitPts[0].x, pitPts[0].y);
  for (let i = 1; i < pitPts.length; i++) {
    ctx.lineTo(pitPts[i].x, pitPts[i].y);
  }
  ctx.stroke();

  // 2. Pit lane boundary line (solid yellow border)
  ctx.lineWidth = 2;
  ctx.strokeStyle = COLORS.pitBorder;
  ctx.stroke();

  // 3. Pit Box / Service Area (at midpoint of pit lane)
  const boxIdx = Math.floor(pitPts.length / 2);
  const boxPt = pitPts[boxIdx];

  ctx.save();
  ctx.translate(boxPt.x, boxPt.y);

  // Pit box painted boundary
  ctx.strokeStyle = COLORS.accentCyan;
  ctx.lineWidth = 2;
  ctx.strokeRect(-18, -12, 36, 24);

  // Garage marker text
  ctx.font = '9px "JetBrains Mono", monospace';
  ctx.fillStyle = COLORS.accentCyan;
  ctx.textAlign = 'center';
  ctx.fillText('BOX 01', 0, 4);

  ctx.restore();
  ctx.restore();
}
