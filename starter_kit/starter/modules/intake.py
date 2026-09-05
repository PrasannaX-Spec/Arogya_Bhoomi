"""
Module 1: Intake & Compliance
Validates expired pharmaceutical batches against the approved compound whitelist.

Rules:
- Exact case-sensitive match of compound_name against compound_reference table
- No fuzzy matching, no brand name matching
- Updates compliance_status in intake_batches table
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")


def get_db_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_compliance(batch_doc_id):
    """
    Check if a batch's compound_name exactly matches an approved compound.

    Args:
        batch_doc_id: The batch document ID to check.

    Returns:
        dict with 'status' ('Accepted' or 'Rejected') and 'reason' (None if accepted,
        explanation string if rejected).
    """
    conn = get_db_connection()
    try:
        # Look up the batch
        batch = conn.execute(
            "SELECT * FROM intake_batches WHERE batch_doc_id = ?",
            (batch_doc_id,)
        ).fetchone()

        if batch is None:
            return {"status": "Error", "reason": f"Batch '{batch_doc_id}' not found"}

        compound_name = batch["compound_name"]

        # Exact match against approved compound list
        approved = conn.execute(
            "SELECT compound_name FROM compound_reference WHERE compound_name = ?",
            (compound_name,)
        ).fetchone()

        if approved is not None:
            conn.execute(
                "UPDATE intake_batches SET compliance_status = 'Accepted' WHERE batch_doc_id = ?",
                (batch_doc_id,)
            )
            conn.commit()
            return {"status": "Accepted", "reason": None}
        else:
            reason = f"'{compound_name}' is not an approved single-compound medicine"
            conn.execute(
                "UPDATE intake_batches SET compliance_status = 'Rejected' WHERE batch_doc_id = ?",
                (batch_doc_id,)
            )
            conn.commit()
            return {"status": "Rejected", "reason": reason}
    finally:
        conn.close()


def run_all_pending():
    """
    Run compliance check on every batch where compliance_status IS NULL.

    Returns:
        dict with 'accepted' count, 'rejected' count, and 'details' list.
    """
    conn = get_db_connection()
    try:
        pending = conn.execute(
            "SELECT batch_doc_id FROM intake_batches WHERE compliance_status IS NULL"
        ).fetchall()

        accepted = 0
        rejected = 0
        details = []

        for row in pending:
            result = check_compliance(row["batch_doc_id"])
            if result["status"] == "Accepted":
                accepted += 1
            elif result["status"] == "Rejected":
                rejected += 1
            details.append({"batch_doc_id": row["batch_doc_id"], **result})

        return {
            "accepted": accepted,
            "rejected": rejected,
            "total_processed": accepted + rejected,
            "details": details
        }
    finally:
        conn.close()
