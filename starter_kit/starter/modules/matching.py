"""
Module 2: Soil-Deficiency Matching Engine
Matches accepted batches to regions with documented soil deficiency.

Logic:
1. Verify batch has compliance_status = 'Accepted'
2. Resolve batch source_location to state via geolocation
3. Map compound to target elemental nutrient(s) (Zn, Fe, K, S)
4. Same-state match: check if source state is 'usable' AND deficient in target nutrient
5. Fallback match: search all other 'usable' states deficient in target nutrient
6. Rank eligible candidates by nutrient deficiency relevance and Haversine distance
7. Return match result with target state, reason, and ranked eligible candidates (up to 4 max)
"""

import sqlite3
import os
from modules.geolocation import resolve_location, distance_km

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")

COMPOUND_NUTRIENTS = {
    "Zinc Sulphate": ["Zn", "S"],
    "Ferrous Sulphate": ["Fe", "S"],
    "Potassium Chloride": ["K"],
}


def get_db_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_compound_target_nutrients(compound_name):
    """
    Map compound name to active elemental nutrient(s).
    Primary active nutrient is the first element in the list.
    """
    if not compound_name:
        return []
    if compound_name in COMPOUND_NUTRIENTS:
        return COMPOUND_NUTRIENTS[compound_name]

    nutrients = []
    c_lower = compound_name.lower()
    if "zinc" in c_lower:
        nutrients.append("Zn")
    if "ferrous" in c_lower or "iron" in c_lower:
        nutrients.append("Fe")
    if "potassium" in c_lower:
        nutrients.append("K")
    if "sulphate" in c_lower or "sulfate" in c_lower:
        nutrients.append("S")
    return nutrients or [compound_name]


def find_match(batch_doc_id):
    """
    Find a soil-deficiency match for an accepted batch.

    Steps:
    1. Look up batch, verify compliance_status = 'Accepted'
    2. Resolve source_location to state
    3. Determine target elemental nutrients for compound
    4. Search all usable states with documented deficiency for that nutrient
    5. Rank candidate states by deficiency relevance and Haversine distance
    6. Return top match result and top 4 eligible candidates

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

        # Step 3: Determine target nutrients
        target_nutrients = get_compound_target_nutrients(compound_name)
        primary_nutrient = target_nutrients[0] if target_nutrients else None

        # Step 4: Search all usable states for nutrient deficiency match
        all_usable = conn.execute(
            "SELECT * FROM soil_deficiency WHERE status = 'usable'"
        ).fetchall()

        candidates = []
        for row in all_usable:
            state_name = row["state"]
            deficient_nutrients = [n.strip() for n in (row["deficient_nutrients"] or "").split(",") if n.strip()]
            usable_compounds = [c.strip() for c in (row["usable_compounds"] or "").split(",") if c.strip()]

            # Determine nutrient eligibility
            is_compound_match = compound_name in usable_compounds
            is_primary_match = primary_nutrient and (primary_nutrient in deficient_nutrients)
            is_secondary_match = any(ntr in deficient_nutrients for ntr in target_nutrients[1:])

            if not (is_compound_match or is_primary_match or is_secondary_match):
                continue  # Skip state if no nutrient deficiency match

            # Geolocation & Distance
            if state_name == source_state:
                target_coords = source_coords
                dist = 0.0
                match_type = "same_state"
                reason = f"Documented {compound_name} deficiency match in {source_state} (Same-State)"
            else:
                target_geo = resolve_location(f", {state_name}")
                if "error" in target_geo:
                    continue
                target_coords = (target_geo["latitude"], target_geo["longitude"])
                dist = distance_km(source_coords, target_coords)
                match_type = "nearest_fallback"
                reason = f"Documented {primary_nutrient or compound_name} deficiency in {state_name} ({round(dist, 1)} km from source)"

            candidates.append({
                "target_state": state_name,
                "match_type": match_type,
                "reason": reason,
                "distance_km": round(dist, 1),
                "deficient_nutrients": row["deficient_nutrients"],
                "is_same_state": (state_name == source_state),
                "is_primary_match": is_primary_match or is_compound_match,
                "is_suggested": False,
                "target_coordinates": {"lat": target_coords[0], "lon": target_coords[1]} if target_coords else None
            })

        # Step 5: Rank candidates transparently
        # Priority:
        # 1. Same-state match (0 km) if available
        # 2. Primary nutrient match (True over False)
        # 3. Proximity to source location (distance_km ascending)
        candidates.sort(key=lambda c: (
            0 if c["is_same_state"] else 1,
            0 if c["is_primary_match"] else 1,
            c["distance_km"]
        ))

        if candidates:
            candidates[0]["is_suggested"] = True

        # Deduplicate and truncate to top 4 max
        seen_states = set()
        unique_candidates = []
        for cand in candidates:
            if cand["target_state"] not in seen_states:
                seen_states.add(cand["target_state"])
                unique_candidates.append(cand)

        eligible_candidates = unique_candidates[:4]
        for idx, cand in enumerate(eligible_candidates, start=1):
            cand["rank"] = idx

        if eligible_candidates:
            top_match = eligible_candidates[0]
            return {
                "matched": True,
                "target_state": top_match["target_state"],
                "match_type": top_match["match_type"],
                "reason": top_match["reason"],
                "compound": compound_name,
                "source_location": source_location,
                "source_state": source_state,
                "source_coordinates": {"lat": source_coords[0], "lon": source_coords[1]},
                "target_coordinates": top_match.get("target_coordinates"),
                "distance_km": top_match.get("distance_km", 0.0),
                "deficient_nutrients": top_match["deficient_nutrients"],
                "eligible_candidates": eligible_candidates,
            }

        # Step 6: No match found anywhere
        return {
            "matched": False,
            "reason": f"No usable state deficient in this compound/nutrient ({compound_name})",
            "compound": compound_name,
            "source_location": source_location,
            "source_state": source_state,
            "eligible_candidates": [],
        }
    finally:
        conn.close()

