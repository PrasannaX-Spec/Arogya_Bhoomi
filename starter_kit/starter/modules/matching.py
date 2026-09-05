"""
Module 2: Soil-Deficiency Matching Engine
Matches accepted batches to regions with documented soil deficiency.

Logic:
1. Verify batch has compliance_status = 'Accepted'
2. Resolve batch source_location to state via geolocation
3. Same-state match: check if source state is 'usable' AND has the compound
4. Fallback match: search all other 'usable' states for the compound
5. No match: return clear indication
"""

import sqlite3
import os
from modules.geolocation import resolve_location, distance_km

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")


def get_db_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def find_match(batch_doc_id):
    """
    Find a soil-deficiency match for an accepted batch.

    Steps:
    1. Look up batch, verify compliance_status = 'Accepted'
    2. Resolve source_location to state
    3. Check same-state match
    4. If not, find fallback match from all usable states
    5. Return match result with target state and reason

    Args:
        batch_doc_id: The batch document ID to match.

    Returns:
        dict with match result including 'matched', 'target_state', 'reason',
        and location details. Or dict with 'error' if batch is invalid.
    """
    conn = get_db_connection()
    try:
        # Step 1: Look up the batch
        batch = conn.execute(
            "SELECT * FROM intake_batches WHERE batch_doc_id = ?",
            (batch_doc_id,)
        ).fetchone()

        if batch is None:
            return {"error": f"Batch '{batch_doc_id}' not found"}

        if batch["compliance_status"] != "Accepted":
            return {
                "error": "Batch not accepted, cannot match",
                "compliance_status": batch["compliance_status"]
            }

        compound_name = batch["compound_name"]
        source_location = batch["source_location"]

        # Step 2: Resolve source location
        geo_result = resolve_location(source_location)
        if "error" in geo_result:
            return {
                "error": f"Could not resolve location: {geo_result['error']}",
                "source_location": source_location
            }

        source_state = geo_result["state"]
        source_coords = (geo_result["latitude"], geo_result["longitude"])

        # Step 3: Check same-state match
        state_row = conn.execute(
            "SELECT * FROM soil_deficiency WHERE state = ?",
            (source_state,)
        ).fetchone()

        if state_row and state_row["status"] == "usable":
            usable_compounds = [c.strip() for c in state_row["usable_compounds"].split(",")]
            if compound_name in usable_compounds:
                return {
                    "matched": True,
                    "target_state": source_state,
                    "match_type": "same_state",
                    "reason": "Same-state deficiency match",
                    "compound": compound_name,
                    "source_location": source_location,
                    "source_state": source_state,
                    "source_coordinates": {"lat": source_coords[0], "lon": source_coords[1]},
                    "deficient_nutrients": state_row["deficient_nutrients"],
                }

        # Step 4: Fallback — search all other usable states
        all_usable = conn.execute(
            "SELECT * FROM soil_deficiency WHERE status = 'usable'"
        ).fetchall()

        best_match = None
        best_distance = float("inf")

        for row in all_usable:
            if row["state"] == source_state:
                continue  # Already checked same-state

            usable_compounds = [c.strip() for c in row["usable_compounds"].split(",")]
            if compound_name in usable_compounds:
                # Compute distance to this state for nearest-match
                target_geo = resolve_location(f", {row['state']}")
                if "error" not in target_geo:
                    target_coords = (target_geo["latitude"], target_geo["longitude"])
                    dist = distance_km(source_coords, target_coords)

                    if dist < best_distance:
                        best_distance = dist
                        best_match = {
                            "matched": True,
                            "target_state": row["state"],
                            "match_type": "nearest_fallback",
                            "reason": "Nearest available match, not same-state",
                            "compound": compound_name,
                            "source_location": source_location,
                            "source_state": source_state,
                            "source_coordinates": {"lat": source_coords[0], "lon": source_coords[1]},
                            "target_coordinates": {"lat": target_coords[0], "lon": target_coords[1]},
                            "distance_km": round(dist, 1),
                            "deficient_nutrients": row["deficient_nutrients"],
                        }

        if best_match:
            return best_match

        # Step 5: No match found anywhere
        return {
            "matched": False,
            "reason": f"No usable state deficient in this compound ({compound_name})",
            "compound": compound_name,
            "source_location": source_location,
            "source_state": source_state,
        }
    finally:
        conn.close()
