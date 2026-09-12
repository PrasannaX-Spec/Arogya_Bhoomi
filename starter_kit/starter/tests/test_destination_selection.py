"""
Test script for Destination Selection & Candidate Recommendation APIs.
"""

import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db_schema, get_db_connection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db_schema()
    with app.test_client() as client:
        yield client


def test_destination_selection_flow(client):
    """
    Test full flow:
    1. Process batch through pipeline
    2. Get candidates
    3. Select alternative candidate state
    4. Verify DB persistence and audit trail logging
    """
    # 1. Process batch
    resp = client.post("/api/process_batch/BATCH-ZI2026-1014")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["pipeline_complete"] is True

    # Get match ID
    conn = get_db_connection()
    match = conn.execute("SELECT * FROM matches WHERE batch_id = 'BATCH-ZI2026-1014'").fetchone()
    conn.close()
    assert match is not None
    match_id = match["match_id"]

    # 2. Get candidates endpoint
    cand_resp = client.get(f"/api/matches/{match_id}/candidates")
    assert cand_resp.status_code == 200
    cand_data = cand_resp.get_json()
    assert "candidates" in cand_data
    candidates = cand_data["candidates"]
    assert len(candidates) > 0

    # Pick a candidate state
    selected_state = candidates[-1]["target_state"]

    # Reset status to Matched if it was previously set in seed data
    conn = get_db_connection()
    conn.execute("UPDATE matches SET status = 'Matched' WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()

    # 3. Select destination
    sel_resp = client.post(
        f"/api/matches/{match_id}/select_destination",
        json={"selected_state": selected_state, "reason": "Test operator selection"}
    )
    assert sel_resp.status_code == 200, f"Error: {sel_resp.get_json()}"
    sel_data = sel_resp.get_json()
    assert sel_data["success"] is True
    assert sel_data["match"]["target_state"] == selected_state
    assert sel_data["match"]["destination_selection_mode"] == "MANUAL_OVERRIDE"

    # 4. Verify DB persistence & Audit event
    conn = get_db_connection()
    updated_match = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    audit_events = conn.execute(
        "SELECT * FROM audit_events WHERE batch_id = 'BATCH-ZI2026-1014' AND event_type = 'DESTINATION_SELECTED'"
    ).fetchall()
    conn.close()

    assert updated_match["target_state"] == selected_state
    assert len(audit_events) > 0
    assert "DESTINATION_SELECTED" in audit_events[0]["event_type"]
    assert selected_state in audit_events[0]["description"]

    # Cleanup test mutations for BATCH-ZI2026-1014
    conn = get_db_connection()
    conn.execute("UPDATE matches SET target_state = 'Odisha', suggested_target_state = 'Odisha', destination_selection_mode = 'AUTO' WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()


def test_existing_destination_remains_unchanged_until_user_selects(client):
    """
    Rigorously test user's requirement:
    Source: Karnataka
    Initial DB Destination: Delhi / NCR
    - Running process_batch MUST NOT change target_state from Delhi / NCR.
    - Manually selecting 'Kerala' MUST update target_state to Kerala while keeping suggested_target_state as Delhi / NCR.
    - Subsequent process_batch runs MUST reflect Kerala.
    """
    batch_id = "BATCH-PO2025-1009"  # Real batch from Bengaluru Rural, Karnataka

    # 1. Setup DB record with target_state = 'Delhi / NCR' and suggested_target_state = 'Delhi / NCR'
    conn = get_db_connection()
    conn.execute("""
        UPDATE matches 
        SET target_state = 'Delhi / NCR', 
            suggested_target_state = 'Delhi / NCR', 
            destination_selection_mode = 'AUTO', 
            status = 'Matched'
        WHERE batch_id = ?
    """, (batch_id,))
    conn.commit()
    match = conn.execute("SELECT * FROM matches WHERE batch_id = ?", (batch_id,)).fetchone()
    conn.close()

    assert match is not None
    match_id = match["match_id"]
    assert match["target_state"] == "Delhi / NCR"

    # 2. Run pipeline process_batch -> MUST NOT change target_state from Delhi / NCR!
    resp = client.post(f"/api/process_batch/{batch_id}")
    assert resp.status_code == 200
    p_data = resp.get_json()
    assert p_data["matching"]["target_state"] == "Delhi / NCR"
    assert p_data["matching"]["suggested_target_state"] == "Delhi / NCR"
    assert p_data["matching"]["destination_selection_mode"] == "AUTO"

    # Verify DB remains Delhi / NCR
    conn = get_db_connection()
    db_check = conn.execute("SELECT target_state FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    conn.close()
    assert db_check["target_state"] == "Delhi / NCR"

    # 3. User selects Kerala via select_destination API
    sel_resp = client.post(
        f"/api/matches/{match_id}/select_destination",
        json={"selected_state": "Kerala", "reason": "Operator manually selected Kerala"}
    )
    assert sel_resp.status_code == 200
    sel_data = sel_resp.get_json()

    # 4. Verify updated state in database
    conn = get_db_connection()
    updated_match = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    conn.close()

    assert updated_match["target_state"] == "Kerala"
    assert updated_match["suggested_target_state"] == "Delhi / NCR"  # PRESERVED ORIGINAL SUGGESTION!
    assert updated_match["destination_selection_mode"] == "MANUAL_OVERRIDE"

    # 5. Re-run process_batch -> MUST return Kerala as target_state!
    resp2 = client.post(f"/api/process_batch/{batch_id}")
    assert resp2.status_code == 200
    p2_data = resp2.get_json()
    assert p2_data["matching"]["target_state"] == "Kerala"
    assert p2_data["matching"]["suggested_target_state"] == "Delhi / NCR"
    assert p2_data["matching"]["destination_selection_mode"] == "MANUAL_OVERRIDE"
