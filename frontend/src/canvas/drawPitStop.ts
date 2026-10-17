/**
 * Detailed Pit Stop Choreography Animation.
 * Renders swarming pit crew mechanics, tyre change swap effect, animated refuelling hose,
 * rising fuel gauge, and live stationary stopwatch banner.
 */

import { Point2D } from '../types/snapshot';
import { COLORS, getCompoundColor } from './colors';

export function drawPitStopChoreography(
  ctx: CanvasRenderingContext2D,
  boxX: number,
  boxY: number,
  stage: string,
  stageProgress: number,
  newCompound: string,
  refuelKg: number,
  stopTimeLoss: number
): void {
  ctx.save();
  ctx.translate(boxX, boxY);

  // 1. Pit Crew Mechanics around the car
  // 4 tyre changers at each wheel position + 2 jack men + 1 fueler
  const crewPositions = [
    { x: 12, y: -16, label: 'RF' },
    { x: 12, y: 16, label: 'LF' },
    { x: -12, y: -16, label: 'RR' },
    { x: -12, y: 16, label: 'LR' },
    { x: 26, y: 0, label: 'JACK_F' },
    { x: -24, y: 0, label: 'JACK_R' },
    { x: -6, y: -20, label: 'FUEL' },
  ];

  ctx.fillStyle = '#f8fafc';
  for (const crew of crewPositions) {
    // Mechanic body
    ctx.beginPath();
    ctx.arc(crew.x, crew.y, 4, 0, Math.PI * 2);
    ctx.fill();
    // Mechanic safety helmet
    ctx.fillStyle = '#06b6d4';
    ctx.beginPath();
    ctx.arc(crew.x, crew.y, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#f8fafc';
  }

  // 2. Animated Refuelling Rig Hose
  ctx.save();
  ctx.strokeStyle = '#eab308';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(-6, -20);
  // Bezier curve to fuel tank intake
  const wave = Math.sin(Date.now() / 150) * 2;
  ctx.quadraticCurveTo(-10 + wave, -12, -4, -4);
  ctx.stroke();
  ctx.restore();

  // 3. Tyre Swap Glow / Burst Effect
  const compColor = getCompoundColor(newCompound);
  ctx.save();
  ctx.strokeStyle = compColor;
  ctx.lineWidth = 2;
  const pulseRadius = 14 + Math.sin(Date.now() / 100) * 3;
  ctx.beginPath();
  ctx.arc(10, -9, pulseRadius, 0, Math.PI * 2);
  ctx.arc(10, 9, pulseRadius, 0, Math.PI * 2);
  ctx.arc(-10, -9, pulseRadius, 0, Math.PI * 2);
  ctx.arc(-10, 9, pulseRadius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // 4. Floating Pit Banner: "PIT STOP - Medium tyres, +32 kg fuel - 24.3 s"
  ctx.save();
  ctx.translate(0, -45);
  ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
  ctx.strokeStyle = COLORS.accentCyan;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(-110, -18, 220, 36, 6);
  ctx.fill();
  ctx.stroke();

  // Banner text
  ctx.font = 'bold 11px "Rajdhani", sans-serif';
  ctx.fillStyle = '#f8fafc';
  ctx.textAlign = 'center';
  const fuelText = refuelKg > 0 ? `+${refuelKg.toFixed(0)} kg fuel` : 'tyres only';
  ctx.fillText(`BOX BOX - ${newCompound.toUpperCase()} (${fuelText})`, 0, -3);

  ctx.font = 'bold 12px "JetBrains Mono", monospace';
  ctx.fillStyle = '#f59e0b';
  ctx.fillText(`STOP TIME: ${stopTimeLoss.toFixed(1)}s`, 0, 11);

  ctx.restore();
  ctx.restore();
}
