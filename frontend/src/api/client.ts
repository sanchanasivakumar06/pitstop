/**
 * REST API client for race simulation management, metadata, and evaluations.
 */

const BASE_URL = '';

export async function fetchTracks() {
  const res = await fetch(`${BASE_URL}/api/tracks`);
  if (!res.ok) throw new Error('Failed to load tracks');
  return res.json();
}

export async function fetchStrategies() {
  const res = await fetch(`${BASE_URL}/api/strategies`);
  if (!res.ok) throw new Error('Failed to load strategies');
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${BASE_URL}/api/scenarios`);
  if (!res.ok) throw new Error('Failed to load scenarios');
  return res.json();
}

export async function createRace(config: any) {
  const res = await fetch(`${BASE_URL}/api/races`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) throw new Error('Failed to create race');
  return res.json();
}

export async function fetchRaceInfo(raceId: string) {
  const res = await fetch(`${BASE_URL}/api/races/${raceId}`);
  if (!res.ok) throw new Error(`Failed to load race ${raceId}`);
  return res.json();
}

export async function fetchRaceSnapshots(raceId: string) {
  const res = await fetch(`${BASE_URL}/api/races/${raceId}/snapshots`);
  if (!res.ok) throw new Error(`Failed to load snapshots for race ${raceId}`);
  return res.json();
}

export async function runEvaluation(payload: any) {
  const res = await fetch(`${BASE_URL}/api/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Evaluation request failed');
  return res.json();
}
