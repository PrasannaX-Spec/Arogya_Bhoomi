"""
Unit tests for Phase 3: Matching Engine & Active Matches
Covers:
1. Active match retrieval (/api/matches)
2. Match creation via pipeline
3. Duplicate match prevention (Idempotency)
4. Match detail (/api/matches/<id>)
5. Zinc match specifics (soil dosage)
6. Ferrous Sulphate match specifics (foliar spray, no soil dosage)
7. Match status update (/api/matches/<id>/status)
8. Available stock filtering on soil deficiency API
9. Compound tab filtering on soil deficiency API
10. Non-existent match handling (404)
"""

import sys
import os
import sqlite3
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, DB_PATH

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_1_active_matches_retrieval(client):
    """Test 1: GET /api/matches returns match list and stats."""
    res = client.get("/api/matches")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "stats" in data
    assert "matches" in data
    assert data["stats"]["active_matches"] >= 1
    assert data["stats"]["total_matched_stock_kg"] > 0


def test_2_match_creation_via_pipeline(client):
    """Test 2: Pipeline execution creates match record."""
    batch_id = "BATCH-ZI2026-1014"
    res = client.post(f"/api/process_batch/{batch_id}")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["pipeline_complete"] is True
    assert data["matching"]["matched"] is True

    # Verify match exists in DB
    conn = sqlite3.connect(DB_PATH)
    match_row = conn.execute("SELECT * FROM matches WHERE batch_id = ?", (batch_id,)).fetchone()
    conn.close()
    assert match_row is not None


def test_3_duplicate_match_prevention(client):
    """Test 3: Idempotent processing does not create duplicate match records."""
    batch_id = "BATCH-ZI2026-1014"

    conn = sqlite3.connect(DB_PATH)
    count1 = conn.execute("SELECT COUNT(*) FROM matches WHERE batch_id = ?", (batch_id,)).fetchone()[0]
    conn.close()

    # Call process_batch second time
    res = client.post(f"/api/process_batch/{batch_id}")
    assert res.status_code == 200

    conn = sqlite3.connect(DB_PATH)
    count2 = conn.execute("SELECT COUNT(*) FROM matches WHERE batch_id = ?", (batch_id,)).fetchone()[0]
    conn.close()

    assert count1 == count2 == 1, "Duplicate match created!"


def test_4_match_detail_endpoint(client):
    """Test 4: GET /api/matches/<id> returns comprehensive detail and explanation."""
    conn = sqlite3.connect(DB_PATH)
    match_id = conn.execute("SELECT match_id FROM matches LIMIT 1").fetchone()[0]
    conn.close()

    res = client.get(f"/api/matches/{match_id}")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["match_id"] == match_id
    assert "explanation" in data
    assert "verified during intake" in data["explanation"]


def test_5_zinc_match_specifics(client):
    """Test 5: Zinc Sulphate match returns soil dosage (37.5 kg/ha)."""
    batch_id = "BATCH-ZI2026-1014"
    client.post(f"/api/process_batch/{batch_id}")

    conn = sqlite3.connect(DB_PATH)
    m = conn.execute("SELECT * FROM matches WHERE batch_id = ?", (batch_id,)).fetchone()
    conn.close()

    assert m is not None
    assert m[2] == "Zinc Sulphate"  # compound_name
    assert "37.5" in m[9]  # recommended_dosage


def test_6_ferrous_sulphate_match_specifics(client):
    """Test 6: Ferrous Sulphate match returns foliar spray, no soil dosage."""
    batch_id = "BATCH-FE2025-1007"
    res = client.post(f"/api/process_batch/{batch_id}")
    assert res.status_code == 200
    data = json.loads(res.data)

    assert data["dosage"]["type"] == "foliar_spray"
    assert "3-4 sprays" in data["dosage"]["spec"]
    assert "rate_kg_ha" not in data["dosage"]


def test_7_match_status_update(client):
    """Test 7: POST /api/matches/<id>/status updates match lifecycle."""
    conn = sqlite3.connect(DB_PATH)
    match_id = conn.execute("SELECT match_id FROM matches LIMIT 1").fetchone()[0]
    conn.close()

    res = client.post(f"/api/matches/{match_id}/status",
                      data=json.dumps({"status": "Ready for Partner"}),
                      content_type="application/json")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "Ready for Partner"


def test_8_available_stock_filtering(client):
    """Test 8: GET /api/soil_deficiency?has_available_stock=true returns only matched states."""
    res = client.get("/api/soil_deficiency?has_available_stock=true")
    assert res.status_code == 200
    states = json.loads(res.data)
    for s in states:
        assert s["has_matched_stock"] is True


def test_9_compound_tab_filtering(client):
    """Test 9: GET /api/soil_deficiency?compound=Zinc+Sulphate filters states correctly."""
    res = client.get("/api/soil_deficiency?compound=Zinc+Sulphate")
    assert res.status_code == 200
    states = json.loads(res.data)
    for s in states:
        if s["status"] == "usable":
            assert "Zinc Sulphate" in s["usable_compounds"]


def test_10_non_existent_match_handling(client):
    """Test 10: GET /api/matches/99999 returns 404."""
    res = client.get("/api/matches/99999")
    assert res.status_code == 404
    data = json.loads(res.data)
    assert "error" in data
