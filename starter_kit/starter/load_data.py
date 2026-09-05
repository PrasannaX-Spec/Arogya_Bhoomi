"""
load_data.py
Run this once to set up your SQLite database from the /data reference files.

Usage: python load_data.py
Creates app.db in the current directory with all 4 tables populated.
"""

import sqlite3
import json
import csv

DB_PATH = "app.db"


def create_tables(conn):
    conn.executescript("""
    DROP TABLE IF EXISTS compound_reference;
    DROP TABLE IF EXISTS soil_deficiency;
    DROP TABLE IF EXISTS dosage_rates;
    DROP TABLE IF EXISTS intake_batches;

    CREATE TABLE compound_reference (
        compound_name TEXT PRIMARY KEY,
        nutrient TEXT,
        product_reference TEXT,
        agri_precedent TEXT,
        water_soluble INTEGER
    );

    CREATE TABLE soil_deficiency (
        state TEXT PRIMARY KEY,
        deficient_nutrients TEXT,   -- comma-separated
        usable_compounds TEXT,      -- comma-separated
        status TEXT                 -- 'usable' or 'not_usable'
    );

    CREATE TABLE dosage_rates (
        compound_name TEXT,
        base_rate_kg_ha REAL,
        unit TEXT,
        source TEXT,
        raw_json TEXT                -- full record for compounds with non-standard fields (e.g. Fe foliar spec)
    );

    CREATE TABLE intake_batches (
        batch_doc_id TEXT PRIMARY KEY,
        compound_name TEXT,
        zn_concentration_grade TEXT,
        batch_qty_kg REAL,
        manufacture_date TEXT,
        expiry_date TEXT,
        days_to_expiry INTEGER,
        source_location TEXT,
        source_type TEXT,
        intake_status TEXT,          -- original demo status, kept for reference
        compliance_status TEXT        -- set by your Module 1 filter logic, starts NULL
    );
    """)


def load_compounds(conn):
    with open("data/compound_list.json") as f:
        compounds = json.load(f)
    for c in compounds:
        conn.execute(
            "INSERT INTO compound_reference VALUES (?, ?, ?, ?, ?)",
            (c["compound_name"], c["nutrient"], c["product_reference"],
             c["agri_precedent"], int(c["water_soluble"]))
        )
    print(f"Loaded {len(compounds)} compounds")


def load_soil_deficiency(conn):
    with open("data/soil_deficiency.json") as f:
        data = json.load(f)
    for s in data["states"]:
        conn.execute(
            "INSERT INTO soil_deficiency VALUES (?, ?, ?, ?)",
            (s["state"], ",".join(s["deficient_nutrients"]),
             ",".join(s["usable_compounds"]), s["status"])
        )
    print(f"Loaded {len(data['states'])} states")
    print(f"National baseline: {data['national_baseline']}")


def load_dosage(conn):
    with open("data/dosage_table.json") as f:
        data = json.load(f)
    for name, rec in data["compounds"].items():
        conn.execute(
            "INSERT INTO dosage_rates VALUES (?, ?, ?, ?, ?)",
            (name, rec.get("base_rate_kg_ha"), rec.get("unit"),
             rec.get("source"), json.dumps(rec))
        )
    print(f"Loaded dosage rates for {len(data['compounds'])} compounds")


def load_intake(conn):
    with open("data/demo_intake.csv") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            conn.execute(
                """INSERT INTO intake_batches
                   (batch_doc_id, compound_name, zn_concentration_grade, batch_qty_kg,
                    manufacture_date, expiry_date, days_to_expiry, source_location,
                    source_type, intake_status, compliance_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)""",
                (row["batch_doc_id"], row["compound_name"], row.get("zn_concentration_grade"),
                 float(row["batch_qty_kg"]), row["manufacture_date"], row["expiry_date"],
                 int(row["days_to_expiry"]), row["source_location"], row["source_type"],
                 row["intake_status"])
            )
            count += 1
    print(f"Loaded {count} intake batches")


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    load_compounds(conn)
    load_soil_deficiency(conn)
    load_dosage(conn)
    load_intake(conn)
    conn.commit()
    conn.close()
    print(f"\nDone. Database written to {DB_PATH}")
    print("Sanity check: run `sqlite3 app.db` then `.tables` and `SELECT COUNT(*) FROM intake_batches;`")
