"""
Module 3: Dosage Recommendation
Returns ICAR-based dosage recommendations with GRD +/-25% severity adjustment.

CRITICAL: Ferrous Sulphate does NOT use soil kg/ha dosage.
It uses a foliar spray specification instead.
The base_rate_kg_ha is NULL for Ferrous Sulphate — do NOT attempt
to multiply a null rate by anything.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")

VALID_SEVERITY_TIERS = ("Low", "Medium", "High")


def get_db_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_dosage(compound_name, severity_tier):
    """
    Look up the dosage recommendation for a compound and severity tier.

    For Zinc Sulphate and Potassium Chloride (soil application):
        Returns base_rate_kg_ha * severity_adjustment[tier]

    For Ferrous Sulphate (foliar spray):
        Returns the foliar_spec from the raw JSON — NO rate multiplication.

    Args:
        compound_name: One of the 3 approved compound names.
        severity_tier: One of "Low", "Medium", "High".

    Returns:
        dict with dosage recommendation details.
    """
    if severity_tier not in VALID_SEVERITY_TIERS:
        return {
            "error": f"Invalid severity tier '{severity_tier}'. Must be one of: {VALID_SEVERITY_TIERS}"
        }

    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT * FROM dosage_rates WHERE compound_name = ?",
            (compound_name,)
        ).fetchone()

        if row is None:
            return {"error": f"Compound '{compound_name}' not found in dosage_rates"}

        base_rate = row["base_rate_kg_ha"]
        raw_json = json.loads(row["raw_json"])
        source = row["source"]

        # CRITICAL BRANCH: Ferrous Sulphate foliar spray path
        if base_rate is None:
            # This is the Ferrous Sulphate case — return foliar specification
            foliar_spec = raw_json.get("foliar_spec")
            if foliar_spec is None:
                return {"error": f"Compound '{compound_name}' has no base_rate and no foliar_spec"}

            return {
                "type": "foliar_spray",
                "compound": compound_name,
                "severity_tier": severity_tier,
                "spec": foliar_spec,
                "note": "ICAR recommends foliar route for Fe, not soil application",
                "source": source,
            }

        # Normal soil application path (Zinc Sulphate, Potassium Chloride)
        severity_adjustment = raw_json.get("severity_adjustment", {})
        multiplier = severity_adjustment.get(severity_tier, 1.0)

        adjusted_rate = round(base_rate * multiplier, 2)
        unit = row["unit"]

        return {
            "type": "soil_application",
            "compound": compound_name,
            "severity_tier": severity_tier,
            "base_rate_kg_ha": base_rate,
            "severity_multiplier": multiplier,
            "rate_kg_ha": adjusted_rate,
            "unit": unit,
            "source": source,
        }
    finally:
        conn.close()
