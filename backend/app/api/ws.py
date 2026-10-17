"""
WebSocket streaming endpoint for real-time race telemetry and playback control.
Supports play, pause, step, speed scaling, reset, and seek actions.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.race_manager import get_race_manager
from engine.track import get_track

router = APIRouter()
logger = logging.getLogger("pitstop.ws")


@router.websocket("/ws/races/{race_id}")
async def websocket_race_stream(websocket: WebSocket, race_id: str):
    await websocket.accept()
    manager = get_race_manager()
    race_info = manager.get_race_info(race_id)

    if not race_info:
        await websocket.send_json({"type": "error", "message": f"Race {race_id} not found"})
        await websocket.close()
        return

    track_config = get_track(race_info["config"].get("track_id", "silverstone_classic"))

    # 1. Send initial handshake with static metadata and track geometry
    init_payload = {
        "type": "init",
        "race_id": race_id,
        "config": race_info["config"],
        "track": track_config.to_dict(),
        "total_laps": race_info["total_laps"],
    }
    await websocket.send_json(init_payload)

    # Playback control state
    state = {
        "is_playing": False,
        "speed": 1.0,         # 1.0x to 10.0x
        "tick_rate_hz": 20,   # ticks per second for smooth rendering
    }

    async def incoming_listener():
        """Listens for playback commands from the client."""
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                action = msg.get("action", "")
                val = msg.get("value", None)

                if action == "play":
                    state["is_playing"] = True
                elif action == "pause":
                    state["is_playing"] = False
                elif action == "step":
                    state["is_playing"] = False
                    snap = manager.step_lap(race_id)
                    if snap:
                        await websocket.send_json({"type": "lap_snapshot", "snapshot": snap})
                elif action == "speed":
                    state["speed"] = max(0.2, min(20.0, float(val or 1.0)))
                elif action == "reset":
                    state["is_playing"] = False
                    # Create fresh run with same config
                    req_config = manager.store.get_race(race_id).config
                    new_id = manager.create_race(type("R", (), {"model_dump": lambda: req_config, **req_config})())
                    await websocket.send_json({"type": "reset", "new_race_id": new_id})
            except (WebSocketDisconnect, asyncio.CancelledError):
                break
            except Exception as e:
                logger.error(f"WebSocket client message error: {e}")

    listener_task = asyncio.create_task(incoming_listener())

    try:
        # Main simulation loop streaming ticks and lap snapshots
        sub_progress = 0.0
        while True:
            if state["is_playing"]:
                # Step sub-lap progress for high-framerate visual stream
                step_delta = (1.0 / state["tick_rate_hz"]) * (state["speed"] * 0.75)
                sub_progress += step_delta

                if sub_progress >= 1.0:
                    sub_progress = 0.0
                    snap = manager.step_lap(race_id)
                    if snap:
                        await websocket.send_json({"type": "lap_snapshot", "snapshot": snap})
                        if snap.get("phase") == "FINISHED":
                            state["is_playing"] = False
                            await websocket.send_json({"type": "finished", "metrics": snap.get("metrics")})
                else:
                    # Lightweight sub-lap tick for position and speed
                    stored = manager.store.get_race(race_id)
                    if stored and stored.simulation:
                        car = stored.simulation.car
                        await websocket.send_json({
                            "type": "tick",
                            "progress": round(sub_progress, 4),
                            "speed_kmh": round(car.speed_kmh, 1),
                            "phase": "RACING" if not stored.simulation.event_manager.is_safety_car_active else "SAFETY_CAR",
                        })

            await asyncio.sleep(1.0 / state["tick_rate_hz"])

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for race {race_id}")
    finally:
        listener_task.cancel()
