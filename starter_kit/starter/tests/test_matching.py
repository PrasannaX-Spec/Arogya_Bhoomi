"""
Test script for Module 2: Soil-Deficiency Matching

Tests:
1. Zinc Sulphate batch from Odisha (same-state match)
2. Ferrous Sulphate batch from Haryana (same-state match)
3. Potassium Chloride batch from Kerala (fallback match, Kerala is not_usable)
4. Batch not accepted should return error
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.intake import check_compliance, DB_PATH
from modules.matching import find_match


def ensure_compliance():
    """Run compliance on all pending batches so we can test matching."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    pending = conn.execute(
        "SELECT batch_doc_id FROM intake_batches WHERE compliance_status IS NULL"
    ).fetchall()
    conn.close()

    for row in pending:
        check_compliance(row["batch_doc_id"])


def test_same_state_match_odisha():
    """Test 1: Zinc Sulphate from Bhubaneswar, Odisha -> same-state match."""
    print("=" * 60)
    print("TEST 1: Zinc Sulphate from Odisha (same-state match)")
    print("=" * 60)

    # BATCH-ZI2026-1014: Zinc Sulphate from Bhubaneswar, Odisha
    result = find_match("BATCH-ZI2026-1014")
    print(f"  Matched: {result.get('matched')}")
    print(f"  Target State: {result.get('target_state')}")
    print(f"  Match Type: {result.get('match_type')}")
    print(f"  Reason: {result.get('reason')}")

    assert result["matched"] is True
    assert result["target_state"] == "Odisha"
    assert result["match_type"] == "same_state"
    print("  PASSED - Same-state match for Odisha/Zinc Sulphate\n")


def test_same_state_match_haryana():
    """Test 2: Ferrous Sulphate from Hisar, Haryana -> same-state match."""
    print("=" * 60)
    print("TEST 2: Ferrous Sulphate from Haryana (same-state match)")
    print("=" * 60)

    # BATCH-FE2026-1002 is from Coimbatore, Tamil Nadu. Let's use
    # BATCH-FE2025-1007 from Hisar, Haryana instead.
    result = find_match("BATCH-FE2025-1007")
    print(f"  Matched: {result.get('matched')}")
    print(f"  Target State: {result.get('target_state')}")
    print(f"  Match Type: {result.get('match_type')}")
    print(f"  Reason: {result.get('reason')}")

    assert result["matched"] is True
    assert result["target_state"] == "Haryana"
    assert result["match_type"] == "same_state"
    print("  PASSED - Same-state match for Haryana/Ferrous Sulphate\n")


def test_fallback_match_kerala():
    """Test 3: Potassium Chloride from Kochi, Kerala -> fallback match."""
    print("=" * 60)
    print("TEST 3: Potassium Chloride from Kerala (fallback match)")
    print("=" * 60)

    # BATCH-PO2026-1004: Potassium Chloride from Kochi, Kerala
    # Kerala is 'not_usable' - should trigger fallback
    result = find_match("BATCH-PO2026-1004")
    print(f"  Matched: {result.get('matched')}")
    print(f"  Target State: {result.get('target_state')}")
    print(f"  Match Type: {result.get('match_type')}")
    print(f"  Reason: {result.get('reason')}")
    print(f"  Distance: {result.get('distance_km')} km")

    assert result["matched"] is True, f"Should find a fallback match: {result}"
    assert result["match_type"] == "nearest_fallback"
    assert result["target_state"] != "Kerala"
    print(f"  PASSED - Fallback match to {result['target_state']}\n")


def test_rejected_batch():
    """Test 4: Non-accepted batch should return error."""
    print("=" * 60)
    print("TEST 4: Non-accepted batch should return error")
    print("=" * 60)

    # Insert a rejected batch
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO intake_batches
           (batch_doc_id, compound_name, zn_concentration_grade, batch_qty_kg,
            manufacture_date, expiry_date, days_to_expiry, source_location,
            source_type, intake_status, compliance_status)
           VALUES ('BATCH-TEST-REJECTED', 'Zincovit', 'N/A', 10.0,
                   '01-Jan-2024', '01-Jan-2026', -100,
                   'Test Location, Test State', 'Retail Pharmacy',
                   'Pending Review', 'Rejected')"""
    )
    conn.commit()
    conn.close()

    result = find_match("BATCH-TEST-REJECTED")
    print(f"  Error: {result.get('error')}")

    assert "error" in result
    assert "not accepted" in result["error"].lower()
    print("  PASSED - Rejected batch correctly blocked from matching\n")

    # Cleanup
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM intake_batches WHERE batch_doc_id = 'BATCH-TEST-REJECTED'")
    conn.commit()
    conn.close()


def test_eligible_candidates_generation():
    """Test 5: Verify find_match generates up to 4 ranked eligible candidate destinations."""
    print("=" * 60)
    print("TEST 5: Dynamic Top 4 Candidates Generation")
    print("=" * 60)

    result = find_match("BATCH-ZI2026-1014")
    assert "eligible_candidates" in result
    candidates = result["eligible_candidates"]

    print(f"  Total Candidates Generated: {len(candidates)}")
    for cand in candidates:
        print(f"    Rank #{cand['rank']}: {cand['target_state']} ({cand['distance_km']} km) - Suggested: {cand['is_suggested']}")

    assert len(candidates) > 0
    assert len(candidates) <= 4
    assert candidates[0]["is_suggested"] is True
    assert candidates[0]["rank"] == 1
    print("  PASSED - Dynamic 4 candidate destination generation verified\n")


if __name__ == "__main__":
    print("\n--- Running Module 2 (Soil-Deficiency Matching) Tests ---\n")

    ensure_compliance()

    test_same_state_match_odisha()
    test_same_state_match_haryana()
    test_fallback_match_kerala()
    test_rejected_batch()
    test_eligible_candidates_generation()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
