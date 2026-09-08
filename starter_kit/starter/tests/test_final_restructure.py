"""
test_final_restructure.py — Test suite for the final Arogya Bhoomi project restructure.
Verifies core requirements including navigation routes, pipeline execution,
dosage calculator isolation, and end-to-end judge demonstration flow.
"""

import pytest
import json
import sqlite3
import os
from app import app, get_db_connection

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_01_primary_web_routes(client):
    """Test 1: Verify primary web UI routes load cleanly (HTTP 200)."""
    routes = ["/", "/stock", "/pipeline", "/dosage", "/soil-map", "/about"]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Route {route} failed with status {response.status_code}"


def test_02_legacy_route_aliases(client):
    """Test 2: Verify legacy route aliases redirect/render without breaking."""
    legacy_routes = ["/batches", "/compliance", "/matches", "/simulator", "/network", "/impact"]
    for route in legacy_routes:
        response = client.get(route)
        assert response.status_code == 200, f"Legacy alias route {route} failed with status {response.status_code}"


def test_03_select_demo_batch(client):
    """Test 3: Verify demo batch BATCH-ZI2026-1014 details can be retrieved."""
    response = client.get("/api/batches/BATCH-ZI2026-1014")
    assert response.status_code == 200
    data = response.get_json()
    assert data["batch_doc_id"] == "BATCH-ZI2026-1014"
    assert data["compound_name"] == "Zinc Sulphate"
    assert data["source_location"] == "Bhubaneswar, Odisha"


def test_04_pipeline_execution_e2e(client):
    """Test 4: Verify pipeline execution for BATCH-ZI2026-1014 produces expected match and dosage."""
    response = client.post("/api/process_batch/BATCH-ZI2026-1014")
    assert response.status_code == 200
    data = response.get_json()

    assert data["pipeline_complete"] is True
    assert data["compliance"]["status"] == "Accepted"
    assert data["matching"]["target_state"] == "Odisha"
    assert data["matching"]["matched"] is True
    assert data["dosage"]["type"] == "soil_application"
    assert data["dosage"]["rate_kg_ha"] == 37.5


def test_05_dosage_calculator_isolation(client):
    """Test 5: Verify dosage simulation endpoint functions independently without altering intake batches."""
    payload = {
        "compound_name": "Zinc Sulphate",
        "quantity_kg": 100.0,
        "severity": "Low"
    }
    response = client.post("/api/simulate_recovery", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    data = response.get_json()

    assert data["compound_name"] == "Zinc Sulphate"
    assert data["base_rate_kg_ha"] == 37.5
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM intake_batches WHERE batch_doc_id = 'SIM-TEST'").fetchone()[0]
    conn.close()
    assert count == 0


def test_06_ferrous_sulphate_foliar_branch(client):
    """Test 6: Verify Ferrous Sulphate process pipeline uses foliar spray guidance."""
    response = client.post("/api/process_batch/BATCH-FE2025-1007")
    assert response.status_code == 200
    data = response.get_json()

    assert data["pipeline_complete"] is True
    assert data["dosage"]["type"] == "foliar_spray"
    assert data["dosage"]["spec"] is not None


def test_07_add_new_batch_via_api(client):
    """Test 7: Verify adding a valid new batch via POST /api/batches works cleanly."""
    new_batch = {
        "batch_doc_id": "BATCH-REST-TEST-001",
        "compound_name": "Potassium Chloride",
        "batch_qty_kg": 150.0,
        "source_type": "Retail Pharmacy",
        "source_location": "Bhopal, Madhya Pradesh",
        "manufacture_date": "2024-01-01",
        "expiry_date": "2026-06-01",
        "zn_concentration_grade": "Standard Grade"
    }
    response = client.post("/api/batches", data=json.dumps(new_batch), content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()

    assert data["batch_doc_id"] == "BATCH-REST-TEST-001"
    assert data["compound_name"] == "Potassium Chloride"

    # Cleanup
    conn = get_db_connection()
    conn.execute("DELETE FROM intake_batches WHERE batch_doc_id = 'BATCH-REST-TEST-001'")
    conn.commit()
    conn.close()


def test_08_pdf_download_eligible_batch(client):
    """Test 8: Verify individual PDF download for eligible successful batch BATCH-ZI2026-1014."""
    # First ensure batch is processed & matched
    client.post("/api/process_batch/BATCH-ZI2026-1014")

    response = client.get("/api/reports/pdf/BATCH-ZI2026-1014")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert len(response.data) > 0


def test_09_pdf_download_ineligible_batch(client):
    """Test 9: Verify PDF download is denied for non-existent or rejected/unmatched batch."""
    # Non-existent batch
    resp1 = client.get("/api/reports/pdf/NON-EXISTENT-BATCH")
    assert resp1.status_code == 400
    data1 = resp1.get_json()
    assert "ineligible or not found" in data1["error"]

    # Rejected batch
    resp2 = client.get("/api/reports/pdf/BATCH-MC2026-1045")
    assert resp2.status_code == 400
    data2 = resp2.get_json()
    assert "ineligible" in data2["error"]


def test_10_reports_page_removed(client):
    """Test 10: Verify /reports page remains 100% removed (HTTP 404)."""
    response = client.get("/reports")
    assert response.status_code == 404

