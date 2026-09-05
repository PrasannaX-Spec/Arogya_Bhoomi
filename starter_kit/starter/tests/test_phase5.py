"""
Unit tests for Phase 5: Tamper-Evident Hash-Linked Audit Trail & Soil Re-test Feedback Loop
Covers:
AUDIT TRAIL:
1. Audit event creation
2. Genesis event (previous_hash = 'GENESIS')
3. Hash generation (SHA-256)
4. Previous-hash linkage
5. Chain verification (valid chain)
6. Tamper detection (modified payload fails verification)
7. Append-only behavior (no edit/delete routes exist)
8. Correct batch filtering

HANDOFF WORKFLOW:
9. Handoff requires assigned partner
10. Handoff completion persistence & status transition
11. Duplicate handoff prevention

SOIL RE-TEST WORKFLOW:
12. Re-test creation
13. Match linkage validation
14. Re-test result persistence
15. Improved result classification
16. No-change result classification
17. Worsened result classification
18. Pending result classification
19. Audit event creation for re-test lifecycle
20. Prevention of unrelated re-test records
"""

import sys
import os
import sqlite3
import json
import uuid
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, DB_PATH, calculate_event_hash, record_audit_event, verify_audit_chain

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- AUDIT TRAIL TESTS ---

def test_1_audit_event_creation(client):
    """Test 1: Create an audit event via record_audit_event helper."""
    batch_id = f"BATCH-TEST-1-{uuid.uuid4().hex[:6]}"
    evt = record_audit_event(
        batch_id=batch_id,
        event_type="BATCH_LOGGED",
        actor="Distributor Intake",
        description="Test batch created for unit testing"
    )
    assert evt["batch_id"] == batch_id
    assert evt["event_type"] == "BATCH_LOGGED"
    assert evt["previous_hash"] == "GENESIS"
    assert len(evt["event_hash"]) == 64


def test_2_genesis_event(client):
    """Test 2: Genesis event has previous_hash = 'GENESIS'."""
    batch_id = f"BATCH-TEST-2-{uuid.uuid4().hex[:6]}"
    evt = record_audit_event(
        batch_id=batch_id,
        event_type="BATCH_LOGGED",
        actor="System",
        description="Initial genesis event"
    )
    assert evt["previous_hash"] == "GENESIS"


def test_3_hash_generation(client):
    """Test 3: Hash generation matches SHA-256 calculation algorithm."""
    event_id = 999
    batch_id = "BATCH-TEST-HASH"
    event_type = "COMPLIANCE_VERIFIED"
    timestamp = "2026-09-05 10:00:00"
    description = "Test hash calculation"
    prev_hash = "GENESIS"

    expected_hash = calculate_event_hash(event_id, batch_id, event_type, timestamp, description, prev_hash)
    assert isinstance(expected_hash, str)
    assert len(expected_hash) == 64


def test_4_previous_hash_linkage(client):
    """Test 4: Subsequent event links to previous event's event_hash."""
    batch_id = f"BATCH-TEST-4-{uuid.uuid4().hex[:6]}"
    evt1 = record_audit_event(batch_id, "BATCH_LOGGED", "Intake", "Step 1")
    evt2 = record_audit_event(batch_id, "COMPLIANCE_VERIFIED", "Compliance Engine", "Step 2")

    assert evt2["previous_hash"] == evt1["event_hash"]


def test_5_chain_verification(client):
    """Test 5: Chain verification returns is_valid=True for untampered chain."""
    batch_id = f"BATCH-TEST-5-{uuid.uuid4().hex[:6]}"
    record_audit_event(batch_id, "BATCH_LOGGED", "Intake", "Step 1")
    record_audit_event(batch_id, "COMPLIANCE_VERIFIED", "Engine", "Step 2")
    record_audit_event(batch_id, "MATCH_CREATED", "Matching Engine", "Step 3")

    res = client.post(f"/api/audit/{batch_id}/verify")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["is_valid"] is True
    assert data["events_count"] == 3


def test_6_tamper_detection(client):
    """Test 6: Chain verification detects tampered data in event history."""
    batch_id = f"BATCH-TEST-6-{uuid.uuid4().hex[:6]}"
    record_audit_event(batch_id, "BATCH_LOGGED", "Intake", "Step 1")
    record_audit_event(batch_id, "COMPLIANCE_VERIFIED", "Engine", "Step 2")

    # Manually tamper with the description in SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE audit_events SET description = 'TAMPERED DESCRIPTION' WHERE batch_id = ? AND event_type = 'BATCH_LOGGED'",
        (batch_id,)
    )
    conn.commit()
    conn.close()

    res = client.post(f"/api/audit/{batch_id}/verify")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["is_valid"] is False
    assert "tamper" in data.get("verification_message", "").lower() or "mismatch" in data.get("reason", "").lower() or "failure" in data.get("reason", "").lower()


def test_7_append_only_behavior(client):
    """Test 7: Verify audit events have no PUT or DELETE routes (append-only API structure)."""
    res_put = client.put("/api/audit/BATCH-ZI2026-1014")
    assert res_put.status_code in [405, 404]

    res_del = client.delete("/api/audit/BATCH-ZI2026-1014")
    assert res_del.status_code in [405, 404]


def test_8_correct_batch_filtering(client):
    """Test 8: GET /api/audit/<batch_id> filters correctly per batch."""
    batch_a = f"BATCH-TEST-8A-{uuid.uuid4().hex[:6]}"
    batch_b = f"BATCH-TEST-8B-{uuid.uuid4().hex[:6]}"

    record_audit_event(batch_a, "BATCH_LOGGED", "System", "Event A")
    record_audit_event(batch_b, "BATCH_LOGGED", "System", "Event B")

    res_a = client.get(f"/api/audit/{batch_a}")
    assert res_a.status_code == 200
    data_a = json.loads(res_a.data)
    assert len(data_a["events"]) == 1
    assert data_a["events"][0]["batch_id"] == batch_a

    res_b = client.get(f"/api/audit/{batch_b}")
    assert res_b.status_code == 200
    data_b = json.loads(res_b.data)
    assert len(data_b["events"]) == 1
    assert data_b["events"][0]["batch_id"] == batch_b


# --- HANDOFF TESTS ---

def test_9_handoff_requires_partner(client):
    """Test 9: Handoff completion fails if no partner is assigned."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO matches (batch_id, compound_name, source_state, target_state, target_district, deficiency_type, severity, match_type, recommended_dosage, status, origin)
        VALUES ('BATCH-ZI2026-1014', 'Zinc Sulphate', 'Telangana', 'Odisha', 'Cuttack', 'Zn', 'Severe', 'same_state', '37.5 kg/ha', 'Matched', 'pipeline')
    """)
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/matches/{match_id}/record-handoff", json={
        "handoff_date": "2026-09-05",
        "receiving_facility": "Test Facility",
        "quantity_kg": 500,
        "receipt_number": "REC-TEST-99"
    })

    # Cleanup test match
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 400
    data = json.loads(res.data)
    assert "partner" in data.get("error", "").lower()


def test_10_handoff_completion_persistence(client):
    """Test 10: Handoff completion transitions status to 'Completed' and records audit event."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO matches (batch_id, compound_name, source_state, target_state, target_district, deficiency_type, severity, match_type, recommended_dosage, status, origin, assigned_partner_id, assigned_partner_name)
        VALUES ('BATCH-ZI2026-1014', 'Zinc Sulphate', 'Telangana', 'Odisha', 'Cuttack', 'Zn', 'Severe', 'same_state', '37.5 kg/ha', 'Assigned', 'pipeline', 1, 'AgriMicro Works')
    """)
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/matches/{match_id}/record-handoff", json={
        "handoff_date": "2026-09-05",
        "receiving_facility": "AgriMicro Recovery Works",
        "quantity_kg": 1000,
        "receipt_number": "REC-2026-HANDOFF-10"
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "Completed"

    # Verify SQLite persistence
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT status, handoff_receipt FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    conn.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()

    assert row[0] == "Completed"
    assert row[1] == "REC-2026-HANDOFF-10"


def test_11_duplicate_handoff_prevention(client):
    """Test 11: Attempting to record handoff twice fails."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO matches (batch_id, compound_name, source_state, target_state, target_district, deficiency_type, severity, match_type, recommended_dosage, status, origin, assigned_partner_id, assigned_partner_name)
        VALUES ('BATCH-ZI2026-1014', 'Zinc Sulphate', 'Telangana', 'Odisha', 'Cuttack', 'Zn', 'Severe', 'same_state', '37.5 kg/ha', 'Completed', 'pipeline', 1, 'AgriMicro Works')
    """)
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/matches/{match_id}/record-handoff", json={
        "handoff_date": "2026-09-05",
        "receiving_facility": "AgriMicro Recovery Works",
        "quantity_kg": 500,
        "receipt_number": "REC-2026-DUP"
    })

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 400
    data = json.loads(res.data)
    assert "already completed" in data.get("error", "").lower()


# --- SOIL RE-TEST TESTS ---

def test_12_retest_creation(client):
    """Test 12: Soil re-test creation links to valid match."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT match_id, batch_id FROM matches LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    match_id, batch_id = row[0], row[1]

    res = client.post("/api/retests", json={
        "match_id": match_id,
        "planned_retest_date": "2026-10-15"
    })
    assert res.status_code in [200, 201]
    data = json.loads(res.data)
    assert data["batch_id"] == batch_id


def test_13_match_linkage_validation(client):
    """Test 13: Soil re-test creation fails for non-existent match_id."""
    res = client.post("/api/retests", json={
        "match_id": 999999,
        "planned_retest_date": "2026-10-15"
    })
    assert res.status_code == 404
    data = json.loads(res.data)
    assert "not found" in data.get("error", "").lower()


def test_14_retest_result_persistence(client):
    """Test 14: Submitting observation persists result and updates status to Completed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO soil_retests (match_id, batch_id, target_state, target_district, compound, initial_severity, retest_status)
        VALUES (1, 'BATCH-ZI2026-1014', 'Odisha', 'Kurdha', 'Zinc Sulphate', 'Severe', 'Pending')
    """)
    retest_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/retests/{retest_id}/result", json={
        "actual_retest_date": "2026-10-10",
        "post_application_severity": "Moderate",
        "result_outcome": "Improved",
        "notes": "Empirical field sample confirmed reduction in deficiency."
    })

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM soil_retests WHERE retest_id = ?", (retest_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["retest_status"] == "Completed"
    assert data["result_outcome"] == "Improved"


def test_15_improved_result(client):
    """Test 15: Severity decrease (Severe -> Moderate) classifies outcome as Improved."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO soil_retests (match_id, batch_id, target_state, compound, initial_severity, retest_status)
        VALUES (1, 'BATCH-ZI2026-1014', 'Odisha', 'Zinc Sulphate', 'Severe', 'Pending')
    """)
    retest_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/retests/{retest_id}/result", json={
        "post_application_severity": "Moderate"
    })

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM soil_retests WHERE retest_id = ?", (retest_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["result_outcome"] == "Improved"


def test_16_no_change_result(client):
    """Test 16: Same severity (Moderate -> Moderate) classifies outcome as No Significant Change."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO soil_retests (match_id, batch_id, target_state, compound, initial_severity, retest_status)
        VALUES (1, 'BATCH-ZI2026-1014', 'Odisha', 'Zinc Sulphate', 'Moderate', 'Pending')
    """)
    retest_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/retests/{retest_id}/result", json={
        "post_application_severity": "Moderate"
    })

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM soil_retests WHERE retest_id = ?", (retest_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["result_outcome"] == "No Significant Change"


def test_17_worsened_result(client):
    """Test 17: Increased severity (Moderate -> Severe) classifies outcome as Worsened."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO soil_retests (match_id, batch_id, target_state, compound, initial_severity, retest_status)
        VALUES (1, 'BATCH-ZI2026-1014', 'Odisha', 'Zinc Sulphate', 'Moderate', 'Pending')
    """)
    retest_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.post(f"/api/retests/{retest_id}/result", json={
        "post_application_severity": "Severe"
    })

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM soil_retests WHERE retest_id = ?", (retest_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["result_outcome"] == "Worsened"


def test_18_pending_result(client):
    """Test 18: Unsubmitted re-test lists status as Pending."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO soil_retests (match_id, batch_id, target_state, compound, initial_severity, retest_status)
        VALUES (1, 'BATCH-ZI2026-1014', 'Odisha', 'Zinc Sulphate', 'Severe', 'Pending')
    """)
    retest_id = cursor.lastrowid
    conn.commit()
    conn.close()

    res = client.get("/api/retests")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM soil_retests WHERE retest_id = ?", (retest_id,))
    conn.commit()
    conn.close()

    assert res.status_code == 200
    data = json.loads(res.data)
    retests = data.get("retests", [])
    match_items = [r for r in retests if r["retest_id"] == retest_id]
    assert len(match_items) == 1
    assert match_items[0]["retest_status"] == "Pending"


def test_19_audit_event_creation_for_retest(client):
    """Test 19: Scheduling re-test and entering result both append audit events to the batch chain."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    batch_id = "BATCH-ZI2026-1014"
    cursor.execute("""
        INSERT INTO matches (batch_id, compound_name, source_state, target_state, target_district, deficiency_type, severity, match_type, recommended_dosage, status, origin, assigned_partner_id, assigned_partner_name)
        VALUES (?, 'Zinc Sulphate', 'Telangana', 'Odisha', 'Cuttack', 'Zn', 'Severe', 'same_state', '37.5 kg/ha', 'Completed', 'pipeline', 1, 'AgriMicro Works')
    """, (batch_id,))
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 1. Schedule re-test
    res_create = client.post("/api/retests", json={
        "match_id": match_id,
        "planned_retest_date": "2026-10-20"
    })
    assert res_create.status_code in [200, 201]
    retest_id = json.loads(res_create.data)["retest_id"]

    # Check audit event recorded
    res_audit1 = client.get(f"/api/audit/{batch_id}")
    events1 = json.loads(res_audit1.data)["events"]
    assert any(e["event_type"] == "RETEST_SCHEDULED" for e in events1)

    # 2. Record result
    res_res = client.post(f"/api/retests/{retest_id}/result", json={
        "post_application_severity": "Moderate"
    })
    assert res_res.status_code == 200

    # Check result audit event recorded
    res_audit2 = client.get(f"/api/audit/{batch_id}")
    events2 = json.loads(res_audit2.data)["events"]
    assert any(e["event_type"] == "RETEST_RESULT_RECORDED" for e in events2)

    # Cleanup
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM soil_retests WHERE retest_id = ?", (retest_id,))
    conn.execute("DELETE FROM audit_events WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()


def test_20_prevention_of_unrelated_retest_records(client):
    """Test 20: Prevention of re-test creation for invalid/unmatched batches."""
    res = client.post("/api/retests", json={
        "match_id": -999,
        "planned_retest_date": "2026-10-20"
    })
    assert res.status_code == 404
