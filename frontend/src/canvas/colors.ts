/**
 * Color definitions for canvas rendering and UI elements.
 */

export const COLORS = {
  // Asphalt & Track
  asphalt: '#1e2430',
  asphaltWet: '#11151c',
  trackBorder: '#334155',
  kerbRed: '#ef4444',
  kerbWhite: '#f8fafc',
  startLine: '#ffffff',
  sectorLine: '#06b6d4',
  accentCyan: '#06b6d4',
  accentGreen: '#10b981',
  accentAmber: '#f59e0b',

  // Pit Lane
  pitAsphalt: '#171c26',
  pitBorder: '#f59e0b',
  pitBox: '#06b6d4',
  pitCrew: '#f8fafc',
  fuelHose: '#eab308',

  // Cars & Liveries
  carPlayer: '#06b6d4',       // Cyan Strategist AI car
  carPlayerSecondary: '#0284c7',
  carRival1: '#ef4444',       // Scuderia Red
  carRival2: '#94a3b8',       // Silver Arrow
  carRival3: '#f59e0b',       // Apex Racing
  carRival4: '#8b5cf6',       // Phantom Bull
  safetyCar: '#eab308',       // Safety Car Neon Yellow

  // Tyre Compounds
  tyreSoft: '#ef4444',
  tyreMedium: '#eab308',
  tyreHard: '#ffffff',
  tyreInter: '#10b981',
  tyreWet: '#3b82f6',

  // Weather & Overlays
  rainDrop: 'rgba(147, 197, 253, 0.65)',
  wetReflection: 'rgba(6, 182, 212, 0.12)',
  safetyCarFlag: 'rgba(234, 179, 8, 0.22)',
  punctureFlash: 'rgba(239, 68, 68, 0.45)',

  // HUD
  hudText: '#f8fafc',
  hudSub: '#94a3b8',
};

export function getCompoundColor(compound: string): string {
  const norm = compound.toUpperCase();
  if (norm.includes('SOFT')) return COLORS.tyreSoft;
  if (norm.includes('HARD')) return COLORS.tyreHard;
  if (norm.includes('INTER')) return COLORS.tyreInter;
  if (norm.includes('WET')) return COLORS.tyreWet;
  return COLORS.tyreMedium;
}
