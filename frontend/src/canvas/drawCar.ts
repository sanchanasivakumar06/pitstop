/**
 * Car and rival vehicle rendering module.
 * Draws procedural formula/prototype race cars with wheels, tyre compound colored rings,
 * aero surfaces, driver helmets, and position indicator badges.
 */

import { Point2D } from '../types/snapshot';
import { COLORS, getCompoundColor } from './colors';

export function drawCarShape(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  headingRad: number,
  color: string,
  compound: string,
  positionText: string,
  isPlayer: boolean = false
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(headingRad);

  const compoundColor = getCompoundColor(compound);

  // 1. Draw 4 Wheels with Tyre Compound Colored Rings
  const wheelW = 4;
  const wheelL = 9;
  const wheelOffset = 9;

  // Front wheels
  drawWheel(ctx, 10, -wheelOffset, wheelL, wheelW, compoundColor);
  drawWheel(ctx, 10, wheelOffset, wheelL, wheelW, compoundColor);
  // Rear wheels
  drawWheel(ctx, -10, -wheelOffset, wheelL, wheelW, compoundColor);
  drawWheel(ctx, -10, wheelOffset, wheelL, wheelW, compoundColor);

  // 2. Aerodynamic Chassis / Bodywork
  ctx.fillStyle = color;
  ctx.beginPath();
  // Nose cone
  ctx.moveTo(18, 0);
  ctx.lineTo(8, -5);
  // Sidepod left
  ctx.lineTo(-6, -7);
  // Rear wing endplate left
  ctx.lineTo(-14, -8);
  // Rear wing center
  ctx.lineTo(-15, 0);
  // Rear wing endplate right
  ctx.lineTo(-14, 8);
  // Sidepod right
  ctx.lineTo(-6, 7);
  ctx.lineTo(8, 5);
  ctx.closePath();
  ctx.fill();

  // 3. Front Wing (aerodynamic plane)
  ctx.fillStyle = isPlayer ? '#0284c7' : '#334155';
  ctx.fillRect(14, -9, 3, 18);

  // 4. Rear Wing
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(-16, -9, 4, 18);

  // 5. Cockpit & Driver Helmet
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(-2, -3, 6, 6);
  ctx.fillStyle = isPlayer ? '#f8fafc' : '#fbbf24';
  ctx.beginPath();
  ctx.arc(0, 0, 2.5, 0, Math.PI * 2);
  ctx.fill();

  // 6. Player Glowing Highlight
  if (isPlayer) {
    ctx.strokeStyle = COLORS.accentCyan;
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }

  ctx.restore();

  // 7. Position Badge & Tag (drawn unrotated for easy reading)
  ctx.save();
  ctx.translate(x, y - 18);

  // Position pill
  ctx.fillStyle = isPlayer ? COLORS.accentCyan : 'rgba(15, 23, 42, 0.85)';
  ctx.strokeStyle = isPlayer ? '#ffffff' : '#475569';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(-10, -8, 20, 14, 3);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = isPlayer ? '#03141f' : '#f8fafc';
  ctx.font = 'bold 9px "JetBrains Mono", monospace';
  ctx.textAlign = 'center';
  ctx.fillText(positionText, 0, 2);

  ctx.restore();
}

function drawWheel(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  length: number,
  width: number,
  compoundColor: string
): void {
  ctx.save();
  // Black rubber tyre
  ctx.fillStyle = '#090d14';
  ctx.fillRect(cx - length / 2, cy - width / 2, length, width);

  // Compound colored outer sidewall stripe
  ctx.strokeStyle = compoundColor;
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.arc(cx, cy, 2.2, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}
