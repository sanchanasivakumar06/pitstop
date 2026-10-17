"""
REST endpoints for race lifecycle, snapshot querying, and data export.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse

from app.schemas.config import RaceCreateRequest
from app.services.race_manager import get_race_manager
from app.services.exporter import export_race_data

router = APIRouter()


@router.post("", status_code=201)
def create_race(req: RaceCreateRequest) -> Dict[str, str]:
    """Creates a new deterministic race simulation."""
    manager = get_race_manager()
    race_id = manager.create_race(req)
    return {"race_id": race_id}


@router.get("/{race_id}")
def get_race(race_id: str) -> Dict[str, Any]:
    """Returns race configuration, status, and latest telemetry metrics."""
    manager = get_race_manager()
    info = manager.get_race_info(race_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Race {race_id} not found")
    return info


@router.get("/{race_id}/snapshots")
def get_race_snapshots(race_id: str) -> List[Dict[str, Any]]:
    """Returns complete list of per-lap snapshots (runs to completion if needed for offline export)."""
    manager = get_race_manager()
    snaps = manager.get_snapshots(race_id)
    if snaps is None:
        raise HTTPException(status_code=404, detail=f"Race {race_id} not found")
    return snaps


@router.get("/{race_id}/export")
def export_race(race_id: str, format: str = Query("json", pattern="^(json|csv)$")):
    """Exports all race data to JSON or CSV file download."""
    manager = get_race_manager()
    snaps = manager.get_snapshots(race_id)
    if snaps is None:
        raise HTTPException(status_code=404, detail=f"Race {race_id} not found")

    content, media_type = export_race_data(snaps, export_format=format)
    filename = f"{race_id}_export.{format}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
