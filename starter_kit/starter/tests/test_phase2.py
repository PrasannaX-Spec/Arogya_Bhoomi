"""
Unit tests for Phase 2 enhancements:
1. POST /api/batches — Log new batch
2. Idempotent pipeline processing
3. Illustrative district API endpoint
4. Data integrity verification (45 intake records preserved)
"""

import sys
import os
import sqlite3
import json
import pytest

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, DB_PATH

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_data_integrity_45_records():
    """Verify original 45 intake records remain intact in database."""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM intake_batches WHERE batch_doc_id LIKE 'BATCH-%' AND batch_doc_id NOT LIKE 'BATCH-TEST-%'").fetchone()[0]
    conn.close()
    assert count >= 45, f"Expected at least 45 records, found {count}"


def test_post_new_batch(client):
    """Test POST /api/batches creates a new batch in intake_batches."""
    test_id = "BATCH-TEST-PHASE2-NEW"
    payload = {
        "batch_doc_id": test_id,
        "compound_name": "Zinc Sulphate",
        "batch_qty_kg": 120.5,
        "zn_concentration_grade": "21% Zn (heptahydrate)",
        "manufacture_date": "2024-01-01",
        "expiry_date": "2026-06-01",
        "source_location": "Hisar, Haryana",
        "source_type": "Hospital"
    }

    res = client.post("/api/batches", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data["batch_doc_id"] == test_id
    assert data["compound_name"] == "Zinc Sulphate"
    assert data["batch_qty_kg"] == 120.5

    # Cleanup
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM intake_batches WHERE batch_doc_id = ?", (test_id,))
    conn.commit()
    conn.close()


def test_idempotent_pipeline_processing(client):
    """Test running pipeline repeatedly on a batch does not error and returns already_processed flag."""
    batch_id = "BATCH-ZI2026-1014"
    res1 = client.post(f"/api/process_batch/{batch_id}")
    assert res1.status_code == 200
    data1 = json.loads(res1.data)
    assert data1["pipeline_complete"] is True

    # Second call — idempotent
    res2 = client.post(f"/api/process_batch/{batch_id}")
    assert res2.status_code == 200
    data2 = json.loads(res2.data)
    assert data2["already_processed"] is True
    assert data2["pipeline_complete"] is True


def test_districts_endpoint(client):
    """Test GET /api/districts returns illustrative districts and disclaimer."""
    res = client.get("/api/districts")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "disclaimer" in data
    assert "Illustrative" in data["disclaimer"]
    assert len(data["illustrative_districts"]) == 8
