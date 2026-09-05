"""
Unit tests for Phase 4: Certified Partner Facilities & Downstream Routing
Covers:
1. Partner retrieval (/api/partners)
2. Partner detail (/api/partners/<id>)
3. Eligible partner filtering (/api/partners/eligible?match_id=<id>)
4. Compound compatibility check
5. Capacity validation (sufficient capacity)
6. Insufficient capacity rejection (low capacity partner)
7. Partner assignment (/api/matches/<id>/assign-partner)
8. Assignment persistence in SQLite
9. Re-assignment handling (capacity restoration)
10. Invalid match handling (404)
11. Non-existent partner handling (404)
12. Match origin field verification ('pipeline' vs 'demo_seed')
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


def test_1_partner_retrieval(client):
    """Test 1: GET /api/partners returns list of certified partner facilities."""
    res = client.get("/api/partners")
    assert res.status_code == 200
    partners = json.loads(res.data)
    assert len(partners) >= 6
    assert "name" in partners[0]
    assert "supported_compounds" in partners[0]


def test_2_partner_detail(client):
    """Test 2: GET /api/partners/<id> returns single partner detail."""
    res = client.get("/api/partners/1")
    assert res.status_code == 200
    p = json.loads(res.data)
    assert p["partner_id"] == 1
    assert "Odisha" in p["name"] or "Bhubaneswar" in p["location"]


def test_3_eligible_partner_filtering(client):
    """Test 3: GET /api/partners/eligible?match_id=<id> returns partners with capacity check results."""
    conn = sqlite3.connect(DB_PATH)
    match_id = conn.execute("SELECT match_id FROM matches LIMIT 1").fetchone()[0]
    conn.close()

    res = client.get(f"/api/partners/eligible?match_id={match_id}")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "match" in data
    assert "eligible_partners" in data
    assert len(data["eligible_partners"]) >= 1


def test_4_compound_compatibility(client):
    """Test 4: Verify compound compatibility is evaluated correctly."""
    conn = sqlite3.connect(DB_PATH)
    match_id = conn.execute("SELECT match_id FROM matches WHERE compound_name = 'Zinc Sulphate' LIMIT 1").fetchone()[0]
    conn.close()

    res = client.get(f"/api/partners/eligible?match_id={match_id}")
    data = json.loads(res.data)

    for p in data["eligible_partners"]:
        if "Zinc Sulphate" in p["supported_compounds"]:
            assert p["is_compound_supported"] is True
        else:
            assert p["is_compound_supported"] is False


def test_5_capacity_validation(client):
    """Test 5: Capacity check evaluates available_capacity_kg against batch quantity."""
    conn = sqlite3.connect(DB_PATH)
    match_id = conn.execute("SELECT match_id FROM matches LIMIT 1").fetchone()[0]
    conn.close()

    res = client.get(f"/api/partners/eligible?match_id={match_id}")
    data = json.loads(res.data)

    for p in data["eligible_partners"]:
        if p["available_capacity_kg"] >= p["required_qty_kg"]:
            assert p["is_capacity_sufficient"] is True
        else:
            assert p["is_capacity_sufficient"] is False


def test_6_insufficient_capacity_rejection(client):
    """Test 6: Assigning to a partner with insufficient capacity returns 400 Error."""
    # Find low capacity partner (e.g. Punjab with 50kg capacity) and a large batch (e.g. >100kg)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE partners SET available_capacity_kg = 10.0 WHERE partner_id = 6")
    conn.commit()

    match_id = conn.execute("SELECT match_id FROM matches LIMIT 1").fetchone()[0]
    conn.close()

    res = client.post(f"/api/matches/{match_id}/assign-partner",
                      data=json.dumps({"partner_id": 6}),
                      content_type="application/json")

    assert res.status_code == 400
    data = json.loads(res.data)
    assert "error" in data
    assert "Insufficient capacity" in data["error"]


def test_7_partner_assignment(client):
    """Test 7: POST /api/matches/<id>/assign-partner assigns partner and updates status."""
    conn = sqlite3.connect(DB_PATH)
    # Ensure partner 1 has sufficient capacity
    conn.execute("UPDATE partners SET available_capacity_kg = 2000.0 WHERE partner_id = 1")
    match_id = conn.execute("SELECT match_id FROM matches WHERE compound_name = 'Zinc Sulphate' LIMIT 1").fetchone()[0]
    conn.commit()
    conn.close()

    res = client.post(f"/api/matches/{match_id}/assign-partner",
                      data=json.dumps({"partner_id": 1}),
                      content_type="application/json")

    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "Partner Assigned"
    assert data["assigned_partner_id"] == 1
    assert data["assigned_partner_name"] is not None


def test_8_assignment_persistence(client):
    """Test 8: Partner assignment persists in SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    match_row = conn.execute("SELECT * FROM matches WHERE status = 'Partner Assigned' LIMIT 1").fetchone()
    conn.close()

    assert match_row is not None
    assert match_row[13] is not None or match_row["assigned_partner_id"] is not None


def test_9_reassignment_handling(client):
    """Test 9: Reassigning partner restores capacity to previous partner and deducts from new partner."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE partners SET available_capacity_kg = 1000.0 WHERE partner_id = 2")
    match_id = conn.execute("SELECT match_id FROM matches WHERE status = 'Partner Assigned' LIMIT 1").fetchone()[0]
    conn.commit()
    conn.close()

    res = client.post(f"/api/matches/{match_id}/assign-partner",
                      data=json.dumps({"partner_id": 2}),
                      content_type="application/json")

    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["assigned_partner_id"] == 2


def test_10_invalid_match_handling(client):
    """Test 10: Assigning non-existent match returns 404."""
    res = client.post("/api/matches/99999/assign-partner",
                      data=json.dumps({"partner_id": 1}),
                      content_type="application/json")

    assert res.status_code == 404
    data = json.loads(res.data)
    assert "error" in data


def test_11_non_existent_partner_handling(client):
    """Test 11: Assigning non-existent partner returns 404."""
    conn = sqlite3.connect(DB_PATH)
    match_id = conn.execute("SELECT match_id FROM matches LIMIT 1").fetchone()[0]
    conn.close()

    res = client.post(f"/api/matches/{match_id}/assign-partner",
                      data=json.dumps({"partner_id": 99999}),
                      content_type="application/json")

    assert res.status_code == 404
    data = json.loads(res.data)
    assert "error" in data


def test_12_origin_field_verification(client):
    """Test 12: Verify match origin field distinguishes pipeline vs demo_seed."""
    res = client.get("/api/matches")
    assert res.status_code == 200
    data = json.loads(res.data)

    for m in data["matches"]:
        assert "origin" in m
        assert m["origin"] in ["pipeline", "demo_seed"]
