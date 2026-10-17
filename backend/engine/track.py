"""
Track definitions, geometry, and preset configurations.
Provides 2D polyline control points, pit lane paths, and spatial queries.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any


@dataclass
class Point2D:
    x: float
    y: float

    def to_dict(self) -> Dict[str, float]:
        return {"x": round(self.x, 2), "y": round(self.y, 2)}


@dataclass
class TrackConfig:
    id: str
    name: str
    length_km: float
    corners: int
    base_lap_time_s: float
    pit_lane_loss_s: float
    default_laps: int
    centerline: List[Point2D]
    pit_lane: List[Point2D]
    pit_entry_progress: float = 0.88
    pit_box_progress: float = 0.94
    pit_exit_progress: float = 0.06

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "length_km": self.length_km,
            "corners": self.corners,
            "base_lap_time_s": self.base_lap_time_s,
            "pit_lane_loss_s": self.pit_lane_loss_s,
            "default_laps": self.default_laps,
            "pit_entry_progress": self.pit_entry_progress,
            "pit_box_progress": self.pit_box_progress,
            "pit_exit_progress": self.pit_exit_progress,
            "centerline": [p.to_dict() for p in self.centerline],
            "pit_lane": [p.to_dict() for p in self.pit_lane],
        }


def _interpolate_polyline(points: List[Point2D], t: float) -> Tuple[float, float, float]:
    """
    Given a closed polyline of points and progress t in [0, 1),
    returns (x, y, heading_radians).
    """
    if not points:
        return 0.0, 0.0, 0.0
    n = len(points)
    t = t % 1.0
    raw_idx = t * n
    idx = int(raw_idx)
    frac = raw_idx - idx
    p0 = points[idx]
    p1 = points[(idx + 1) % n]

    x = p0.x + frac * (p1.x - p0.x)
    y = p0.y + frac * (p1.y - p0.y)

    dx = p1.x - p0.x
    dy = p1.y - p0.y
    heading = math.atan2(dy, dx)
    return x, y, heading


def _create_monza_sprint() -> TrackConfig:
    """Fast short circuit with long straights and chicanes."""
    # Control points on an 800x500 virtual canvas
    pts = [
        Point2D(150, 420), Point2D(350, 420), Point2D(550, 420), Point2D(700, 420),  # Main straight
        Point2D(750, 390), Point2D(760, 330), Point2D(720, 280),                      # Curva Grande
        Point2D(650, 270), Point2D(620, 240), Point2D(650, 210),                      # Variante chicane
        Point2D(720, 180), Point2D(750, 130), Point2D(720, 80),                       # Lesmo 1 & 2
        Point2D(580, 80),  Point2D(420, 100), Point2D(280, 100),                      # Serraglio straight
        Point2D(220, 130), Point2D(180, 170), Point2D(210, 220),                      # Ascari chicane
        Point2D(260, 240), Point2D(220, 280),                                         # Straight to Parabolica
        Point2D(130, 320), Point2D(100, 370), Point2D(110, 410)                       # Parabolica curve
    ]
    # Pit lane parallel to the main straight (shifted inside/north of straight: y=385)
    pit = [
        Point2D(120, 400), Point2D(160, 385), Point2D(400, 385),
        Point2D(600, 385), Point2D(730, 385), Point2D(750, 390)
    ]
    return TrackConfig(
        id="monza_sprint",
        name="Monza Sprint Circuit",
        length_km=3.85,
        corners=8,
        base_lap_time_s=72.0,
        pit_lane_loss_s=20.0,
        default_laps=45,
        centerline=pts,
        pit_lane=pit,
        pit_entry_progress=0.89,
        pit_box_progress=0.95,
        pit_exit_progress=0.07,
    )


def _create_silverstone_classic() -> TrackConfig:
    """Medium technical circuit with sweeping corners."""
    pts = [
        Point2D(180, 420), Point2D(360, 420), Point2D(540, 420), Point2D(660, 420),  # Hamilton straight
        Point2D(720, 390), Point2D(750, 340), Point2D(710, 290),                      # Abbey & Farm
        Point2D(640, 300), Point2D(600, 330), Point2D(540, 310),                      # Village & Loop
        Point2D(520, 250), Point2D(580, 200), Point2D(680, 190),                      # Aintree & Wellington Straight
        Point2D(740, 160), Point2D(730, 100), Point2D(650, 80),                       # Brooklands & Luffield
        Point2D(500, 80),  Point2D(380, 90),                                           # Woodcote & Copse
        Point2D(310, 120), Point2D(250, 160), Point2D(270, 200), Point2D(220, 240),  # Maggotts, Becketts, Chapel
        Point2D(170, 280), Point2D(140, 340), Point2D(140, 390)                       # Hangar straight & Stowe/Club
    ]
    pit = [
        Point2D(140, 400), Point2D(190, 390), Point2D(400, 390),
        Point2D(600, 390), Point2D(690, 395), Point2D(720, 400)
    ]
    return TrackConfig(
        id="silverstone_classic",
        name="Silverstone Classic",
        length_km=5.25,
        corners=18,
        base_lap_time_s=88.5,
        pit_lane_loss_s=22.5,
        default_laps=60,
        centerline=pts,
        pit_lane=pit,
        pit_entry_progress=0.88,
        pit_box_progress=0.94,
        pit_exit_progress=0.06,
    )


def _create_spa_endurance() -> TrackConfig:
    """Long endurance track with elevation variations and heavy tire load."""
    pts = [
        Point2D(150, 440), Point2D(300, 440), Point2D(450, 440), Point2D(580, 440),  # Pit straight
        Point2D(650, 420), Point2D(690, 370), Point2D(660, 330),                      # La Source
        Point2D(590, 310), Point2D(610, 260), Point2D(680, 240),                      # Eau Rouge & Raidillon
        Point2D(740, 210), Point2D(760, 150), Point2D(720, 90),                       # Kemmel Straight
        Point2D(630, 70),  Point2D(540, 90),  Point2D(470, 130),                      # Les Combes & Malmedy
        Point2D(420, 180), Point2D(360, 210), Point2D(310, 230),                      # Bruxelles & Rivage
        Point2D(250, 200), Point2D(180, 180), Point2D(130, 220),                      # Pouhon double-apex
        Point2D(120, 280), Point2D(170, 320), Point2D(220, 340),                      # Campus & Stavelot
        Point2D(200, 380), Point2D(140, 400)                                           # Blanchimont & Bus Stop chicane
    ]
    pit = [
        Point2D(120, 420), Point2D(160, 410), Point2D(350, 410),
        Point2D(520, 410), Point2D(620, 415), Point2D(650, 420)
    ]
    return TrackConfig(
        id="spa_endurance",
        name="Spa Endurance Circuit",
        length_km=7.00,
        corners=19,
        base_lap_time_s=106.0,
        pit_lane_loss_s=25.0,
        default_laps=75,
        centerline=pts,
        pit_lane=pit,
        pit_entry_progress=0.87,
        pit_box_progress=0.93,
        pit_exit_progress=0.05,
    )


TRACK_PRESETS: Dict[str, TrackConfig] = {
    "monza_sprint": _create_monza_sprint(),
    "silverstone_classic": _create_silverstone_classic(),
    "spa_endurance": _create_spa_endurance(),
}


def get_track(track_id: str) -> TrackConfig:
    if track_id not in TRACK_PRESETS:
        return TRACK_PRESETS["silverstone_classic"]
    return TRACK_PRESETS[track_id]


def get_track_position(track: TrackConfig, progress: float, in_pit: bool = False, pit_stage_progress: float = 0.0) -> Tuple[float, float, float]:
    """
    Returns (x, y, heading_rad) on the canvas for a given race progress.
    If the car is in the pit lane, smoothly navigates the pit_lane polyline.
    """
    if not in_pit:
        return _interpolate_polyline(track.centerline, progress)
    
    # In pit lane: map pit_stage_progress [0, 1] onto pit lane points
    return _interpolate_polyline(track.pit_lane, pit_stage_progress)
