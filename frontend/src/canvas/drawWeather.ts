/**
 * Environmental effects: Rain drops, wet asphalt reflections, and Safety Car caution overlays.
 */

import { COLORS } from './colors';

interface RainDrop {
  x: number;
  y: number;
  length: number;
  speed: number;
}

const rainDrops: RainDrop[] = [];
for (let i = 0; i < 120; i++) {
  rainDrops.push({
    x: Math.random() * 1000,
    y: Math.random() * 700,
    length: 10 + Math.random() * 12,
    speed: 12 + Math.random() * 8,
  });
}

export function drawWeatherAndCautionOverlays(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  weatherState: string,
  isSafetyCar: boolean,
  isVsc: boolean
): void {
  // 1. Wet track darkness & rain particles
  if (weatherState === 'LIGHT_RAIN' || weatherState === 'HEAVY_RAIN') {
    ctx.save();
    const rainAlpha = weatherState === 'HEAVY_RAIN' ? 0.35 : 0.18;
    ctx.fillStyle = `rgba(15, 23, 42, ${rainAlpha})`;
    ctx.fillRect(0, 0, width, height);

    // Diagonal rain streaks
    ctx.strokeStyle = weatherState === 'HEAVY_RAIN' ? 'rgba(186, 230, 253, 0.75)' : 'rgba(186, 230, 253, 0.45)';
    ctx.lineWidth = weatherState === 'HEAVY_RAIN' ? 1.8 : 1.0;
    ctx.beginPath();
    for (const drop of rainDrops) {
      drop.x -= drop.speed * 0.3;
      drop.y += drop.speed;
      if (drop.y > height) {
        drop.y = 0;
        drop.x = Math.random() * width;
      }
      if (drop.x < 0) {
        drop.x = width;
      }
      ctx.moveTo(drop.x, drop.y);
      ctx.lineTo(drop.x - drop.length * 0.3, drop.y + drop.length);
    }
    ctx.stroke();
    ctx.restore();
  }

  // 2. Safety Car Caution Flag Overlay
  if (isSafetyCar || isVsc) {
    ctx.save();
    const flash = Math.floor(Date.now() / 350) % 2 === 0;

    // Glowing yellow caution border around viewport
    ctx.strokeStyle = flash ? '#eab308' : '#ca8a04';
    ctx.lineWidth = 6;
    ctx.strokeRect(3, 3, width - 6, height - 6);

    // Top banner
    ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
    ctx.beginPath();
    ctx.roundRect(width / 2 - 140, 12, 280, 36, 6);
    ctx.fill();
    ctx.strokeStyle = '#eab308';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.font = 'bold 14px "JetBrains Mono", monospace';
    ctx.fillStyle = flash ? '#eab308' : '#ffffff';
    ctx.textAlign = 'center';
    const flagText = isSafetyCar ? '⚠️ SAFETY CAR DEPLOYED' : '🟡 VIRTUAL SAFETY CAR';
    ctx.fillText(flagText, width / 2, 35);

    ctx.restore();
  }
}
