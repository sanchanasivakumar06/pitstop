"""
Integration and functional tests for the FastAPI REST and WebSocket endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_get_metadata_endpoints():
    # Strategies
    resp_strat = client.get("/api/strategies")
    assert resp_strat.status_code == 200
    strategies = resp_strat.json()
    assert len(strategies) >= 4
    strategy_ids = [s["id"] for s in strategies]
    assert "mdp_agent" in strategy_ids
    assert "baseline_fixed" in strategy_ids

    # Scenarios
    resp_scen = client.get("/api/scenarios")
    assert resp_scen.status_code == 200
    scenarios = resp_scen.json()
    assert len(scenarios) >= 5

    # Tracks
    resp_tracks = client.get("/api/tracks")
    assert resp_tracks.status_code == 200
    tracks = resp_tracks.json()
    assert len(tracks) >= 3
    track_ids = [t["id"] for t in tracks]
    assert "silverstone_classic" in track_ids
    assert "centerline" in tracks[0]
    assert "pit_lane" in tracks[0]


def test_race_creation_lifecycle_and_snapshots():
    # Create race
    create_payload = {
        "seed": 42,
        "track_id": "silverstone_classic",
        "total_laps": 15,
        "strategy_id": "mdp_agent",
        "scenario_name": "changing_weather",
        "start_fuel_kg": 60.0,
        "start_tyre_compound": "MEDIUM",
    }
    resp_create = client.post("/api/races", json=create_payload)
    assert resp_create.status_code == 201
    race_id = resp_create.json()["race_id"]
    assert race_id.startswith("race_")

    # Get race info
    resp_get = client.get(f"/api/races/{race_id}")
    assert resp_get.status_code == 200
    info = resp_get.json()
    assert info["race_id"] == race_id
    assert info["total_laps"] == 15

    # Get snapshots (triggers complete simulation if not already finished)
    resp_snaps = client.get(f"/api/races/{race_id}/snapshots")
    assert resp_snaps.status_code == 200
    snaps = resp_snaps.json()
    assert len(snaps) == 15
    first_snap = snaps[0]
    assert "car" in first_snap
    assert "decision" in first_snap
    assert "weather" in first_snap
    assert "metrics" in first_snap

    # JSON export
    resp_exp_json = client.get(f"/api/races/{race_id}/export?format=json")
    assert resp_exp_json.status_code == 200
    assert "application/json" in resp_exp_json.headers["content-type"]

    # CSV export
    resp_exp_csv = client.get(f"/api/races/{race_id}/export?format=csv")
    assert resp_exp_csv.status_code == 200
    assert "text/csv" in resp_exp_csv.headers["content-type"]
    assert "lap,sim_time_s,phase" in resp_exp_csv.text


def test_batch_evaluation_endpoint():
    eval_payload = {
        "strategies": ["mdp_agent", "baseline_fixed"],
        "scenarios": ["dry_race", "changing_weather"],
        "n_races": 4,
        "track_id": "silverstone_classic",
        "total_laps": 15,
    }
    resp = client.post("/api/evaluate", json=eval_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "per_race" in data
    assert len(data["summary"]) == 2


def test_nonexistent_race_404():
    resp = client.get("/api/races/race_nonexistent_999")
    assert resp.status_code == 404
    err = resp.json()
    assert "error" in err
    assert err["error"]["code"] == 404


def test_websocket_stream_handshake():
    # Create race first
    create_resp = client.post("/api/races", json={"total_laps": 10})
    race_id = create_resp.json()["race_id"]

    with client.websocket_connect(f"/ws/races/{race_id}") as ws:
        init_data = ws.receive_json()
        assert init_data["type"] == "init"
        assert init_data["race_id"] == race_id
        assert "track" in init_data

        # Send step command
        ws.send_json({"action": "step"})
        step_data = ws.receive_json()
        assert step_data["type"] == "lap_snapshot"
        assert step_data["snapshot"]["lap"] == 1
