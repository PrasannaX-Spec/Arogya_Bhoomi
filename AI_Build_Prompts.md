# AI Build Prompts
## Copy-paste these, in order, to Claude Code / Cursor / any AI coding assistant

Give the AI access to your unzipped `starter/` folder before pasting these — it needs to see `load_data.py` and the `data/*.json` files to get the schema right. Do each prompt one at a time, verify the check before moving to the next.

---

### Prompt 1 — Module 1: Intake & Compliance

```
I have a SQLite database (app.db) built by load_data.py in this folder. The
intake_batches table has this schema:

batch_doc_id, compound_name, zn_concentration_grade, batch_qty_kg,
manufacture_date, expiry_date, days_to_expiry, source_location, source_type,
intake_status, compliance_status

The compound_reference table has: compound_name, nutrient, product_reference,
agri_precedent, water_soluble.

Write modules/intake.py with a function `check_compliance(batch_doc_id)` that:
1. Looks up the batch in intake_batches
2. Checks if its compound_name exactly matches a row in compound_reference
   (case-sensitive exact match on the generic name, not a fuzzy match)
3. If it matches, update that batch's compliance_status to "Accepted" and
   return {"status": "Accepted", "reason": None}
4. If it does not match, update compliance_status to "Rejected" and return
   {"status": "Rejected", "reason": f"'{compound_name}' is not an approved
   single-compound medicine"}
5. Also write a function `run_all_pending()` that runs check_compliance on
   every batch where compliance_status IS NULL, and returns a summary count
   of accepted vs rejected

Do not use fuzzy matching or partial string matching for the compound name
check — it must be an exact match, since brand names like "Zincovit" should
NOT match "Zinc Sulphate" even though both relate to zinc.

Write a small test script tests/test_intake.py that:
- Runs run_all_pending() on the existing 45 demo rows and prints the
  accepted/rejected counts
- Manually inserts a new row with compound_name = "Zincovit" and confirms
  check_compliance() rejects it with a reason mentioning it's not approved
- Confirms a row with compound_name = "Zinc Sulphate" is accepted
```

**Check before moving on:** run the test script. All 45 demo rows should accept (none are combination products). The manually-added "Zincovit" row must reject.

---

### Prompt 2 — Module 4: Geolocation

```
Install the indiapins Python package. Write modules/geolocation.py with a
function `resolve_location(location_string)` that takes a string like
"Hisar, Haryana" or a pincode, and returns a dict with district, state,
latitude, longitude. If indiapins can't resolve a free-text city/state
string directly, look up the district/state by matching against known
Indian place names, and use a static district-centroid lookup as a fallback
for lat/long (you can hardcode a small dictionary of the ~30 state capitals'
coordinates as a fallback if indiapins only supports pincode lookup).

Also write a function `distance_km(loc1, loc2)` using the haversine formula
on two (lat, lon) pairs.

Write tests/test_geolocation.py that resolves these 3 known source_locations
from my demo_intake.csv and prints the result: "Hisar, Haryana",
"Bhubaneswar, Odisha", "Coimbatore, Tamil Nadu" — confirm each returns a
sensible state field matching what's in the string.
```

**Check before moving on:** all 3 test locations return the correct state name, and coordinates are non-null.

---

### Prompt 3 — Module 2: Soil-Deficiency Matching

```
I have a soil_deficiency table in app.db with columns: state,
deficient_nutrients (comma-separated), usable_compounds (comma-separated),
status ('usable' or 'not_usable').

I have modules/geolocation.py with a resolve_location() function already
built (import it).

Write modules/matching.py with a function `find_match(batch_doc_id)` that:
1. Looks up the batch in intake_batches (must have compliance_status =
   'Accepted' — if not, return {"error": "batch not accepted, cannot match"})
2. Resolves the batch's source_location to get its state
3. Checks if that state's row in soil_deficiency has status = 'usable' AND
   the batch's compound_name appears in that state's usable_compounds
4. If yes, return {"matched": True, "target_state": <that state>,
   "reason": "same-state deficiency match"}
5. If the source state itself is not a usable match, search all other
   'usable' states whose usable_compounds includes this batch's compound,
   and return the first one found as a fallback match, with
   "reason": "nearest available match, not same-state"
6. If no usable state anywhere has this compound in its usable_compounds
   list, return {"matched": False, "reason": "no usable state deficient in
   this compound"}

Write tests/test_matching.py that:
- Runs find_match() on 3 accepted batches from different states and prints
  the result
- Deliberately tests a batch whose source_location is in Kerala (not in the
  usable states list) and confirms the function still returns a valid
  fallback match in a different usable state, not an error
```

**Check before moving on:** matches make sense against your own State_Match_FILTERED spreadsheet — manually verify at least 2 results by eye.

---

### Prompt 4 — Module 3: Dosage Recommendation

```
I have a dosage_rates table in app.db with columns: compound_name,
base_rate_kg_ha, unit, source, raw_json (a JSON string with the full
record, including a "severity_adjustment" dict like {"Low": 1.25,
"Medium": 1.0, "High": 0.75}, and for Ferrous Sulphate specifically a
"foliar_spec" field instead of a usable base_rate_kg_ha, since
base_rate_kg_ha is NULL for that compound).

Write modules/dosage.py with a function `get_dosage(compound_name,
severity_tier)` where severity_tier is one of "Low", "Medium", "High":
1. Look up the compound in dosage_rates
2. If base_rate_kg_ha is NOT NULL: return {"type": "soil_application",
   "rate_kg_ha": base_rate_kg_ha * severity_adjustment[severity_tier],
   "unit": unit, "source": source}
3. If base_rate_kg_ha IS NULL (this is the Ferrous Sulphate case): return
   {"type": "foliar_spray", "spec": <the foliar_spec value from raw_json>,
   "source": source} — do NOT attempt to multiply a null rate by anything

Write tests/test_dosage.py that:
- Calls get_dosage("Zinc Sulphate", "Low") and confirms it returns a
  soil_application type with a rate 25% higher than the base rate
- Calls get_dosage("Ferrous Sulphate", "Medium") and confirms it returns a
  foliar_spray type, not a crash or a null rate
- Calls get_dosage("Potassium Chloride", "High") and confirms the rate is
  25% lower than base
```

**Check before moving on:** the Ferrous Sulphate test must NOT throw an error or return a null/zero rate — if it does, the branching logic was skipped. This is the exact bug I warned about earlier.

---

### Prompt 5 — End-to-end wiring

```
I have modules/intake.py, modules/matching.py, modules/dosage.py, and
modules/geolocation.py, each already tested individually.

Write a Flask app.py with a single endpoint POST /process_batch/<batch_doc_id>
that runs the full pipeline in sequence:
1. Call check_compliance(batch_doc_id) from intake.py
2. If rejected, return the rejection reason immediately, do not continue
3. If accepted, call find_match(batch_doc_id) from matching.py
4. If no match found, return that result, do not continue
5. If matched, determine a severity_tier (for this prototype, hardcode
   "Medium" as the default — note this as a simplification in a code
   comment, since we don't have real soil-test severity data per batch yet)
6. Call get_dosage(compound_name, severity_tier) from dosage.py
7. Return a combined JSON response with all four modules' outputs:
   compliance result, geolocation result, match result, dosage result

Write a manual test: pick 3 batch_doc_ids from the demo data — one that
should end up Accepted+Matched+Dosed successfully, and after temporarily
inserting one fake "Zincovit" row, confirm it stops at step 2 with a clean
rejection message and does not attempt matching or dosage.
```

**Check before moving on:** this is your Checkpoint 6. If this works, you have a demoable product even with zero UI.

---

## Rules for every prompt above (tell the AI this once, upfront, if it starts improvising)

- Do not invent new database columns or tables not listed above
- Do not fuzzy-match compound names — exact match only
- Do not skip the Ferrous Sulphate foliar-spray branch — it is not an edge case, it's a required path
- Do not add authentication, Docker, or cloud deployment — out of scope
- If something in the data looks wrong or missing, ask, don't guess
