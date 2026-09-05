# Product Requirements Document
## Traceable Recovery & Deployment Platform for Micronutrient Compounds from Expired Pharmaceuticals

**Version:** 1.0 (Hackathon Prototype)
**Date:** September 2026

---

## 1. Problem Statement

There is currently no system in India that connects verified, composition-known expired pharmaceutical stock (held by distributors, pharmacies, and hospitals) with regions of documented soil micronutrient deficiency, to enable safe, dosage-controlled agricultural reuse of recoverable mineral compounds.

## 2. Goals (this prototype)

- Demonstrate an end-to-end flow: expired stock intake → compliance filtering → soil-deficiency matching → dosage recommendation
- Prove the coordination logic works using real reference data (soil deficiency %, ICAR dosage rates) and realistic synthetic transaction data
- Show judges a working, navigable demo, not just slides

## 3. Non-Goals (explicitly out of scope)

- Actual chemical extraction (assumed handled by a certified partner facility)
- Logistics/transport routing and last-mile delivery
- Combination-formulation medicines (Zincovit, Fefol, Shelcal, etc.) — single-compound only
- Full ICAR STCR target-yield equations — using the simpler GRD ±25% rule instead
- Compounds beyond Ferrous Sulphate, Zinc Sulphate, Potassium Chloride

## 4. Users

| User | Need |
|---|---|
| Distributor / Pharmacy / Hospital (intake source) | Submit expired stock for verified redistribution instead of standard disposal |
| Platform admin / reviewer | See intake queue, accept/reject batches against compound rules |
| Agricultural body / farmer cooperative (demand side) | See which compounds are available for their region's documented deficiency |

## 5. Core Modules & Requirements

### Module 1 — Verified Intake & Compliance
- Form/API to submit a batch: `batch_doc_id, compound_name, batch_qty_kg, manufacture_date, expiry_date, days_to_expiry, source_location, source_type, zn_concentration_grade (if applicable), compliance_status`
- Rule-based filter: accept only if `compound_name` is one of the 3 approved compounds (matched by generic name, not brand)
- Reject with reason if compound not on approved list, or documentation missing
- Status workflow: `Pending Review → Accepted (Queued for Redistribution) / Accepted (Sent to Partner) / Rejected`

**Acceptance criteria:** Given a batch with `compound_name = "Zincovit"`, system rejects it with reason "combination product not permitted." Given `compound_name = "Zinc Sulphate"` with valid docs, system accepts it.

### Module 2 — Soil-Deficiency Matching Engine
- Ingests static soil deficiency reference data (state-level %, from Soil_Deficiency_Data.docx / State_Match_FILTERED.xlsx)
- Given an accepted batch's source location, find nearest state/district with documented deficiency in that compound's mineral
- Output: a matched pairing (batch → target region)

**Acceptance criteria:** Given an accepted Zinc Sulphate batch from Bhubaneswar, Odisha, system correctly identifies Odisha as zinc-deficient and returns it as a valid match (or nearest alternative if same-state logic requires it).

### Module 3 — Dosage Recommendation (simplified)
- Static lookup table: compound × severity tier (Low/Medium/High) → kg/ha, using GRD ±25% rule from ICAR reference doc
- **Exception — Ferrous Sulphate has no soil kg/ha rate.** ICAR recommends a foliar spray (3-4 sprays of 1.0% ferrous sulphate at weekly intervals) for iron correction, not a soil application rate. `dosage_table.json` encodes this as `base_rate_kg_ha: null` with a separate `foliar_spec` field — Module 3 logic must branch on compound, not assume a uniform kg/ha formula for all three.
- Given a matched region's soil test category, return application rate (or foliar spec, for Fe)

**Acceptance criteria:** Given Zinc Sulphate matched to a "Low" soil-test-K region, system returns GRD + 25% recommended rate, correctly labeled with source (ICAR, Indian Farming 75(06)). Given Ferrous Sulphate in any severity tier, system returns the foliar spray spec, not a null or a crash.

### Module 4 — Geolocation
- Integrate pincode/district → lat-long lookup (open REST API or `indiapins` package)
- Used to compute nearest deficient region to a given source location

**Acceptance criteria:** Given a source pincode, system returns district, state, and coordinates.

## 6. Data Sources (see Data_Requirements_Reference.docx for full detail)

| Category | Status |
|---|---|
| Soil deficiency data | Real (sourced), static reference |
| Expired stock intake | Synthetic demo data (45 rows) |
| Accepted compound list | Real, static (3 compounds) |
| Agronomic dosage | Real (ICAR-sourced), static, GRD ±25% simplification |
| Geolocation | Real, source identified, integration pending |

## 7. Success Metrics (for demo purposes)

- End-to-end flow completes without manual intervention for at least 3 sample batches
- At least one Accepted, one Rejected, and one Pending Review case demoable live
- Matching engine correctly excludes states with no approved-compound deficiency (per FILTERED spreadsheet)

## 8. Known Limitations (state these openly to judges)

- Soil deficiency data is static/demo-sourced, not a live government feed
- Dosage uses simplified GRD ±25% rule, not full STCR equations
- No real distributor/pharmacy has been onboarded — intake is fully synthetic
- Logistics and actual extraction are out of scope, assumed handled by a partner

## 9. Open Questions

- ~~Final tech stack~~ — resolved: Flask + SQLite + `indiapins` + Streamlit (see Tech_Stack.md)
- Whether Module 3 outputs render inline in the matching UI or as a separate report view
- Whether to add OCR-based intake (photographed batch labels → auto-extracted compound/expiry data) as a stretch goal after Checkpoint 6 — this is the one genuinely justified AI/ML component for this project; everything else in the core pipeline is intentionally rule-based, not ML
