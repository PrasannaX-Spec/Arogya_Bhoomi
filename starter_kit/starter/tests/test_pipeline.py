"""
End-to-end pipeline test via the Flask API.
Tests the 3 critical scenarios plus the 7 required test cases.
"""

import urllib.request
import json
import sqlite3
import os

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")



def api_post(path):
    req = urllib.request.Request(f"{BASE_URL}{path}", method="POST",
                                headers={"Content-Type": "application/json"},
                                data=b"{}")
    res = urllib.request.urlopen(req)
    return json.loads(res.read())


def api_get(path):
    res = urllib.request.urlopen(f"{BASE_URL}{path}")
    return json.loads(res.read())


def insert_test_batch(batch_id, compound):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO intake_batches
           (batch_doc_id, compound_name, zn_concentration_grade, batch_qty_kg,
            manufacture_date, expiry_date, days_to_expiry, source_location,
            source_type, intake_status, compliance_status)
           VALUES (?, ?, 'N/A', 10.0, '01-Jan-2024', '01-Jan-2026', -100,
                   'Kochi, Kerala', 'Retail Pharmacy', 'Pending Review', NULL)""",
        (batch_id, compound)
    )
    conn.commit()
    conn.close()


def cleanup_test_batch(batch_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM intake_batches WHERE batch_doc_id = ?", (batch_id,))
    conn.commit()
    conn.close()


def test_scenario_1_valid_compound():
    """Scenario 1: Valid Zinc Sulphate from Odisha -> full pipeline success."""
    print("=" * 60)
    print("SCENARIO 1: Valid approved compound (Zinc Sulphate, Odisha)")
    print("=" * 60)
    data = api_post("/api/process_batch/BATCH-ZI2026-1014")
    print(f"  Pipeline complete: {data['pipeline_complete']}")
    print(f"  Compliance: {data['compliance']['status']}")
    print(f"  Match: {data['matching']['target_state']} ({data['matching']['match_type']})")
    print(f"  Dosage: {data['dosage']['type']} - {data['dosage'].get('rate_kg_ha', data['dosage'].get('spec'))}")
    assert data["pipeline_complete"] is True
    assert data["compliance"]["status"] == "Accepted"
    assert data["matching"]["matched"] is True
    print("  PASSED\n")


def test_scenario_2_invalid_compound():
    """Scenario 2: Zincovit -> rejected at compliance."""
    print("=" * 60)
    print("SCENARIO 2: Invalid compound (Zincovit)")
    print("=" * 60)
    insert_test_batch("BATCH-TEST-ZINCOVIT-API", "Zincovit")
    data = api_post("/api/process_batch/BATCH-TEST-ZINCOVIT-API")
    print(f"  Pipeline complete: {data['pipeline_complete']}")
    print(f"  Stopped at: {data['stopped_at']}")
    print(f"  Compliance: {data['compliance']['status']}")
    print(f"  Reason: {data['compliance']['reason']}")
    assert data["pipeline_complete"] is False
    assert data["stopped_at"] == "compliance"
    assert data["compliance"]["status"] == "Rejected"
    assert "matching" not in data  # Pipeline should not continue
    cleanup_test_batch("BATCH-TEST-ZINCOVIT-API")
    print("  PASSED\n")


def test_scenario_3_soil_match():
    """Scenario 3: Same-state soil deficiency match."""
    print("=" * 60)
    print("SCENARIO 3: Soil-deficiency match (Odisha/Zinc)")
    print("=" * 60)
    data = api_post("/api/process_batch/BATCH-ZI2026-1014")
    print(f"  Target: {data['matching']['target_state']}")
    print(f"  Type: {data['matching']['match_type']}")
    assert data["matching"]["target_state"] == "Odisha"
    assert data["matching"]["match_type"] == "same_state"
    print("  PASSED\n")


def test_scenario_4_fallback_match():
    """Scenario 4: Kerala (not_usable) -> fallback match."""
    print("=" * 60)
    print("SCENARIO 4: Fallback match (Kerala/Potassium Chloride)")
    print("=" * 60)
    data = api_post("/api/process_batch/BATCH-PO2026-1004")
    print(f"  Source: Kerala")
    print(f"  Target: {data['matching']['target_state']}")
    print(f"  Type: {data['matching']['match_type']}")
    print(f"  Distance: {data['matching'].get('distance_km')} km")
    assert data["matching"]["matched"] is True
    assert data["matching"]["match_type"] == "nearest_fallback"
    assert data["matching"]["target_state"] != "Kerala"
    print("  PASSED\n")


def test_scenario_5_ferrous_sulphate():
    """Scenario 5: Ferrous Sulphate -> foliar spray, NOT soil application."""
    print("=" * 60)
    print("SCENARIO 5: Ferrous Sulphate -> foliar spray (CRITICAL)")
    print("=" * 60)
    data = api_post("/api/process_batch/BATCH-FE2025-1007")
    print(f"  Dosage type: {data['dosage']['type']}")
    print(f"  Spec: {data['dosage'].get('spec')}")
    assert data["dosage"]["type"] == "foliar_spray"
    assert data["dosage"]["spec"] is not None
    assert "rate_kg_ha" not in data["dosage"]
    print("  PASSED\n")


def test_scenario_6_severity_tiers():
    """Scenario 6: Verify dosage amounts are correct."""
    print("=" * 60)
    print("SCENARIO 6: Dosage severity tiers (via direct module)")
    print("=" * 60)
    # Already verified in test_dosage.py, confirm via API stats
    data = api_post("/api/process_batch/BATCH-PO2024-1001")
    # Potassium Chloride, default Medium severity
    print(f"  Compound: {data['dosage']['compound']}")
    print(f"  Rate: {data['dosage']['rate_kg_ha']} (base: {data['dosage']['base_rate_kg_ha']})")
    print(f"  Multiplier: {data['dosage']['severity_multiplier']}")
    assert data["dosage"]["rate_kg_ha"] == 30.0  # Medium = 1.0x
    assert data["dosage"]["severity_multiplier"] == 1.0
    print("  PASSED\n")


def test_scenario_7_invalid_input():
    """Scenario 7: Non-existent batch -> clear error."""
    print("=" * 60)
    print("SCENARIO 7: Invalid input (non-existent batch)")
    print("=" * 60)
    data = api_post("/api/process_batch/BATCH-DOES-NOT-EXIST")
    print(f"  Status: {data['compliance']['status']}")
    print(f"  Reason: {data['compliance']['reason']}")
    assert data["compliance"]["status"] == "Error"
    print("  PASSED\n")


if __name__ == "__main__":
    print("\n--- Running End-to-End Pipeline Tests ---\n")

    test_scenario_1_valid_compound()
    test_scenario_2_invalid_compound()
    test_scenario_3_soil_match()
    test_scenario_4_fallback_match()
    test_scenario_5_ferrous_sulphate()
    test_scenario_6_severity_tiers()
    test_scenario_7_invalid_input()

    print("=" * 60)
    print("ALL 7 SCENARIOS PASSED")
    print("=" * 60)
