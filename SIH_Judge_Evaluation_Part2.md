# CONFIDENTIAL EVALUATION REPORT — PART 2 of 2
## Smart India Hackathon (SIH) 2026
### Project: Arogya Bhoomi | Team: Algorift | PS ID: SIH26193

---

# SECTION 8 — DEMO EVALUATION

## Ideal Demo Sequence (5 minutes)

### Step 1: Dashboard (30 seconds)
**Show**: Platform KPIs — 53 batches, 29 soil profiles, 51 matches, 6 partners, 561 audit events.

**Say**: "Everything you see is live data from our SQLite database. 53 expired pharmaceutical batches tracked. 51 matched to soil-deficient states. Let me show you exactly how one match was created."

### Step 2: Stock & Compliance — /stock (45 seconds)
**Show**: Batch ledger. Find **BATCH-ZI2026-1014** (Zinc Sulphate, 247 kg, Bhubaneswar, Odisha).

**Say**: "A pharmacy in Bhubaneswar submits 247 kg of expired Zinc Sulphate. Our compliance engine checks: is this an approved single-compound mineral? Yes — it's on our three-compound whitelist. Status: Accepted."

**Say**: "If I submitted 'Zincovit' instead — a combination vitamin — the system rejects it. Exact match only. No brand names, no fuzzy matching."

### Step 3: Recovery Pipeline — /pipeline (90 seconds)
**Show**: Run pipeline on BATCH-ZI2026-1014.

**Say**: "Step 1: compliance — passed. Step 2: geolocation — Bhubaneswar resolves to Odisha, 20.29°N, 85.82°E. Step 3: soil matching — is Odisha deficient in Zinc? [pause] Yes — same-state match. Step 4: dosage — 37.5 kg ZnSO₄ per hectare."

**Then**: Download the acknowledgement PDF. Show it briefly.

**Say**: "Every successful recovery generates a downloadable acknowledgement PDF — batch data, soil match, dosage, partner, SHA-256 audit chain — all in one document."

### Step 4: Audit Trail — /audit (60 seconds)
**Show**: Audit trail for BATCH-ZI2026-1014. Events: BATCH_LOGGED → COMPLIANCE_PASSED → MATCH_CREATED → DOSAGE_GENERATED.

**Say**: "Every step recorded with SHA-256 hash. Each hash includes the previous event's hash — a chain. If anyone modifies any record, the chain breaks at that point."

**Show**: Click "Verify Chain" → "All events verified."

### Step 5: Soil Map — /soil-map (45 seconds)
**Show**: Interactive map. Point out Odisha's marker. Filter by compound.

**Say**: "29 Indian states mapped by soil deficiency profile. Blue = Zinc. Orange = Iron. Purple = Potassium. Our matching engine uses this exact data to route batches."

### Step 6: Dosage Calculator — /dosage (30 seconds)
**Show**: Dosage simulator. Enter **Ferrous Sulphate**, 100 kg, Medium severity.

**Say**: "Notice — Ferrous Sulphate does NOT give a soil application rate. It gives foliar spray guidance: 3-4 sprays of 1.0% FeSO₄ at weekly intervals. This is the ICAR recommendation — soil application of iron is scientifically inappropriate because iron immobilises in alkaline soils. Our system knows this."

### What NOT to demonstrate:
- ❌ Partners page alone (redundant with pipeline)
- ❌ Network map (nice visual, wastes time)
- ❌ Impact stats page (cite the number verbally)
- ❌ Soil re-test result submission (too many clicks)
- ❌ Any page that loads slowly or has rendering bugs

## One Complete Story for Judges

> "A retail pharmacy in Bhubaneswar, Odisha submits 247 kg of expired Zinc Sulphate — batch BATCH-ZI2026-1014. Compliance verifies: Zinc Sulphate is on the whitelist. Accepted. Bhubaneswar resolves to 20.29°N, 85.82°E. Odisha is documented as zinc-deficient — same-state match. Dosage: 37.5 kg ZnSO₄/ha. Assigned to AgriMicro Recovery Works, Bhubaneswar. Handoff recorded. Soil re-test scheduled. And every single step — intake, compliance, match, dosage, partner, handoff — is in a SHA-256 hash-linked audit chain verifiable in real time."

---

# SECTION 9 — TEAM MEMBER PREPARATION

## TOP 5 Questions EVERY Team Member Must Know

**1. What problem does Arogya Bhoomi solve?**
→ We create a traceable, verifiable platform to recover mineral compounds from expired single-compound pharmaceuticals and redirect them to Indian soils documented as deficient in exactly those minerals.

**2. What are the three compounds and why only three?**
→ Ferrous Sulphate (iron), Zinc Sulphate (zinc), Potassium Chloride (potassium). Only these have: single-compound pharma formulations, direct agricultural fertiliser equivalents, documented national soil deficiency, AND no significant contamination risk after extraction.

**3. Is this blockchain?**
→ No. SHA-256 hash-linked audit chain in a single SQLite database. Tamper evidence, not distributed consensus. Explicitly stated in README.

**4. What is actually working in the demo?**
→ Full pipeline: intake compliance, geolocation, soil matching, dosage calculation, partner assignment, audit chain, PDF download, recovery map. 88 automated tests.

**5. What do we NOT solve?**
→ Chemical extraction (partner's job), logistics, combination products, full STCR equations, live government APIs, OCR, authentication/RBAC.

---

## TOP 10 Questions for Technical Members

**1. How does the hash chain work?**
→ SHA-256(event_id|batch_id|event_type|timestamp|description|previous_hash). First = "GENESIS." Each event uses previous event's hash.

**2. Why does FeSO₄ return foliar_spec instead of kg/ha?**
→ ICAR recommends foliar for Fe — iron immobilises in alkaline soils. base_rate is NULL in dosage_table.json. Code branches on `if base_rate is None`.

**3. How does matching handle Kerala (not_usable)?**
→ Falls back to nearest-usable-state via Haversine distance.

**4. audit_events table schema?**
→ event_id (PK), batch_id (FK), timestamp, event_type, actor, description, previous_event_hash, event_hash.

**5. What happens at startup?**
→ init_db_schema → seed_demo_partners → seed_demo_matches_and_audit → recompute_and_fix_audit_hashes.

**6. Why is severity hardcoded to "Medium"?**
→ No real per-district soil test data. Documented simplification. Module handles all tiers — proven in tests and calculator.

**7. What does Haversine compute?**
→ Great-circle distance between two lat/lon points on sphere of R = 6371 km. Used in find_match() for nearest-state fallback.

**8. Is indiapins actually used?**
→ Available. Used for pincode lookup. Demo data uses "City, State" strings → hardcoded CITY_COORDINATES. So available but not exercised in standard demo.

**9. PDF generation process?**
→ get_report_data_for_batch() validates eligibility. generate_acknowledgement_pdf_bytes() uses ReportLab for in-memory PDF with 3 sections.

**10. What is missing from requirements.txt?**
→ `reportlab` is not listed. Fresh pip install will fail at PDF generation. **Must fix before demo.**

---

## TOP 10 Questions for Non-Technical / Presentation Members

**1. Why are expired medicines useful for agriculture?**
→ The inorganic mineral (zinc, iron, potassium) doesn't expire like biological medicines. After extraction, it's functionally identical to agricultural fertiliser.

**2. How is this different from throwing medicines in a field?**
→ It isn't throwing anything. Certified partner extracts the mineral, tests quality, then the purified mineral is applied. Our software is the coordination layer.

**3. Farmer benefit?**
→ Free or subsidised micronutrients. ICAR-referenced dosage. Micronutrient correction = 10-15% yield improvement in deficient soils.

**4. Pharmacy benefit?**
→ Documented disposal. Regulatory compliance. ESG reporting.

**5. Environmental benefit?**
→ Diverts from incineration. Reduces synthetic fertiliser production. Improves agricultural productivity.

**6. Is this safe?**
→ Only 3 compounds with agricultural equivalents. Combination products rejected. Extraction at certified facility. ICAR dosage. Full audit trail.

**7. Why does this need software?**
→ Without it: pharmacy doesn't know which soil is deficient. Cooperative doesn't know what stock is available. Nobody has an audit trail.

**8. What is the project NOT doing?**
→ Not treating patients. Not dispensing medicines. Not bypassing regulations. Not extracting chemicals. Not claiming AI or blockchain.

**9. How is this different from existing disposal?**
→ Existing = destroy. We = recover as agricultural input. Destruction wastes mineral value. Recovery creates value.

**10. Next steps after SIH?**
→ ICAR regional pilot. State agriculture department partnership. CPCB regulatory pre-approval. 2-3 real pharmacies + 1 partner for 6-month proof-of-concept.

---

# SECTION 10 — SIH JUDGE SCORECARD

| # | Criterion | Score (0–10) | Rationale |
|---|---|---|---|
| 1 | Problem relevance | **9** | Real, quantified problem. Two sides documented with credible sources. |
| 2 | SIH26193 alignment | **7** | Circular-economy theme coherent. PS text not in repo — alignment unverifiable. |
| 3 | Innovation | **7** | Cross-domain observation genuine. Technology not novel. Innovation = integration + restraint. |
| 4 | Technical implementation | **8** | All 4 modules working. Audit chain correct. Fe foliar branch correct. Severity hardcoded = gap. |
| 5 | Working prototype | **8** | Runs. 88 tests claimed. Pipeline executes. PDF downloads. Map renders. Bug: reportlab missing from requirements.txt. |
| 6 | Feasibility | **7** | Short-term pilot feasible. National = inter-ministerial work. Don't oversell timeline. |
| 7 | Safety | **7** | Scope boundaries address main concerns. Excipient risk real but acknowledged. Extraction correctly outsourced. |
| 8 | Regulatory awareness | **7** | HWM Rules, FCO, D&C Act awareness at surface level. Deep knowledge requires domain expert. |
| 9 | Data credibility | **8** | Naik et al. 2024, ICAR 2012-2018, ICAR Farming June 2025. Static data, synthetic intake data — both declared. Honest. |
| 10 | User impact | **8** | Three-sided value: pharmacy, agricultural body, environment. Farmer benefit = yield improvement. |
| 11 | Economic value | **7** | Impact_stats endpoint computes addressable hectares. No unit economics (cost/kg recovered). |
| 12 | Environmental impact | **7** | Waste diversion from incineration. Fertiliser substitution. Reasonable claims. No LCA. |
| 13 | Scalability | **7** | Architecture scales with known upgrades. Real challenge = operational (partner network). |
| 14 | Presentation potential | **8** | Strong opening story. Honest about limits. Recovery map visually compelling. |
| 15 | Demo potential | **8** | End-to-end in 5 minutes. PDF tactile. Audit verification impressive. Map visual. |

## **CURRENT SCORE: 113 / 150**

## Likely Judge Impression

**First 30 seconds**: "Interesting cross-domain idea. Let's see if it's real or a slide deck."

**After explanation**: "They know their domain. The 3-compound restriction is smart. Let's see if they prepared for the excipient question."

**After technical demo**: "The pipeline runs. Audit chain verification is nice. Map is professional. Fe foliar branch shows domain knowledge. Severity hardcoded to Medium is lazy but it runs."

**After Q&A**: *Depends entirely on how the team handles Section 7 dangerous questions. Honest answers without unsupported scientific claims → Positive. Overclaiming or fabricating ICAR citations → Negative.*

---

# SECTION 11 — WHAT COULD MAKE US LOSE?

| # | Problem | Severity | Judge Perception | Defence | Code Change? |
|---|---|---|---|---|---|
| **1** | **reportlab missing from requirements.txt** | **CRITICAL** | Demo crashes on fresh environment at PDF gen | Fix immediately | **YES** |
| **2** | **Cannot quote PS 193 verbatim** | **CRITICAL** | "Team doesn't know their own problem statement" | Memorise exact text | No — prep |
| **3** | **Severity hardcoded to "Medium"** | **HIGH** | "Dosage module half-implemented in production code" | Acknowledge; demo calculator separately with all tiers | Optional code change |
| **4** | **Geolocation = hardcoded dict** | **HIGH** | "Not a geolocation module — it's a lookup table" | "Demo cities are reliable. Production = geocoding API. Matching works regardless of coordinate source." | Explain honestly |
| **5** | **Soil data 6-12 years old, static** | **HIGH** | "Recommendations based on outdated data" | "Soil patterns change over decades. ICAR published data. Production = Soil Health Card API." | Explain honestly |
| **6** | **No authentication/RBAC** | **MEDIUM** | "Anyone can submit anything" | "Documented limitation. Production = licence verification." | Scope boundary |
| **7** | **Excipient safety not in software** | **MEDIUM** | "System ignores contamination risk" | "Partner extraction + QC is the control. We're coordination, not chemistry." | Architecture boundary |
| **8** | **Synthetic data only, no real users** | **MEDIUM** | "Has anyone used this?" | "Hackathon prototype by design. Proving coordination logic." | Honest answer |
| **9** | **±25% multiplier not directly from ICAR** | **MEDIUM** | "Presenting engineering judgment as ICAR guidance" | "Our implementation of ICAR's tier system. Acknowledged in dosage_table.json note." | Acknowledge distinction |
| **10** | **Demo fails (crash/loading error/unseeded DB)** | **CRITICAL** | "Team couldn't demonstrate their own system" | Rehearse 5+ times on exact demo hardware. Bring backup video. | **YES — prepare** |

---

# SECTION 12 — WHAT SHOULD WE CHANGE?

## MUST FIX

1. **Add `reportlab` to requirements.txt** — PDF generation fails on fresh install. Verifiable bug. Run `pip install -r requirements.txt` on clean env to confirm.

2. **Memorise PS 193 text verbatim** — Every team member. Write it on the inside of a notebook. Review morning of presentation.

3. **Prepare live Fe pipeline demo** — Run BATCH-FE2025-1007 and show foliar_spec output. Strongest technical differentiation.

4. **Prepare live tamper-detection demo** — Before presentation: corrupt one audit event in TEST database copy, run verify_audit_chain(), show specific failed event_id. More impressive than just claiming "it detects tampering."

## SHOULD FIX

5. **Add severity tier selector to pipeline UI** — Dropdown (Low/Medium/High) on pipeline page passed to POST /api/process_batch. ~2-hour change. Makes dosage module's full capability visible.

6. **Add rejected batches to demo dataset** — 2-3 synthetic batches named "Zincovit", "Fefol Capsules", "Calcium Pantothenate" — all reject at compliance. Show one rejection live. Demonstrates compliance filter working.

7. **Fix hardcoded retest date (2026-11-01)** — Compute as `application_date + 60 days`. One line change.

## NICE TO HAVE

8. **Add "QUALITY_FEEDBACK" audit event type** — Stub endpoint where partner records QC result (e.g., "Purity 99.2% — FCO compliant"). Closes biggest safety audit gap.

9. **Add "Batch Comparison" view** — Two batches side-by-side: accepted (Zinc Sulphate) vs. rejected (Zincovit). One screen, two outcomes, crystal clear.

10. **One-page physical infographic** — Complete workflow as circular loop. Printout for judges. Expired pharma → partner extraction → mineral recovery → deficient soil → improved yield.

## DO NOT TOUCH

- ❌ Do NOT add AI/ML components that don't exist
- ❌ Do NOT change the 3-compound whitelist
- ❌ Do NOT replace the simple dosage formula unless fully defensible
- ❌ Do NOT add blockchain just because judges might ask
- ❌ Do NOT add features that aren't demoable — cleaner > bigger
- ❌ Do NOT modify the audit chain implementation — it works correctly

---

# SECTION 13 — FINAL JUDGE VERDICT

## If I were judging this project today, would I shortlist Arogya Bhoomi?

# **MAYBE → leaning YES**

---

### Explanation:

Arogya Bhoomi is one of the more honestly documented hackathon projects I have reviewed. The team correctly identified a real dual-sided problem, correctly scoped to exactly three scientifically defensible compounds, correctly implemented the Ferrous Sulphate foliar branch, correctly built the audit chain as a hash chain (not overclaiming blockchain), and correctly disclosed every limitation in writing.

The working prototype is real — all four modules run, the pipeline executes, the PDF generates, the map renders, the audit chain verifies. The 88-test claim is plausible given the 11 test files. The codebase is clean, well-commented, and internally consistent with the PRD.

**What tips this toward YES**: The scientific restraint. Most SIH teams overclaim — this team actively restricted scope. Documenting "Known Limitations" in the PRD and "Scope Boundaries" in the README is unusual and will stand out to an experienced judge.

**What keeps it at MAYBE**: Three things. (1) Geolocation is a hardcoded dictionary — a judge who tests an unexpected city gets an error. (2) Severity tier is permanently Medium in live pipeline — a judge who asks "what happens for severely deficient soil?" finds the gap. (3) The excipient question will come — if not answered cleanly, it undermines the entire safety claim.

---

### 1. Strongest reason to select us:
The project solves a real, quantified, documented problem with an honest scope, a working prototype, and scientific traceability of every claim. The audit chain is technically rigorous. Documentation is unusually transparent.

### 2. Biggest reason not to select us:
Geolocation is a dictionary lookup and severity is permanently Medium in live execution. Together, these suggest the "Working Prototype" badge covers a narrower scenario than implied. A judge who tests beyond the demo script finds the edges quickly.

### 3. Single biggest improvement required:
**Add a severity tier dropdown to the pipeline UI and add 2-3 rejected batches to demo data.** Both changes make the compliance engine and dosage engine visibly exercised during demo instead of taken on faith.

### 4. Strongest part of the demo:
**The audit chain tamper-detection demonstration.** Show a specific event verified → tampered → detected at exact event_id → re-verified clean. Technically impressive and immediately understandable.

### 5. Most dangerous question:
**"Is expired medicine actually safe for agricultural use?"** If the answer isn't immediate and confident — distinguishing "expired tablet" from "recovered inorganic mineral" — the team loses credibility on the entire safety claim.

### 6. One sentence to remember during Q&A:

> **"We recover the mineral, not the medicine."**

Every safety question, every regulatory question, every "isn't this dangerous?" question has this as its core answer. Repeat when needed. Precise, defensible, memorable.

---

> *Evaluation based on full inspection of: PRD.md, README.md, AI_Build_Prompts.md, PROJECT_UNDERSTANDING.md, app.py (1,981 lines), modules/intake.py, modules/dosage.py, modules/matching.py, modules/geolocation.py, load_data.py, compound_list.json, dosage_table.json, soil_deficiency.json, demo_intake.csv, 11 test files, 18 HTML templates, requirements.txt.*
>
> *Date: September 11, 2026 | Team: Algorift | Project: Arogya Bhoomi | PS: SIH26193*
