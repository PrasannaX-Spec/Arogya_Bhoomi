"""
Test script for Module 1: Intake & Compliance

Tests:
1. run_all_pending() on the 45 demo rows → all should accept
2. Manually inserted "Zincovit" row → should be rejected
3. "Zinc Sulphate" row → should be accepted
"""

import sys
import os
import sqlite3

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.intake import check_compliance, run_all_pending, DB_PATH


def reset_compliance_status():
    """Reset all compliance_status to NULL for a clean test run."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE intake_batches SET compliance_status = NULL")
    conn.commit()
    conn.close()


def insert_test_row(batch_doc_id, compound_name):
    """Insert a test row for validation testing."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO intake_batches
           (batch_doc_id, compound_name, zn_concentration_grade, batch_qty_kg,
            manufacture_date, expiry_date, days_to_expiry, source_location,
            source_type, intake_status, compliance_status)
           VALUES (?, ?, 'N/A', 10.0, '01-Jan-2024', '01-Jan-2026', -100,
                   'Test Location, Test State', 'Retail Pharmacy', 'Pending Review', NULL)""",
        (batch_doc_id, compound_name)
    )
    conn.commit()
    conn.close()


def cleanup_test_row(batch_doc_id):
    """Remove test rows after testing."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM intake_batches WHERE batch_doc_id = ?", (batch_doc_id,))
    conn.commit()
    conn.close()


def test_run_all_pending():
    """Test 1: All 45 demo rows should be accepted."""
    print("=" * 60)
    print("TEST 1: run_all_pending() on 45 demo rows")
    print("=" * 60)

    reset_compliance_status()
    result = run_all_pending()

    print(f"  Total processed: {result['total_processed']}")
    print(f"  Accepted: {result['accepted']}")
    print(f"  Rejected: {result['rejected']}")

    assert result["accepted"] == 45, f"Expected 45 accepted, got {result['accepted']}"
    assert result["rejected"] == 0, f"Expected 0 rejected, got {result['rejected']}"
    print("  PASSED - All 45 demo rows accepted\n")


def test_zincovit_rejection():
    """Test 2: A 'Zincovit' batch must be rejected."""
    print("=" * 60)
    print("TEST 2: 'Zincovit' batch should be rejected")
    print("=" * 60)

    test_id = "BATCH-TEST-ZINCOVIT"
    insert_test_row(test_id, "Zincovit")

    result = check_compliance(test_id)
    print(f"  Status: {result['status']}")
    print(f"  Reason: {result['reason']}")

    assert result["status"] == "Rejected", f"Expected 'Rejected', got '{result['status']}'"
    assert "not an approved" in result["reason"], f"Reason should mention 'not approved'"
    print("  PASSED - Zincovit correctly rejected\n")

    cleanup_test_row(test_id)


def test_zinc_sulphate_acceptance():
    """Test 3: A 'Zinc Sulphate' batch must be accepted."""
    print("=" * 60)
    print("TEST 3: 'Zinc Sulphate' batch should be accepted")
    print("=" * 60)

    test_id = "BATCH-TEST-ZINCSULPHATE"
    insert_test_row(test_id, "Zinc Sulphate")

    result = check_compliance(test_id)
    print(f"  Status: {result['status']}")
    print(f"  Reason: {result['reason']}")

    assert result["status"] == "Accepted", f"Expected 'Accepted', got '{result['status']}'"
    assert result["reason"] is None, f"Reason should be None for accepted batch"
    print("  PASSED - Zinc Sulphate correctly accepted\n")

    cleanup_test_row(test_id)


def test_nonexistent_batch():
    """Test 4: A non-existent batch should return an error."""
    print("=" * 60)
    print("TEST 4: Non-existent batch should return error")
    print("=" * 60)

    result = check_compliance("BATCH-DOES-NOT-EXIST")
    print(f"  Status: {result['status']}")
    print(f"  Reason: {result['reason']}")

    assert result["status"] == "Error", f"Expected 'Error', got '{result['status']}'"
    print("  PASSED - Non-existent batch handled gracefully\n")


if __name__ == "__main__":
    print("\n--- Running Module 1 (Intake & Compliance) Tests ---\n")

    test_run_all_pending()
    test_zincovit_rejection()
    test_zinc_sulphate_acceptance()
    test_nonexistent_batch()

    # Reset compliance status for clean state after tests
    reset_compliance_status()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
