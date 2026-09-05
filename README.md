<![CDATA[<div align="center">

# 🌱 Nirmūla Recovery Platform

### Traceable Recovery & Deployment Platform for Micronutrient Compounds from Expired Pharmaceuticals

**Smart India Hackathon (SIH) 2026 — Problem Statement ID: 198**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4-FF6384?logo=chart.js&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-78%20Passed-brightgreen?logo=pytest&logoColor=white)

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [System Architecture](#-system-architecture)
- [4-Stage Recovery Pipeline](#-4-stage-recovery-pipeline)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Web Interface (UI Pages)](#-web-interface-ui-pages)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the Application](#-running-the-application)
- [Testing](#-testing)
- [Data Sources & References](#-data-sources--references)
- [Known Limitations & Scope](#-known-limitations--scope)

---

## 🔍 Problem Statement

India faces a dual crisis:

1. **Pharmaceutical Waste:** Massive quantities of expired pharmaceutical stock are destroyed or landfilled annually. During the 2016 FDC ban alone, ₹400+ crore worth of medicines were destroyed. No recovery pathway exists.

2. **Soil Micronutrient Deficiency:** Indian soils suffer severe micronutrient deficiencies — **49% are Zinc-deficient** and **>33% are Iron-deficient** nationally (Naik et al., 2024; ICAR Soil Survey 2012–2018).

**The critical insight:** Many expired single-compound medicines (e.g., Ferrous Sulphate, Zinc Sulphate, Potassium Chloride) contain mineral ingredients that are **chemically identical** to standard agricultural fertilizers. Currently, **no system in India** connects verified expired pharmaceutical stock with regions of documented soil micronutrient deficiency to enable safe, dosage-controlled agricultural reuse.

---

## 💡 Our Solution

**Nirmūla** ("from the root" in Sanskrit) is a traceable, end-to-end platform that creates a **circular economy bridge** between expired pharmaceutical stock and agricultural soil remediation.

The platform implements a **4-module rule-based pipeline** that:

1. ✅ **Accepts** only approved single-compound medicines (strict whitelist compliance)
2. 📍 **Geolocates** the source of expired stock
3. 🗺️ **Matches** accepted batches to Indian states with documented soil deficiency in the relevant mineral
4. 💊 **Recommends** ICAR-compliant dosage rates for soil application (with special foliar spray handling for Ferrous Sulphate)

Every step is **audited with SHA-256 hash-linked events**, ensuring complete traceability from pharma waste intake to soil re-test feedback.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NIRMŪLA RECOVERY PLATFORM                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│   │   Frontend    │    │  Flask API   │    │   SQLite DB  │              │
│   │  (HTML/CSS/   │◄──►│  (app.py)    │◄──►│  (app.db)    │              │
│   │   Chart.js/   │    │  1696 lines  │    │  8 tables    │              │
│   │   Leaflet)    │    │  30+ routes  │    │  45+ records │              │
│   └──────────────┘    └──────┬───────┘    └──────────────┘              │
│                              │                                          │
│              ┌───────────────┼───────────────┐                          │
│              ▼               ▼               ▼                          │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│   │  Module 1     │ │  Module 2     │ │  Module 3     │ │  Module 4     │ │
│   │  INTAKE &     │ │  SOIL-DEFIC.  │ │  DOSAGE       │ │  GEOLOCATION │ │
│   │  COMPLIANCE   │ │  MATCHING     │ │  RECOMMEND.   │ │  RESOLUTION  │ │
│   │  intake.py    │ │  matching.py  │ │  dosage.py    │ │ geolocation.py│ │
│   └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘  │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              SHA-256 Hash-Linked Audit Trail                     │   │
│   │   Genesis → Compliance → Match → Partner Assign → Handoff       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architectural Design Principles

| Principle | Implementation |
|---|---|
| **Rule-Based Logic** | Intentionally non-ML. Exact compound whitelist match, ICAR GRD ±25% dosage tables. Transparent, auditable, and reproducible. |
| **Append-Only Audit** | Every pipeline step generates a SHA-256 hash-linked audit event. Chain integrity is cryptographically verifiable. |
| **Idempotent Pipeline** | Re-processing a batch returns cached results — no duplicate matches or audit entries. |
| **Data Integrity** | All 45 original intake records are preserved. Schema uses `CREATE TABLE IF NOT EXISTS` — never drops existing data. |
| **Modular Separation** | Each pipeline stage lives in its own Python module with independent unit tests. |

---

## 🔄 4-Stage Recovery Pipeline

```
     ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
     │   STAGE 1        │         │   STAGE 2        │         │   STAGE 3        │         │   STAGE 4        │
     │   INTAKE &       │────────►│   GEOLOCATION    │────────►│   SOIL-DEFIC.    │────────►│   DOSAGE         │
     │   COMPLIANCE     │         │   RESOLUTION     │         │   MATCHING       │         │   RECOMMENDATION │
     │                  │         │                  │         │                  │         │                  │
     │ • Exact compound │         │ • Pincode → GPS  │         │ • Same-state     │         │ • ICAR GRD ±25%  │
     │   whitelist match│         │ • City → coords  │         │   preference     │         │ • Severity tiers │
     │ • Accept/Reject  │         │ • Haversine dist │         │ • Fallback to    │         │ • Foliar spray   │
     │                  │         │                  │         │   nearest state  │         │   branch (FeSO₄) │
     └─────────────────┘         └─────────────────┘         └─────────────────┘         └─────────────────┘
             │                                                                                     │
             ▼                                                                                     ▼
     ┌─────────────────┐                                                                 ┌─────────────────┐
     │ If REJECTED:     │                                                                 │ COMBINED JSON    │
     │ Return reason    │                                                                 │ RESPONSE with    │
     │ (e.g., "not on   │                                                                 │ match + dosage   │
     │  approved list") │                                                                 │ + audit events   │
     └─────────────────┘                                                                 └─────────────────┘
```

### Pipeline Details

| Stage | Module | Input | Output | Key Logic |
|---|---|---|---|---|
| **1. Intake & Compliance** | `modules/intake.py` | Batch `compound_name` | `Accepted` or `Rejected` with reason | Exact string match against 3-compound whitelist: `Ferrous Sulphate`, `Zinc Sulphate`, `Potassium Chloride` |
| **2. Geolocation** | `modules/geolocation.py` | `source_location` (city or pincode) | `{ lat, lon, state, district }` | Uses `indiapins` package for pincode resolution; manual lookup table for 50+ Indian cities; Haversine distance formula |
| **3. Soil-Deficiency Matching** | `modules/matching.py` | Accepted batch + resolved location | Matched `target_state` with deficiency info | Priority: same-state match → fallback to nearest deficient state via Haversine distance |
| **4. Dosage Recommendation** | `modules/dosage.py` | Compound name + severity tier | Dosage rate (kg/ha) or foliar spec | ICAR GRD base rate with ±25% severity adjustment. **Critical:** Ferrous Sulphate returns foliar spray spec (1.0% FeSO₄ solution, 3–4 weekly sprays) instead of soil application |

### Approved Compound Whitelist

| Compound | Nutrient | Agricultural Precedent | Dosage Type |
|---|---|---|---|
| **Ferrous Sulphate** (FeSO₄·7H₂O) | Iron (Fe) | Standard iron fertilizer | ⚠️ **Foliar Spray Only** |
| **Zinc Sulphate** (ZnSO₄·7H₂O) | Zinc (Zn) | Standard zinc fertilizer | Soil Application |
| **Potassium Chloride** (KCl) | Potassium (K) | Muriate of Potash (MOP) | Soil Application |

### Severity-Adjusted Dosage Table (ICAR GRD ±25%)

| Compound | Low Severity | Medium Severity (Base) | High Severity |
|---|---|---|---|
| **Zinc Sulphate** | 18.75 kg/ha (-25%) | 25.0 kg/ha | 31.25 kg/ha (+25%) |
| **Potassium Chloride** | 37.5 kg/ha (-25%) | 50.0 kg/ha | 62.5 kg/ha (+25%) |
| **Ferrous Sulphate** | Foliar: 1.0% FeSO₄ solution | Foliar: 1.0% FeSO₄ solution | Foliar: 1.0% FeSO₄ solution |

---

## ⚙️ Tech Stack

### Backend

| Technology | Purpose | Details |
|---|---|---|
| **Python 3.10+** | Core language | Compatible with 3.10, 3.11, 3.12, 3.13 |
| **Flask 3.0+** | Web framework & REST API | 30+ endpoints across API and page routes |
| **SQLite 3** | Embedded relational database | Zero-config, file-based (`app.db`), 8 tables |
| **`indiapins` 0.2+** | Indian pincode geolocation | Resolves 6-digit pincodes to GPS coordinates |

### Frontend

| Technology | Purpose | Details |
|---|---|---|
| **HTML5 + Jinja2** | Server-side templating | 15 template files with base template inheritance |
| **CSS3 (Vanilla)** | Styling & responsive design | Enterprise agri-tech design system with `Inter` font |
| **Chart.js 4** | Interactive data visualization | Donut, Bar, and Horizontal Bar charts on dashboard |
| **Leaflet.js 1.9** | Interactive map visualization | Recovery Network Map with source/deficiency/partner markers |
| **Vanilla JavaScript** | Client-side interactivity | API calls, form handling, dynamic filtering |

### Testing

| Technology | Purpose | Details |
|---|---|---|
| **pytest 9.0+** | Unit testing framework | 78 tests across 10 test files |

### Security & Auditability

| Technology | Purpose | Details |
|---|---|---|
| **SHA-256** | Cryptographic audit hashing | Append-only, hash-linked event chain per batch |
| **JSON Canonical Form** | Deterministic serialization | `event_id|batch_id|event_type|timestamp|description|previous_hash` |

---

## 🗄️ Database Schema

The SQLite database (`app.db`) contains **8 tables**:

### Core Data Tables (populated by `load_data.py`)

| Table | Records | Purpose |
|---|---|---|
| `compound_reference` | 3 | Approved compound whitelist (FeSO₄, ZnSO₄, KCl) |
| `soil_deficiency` | 29 | Indian state-level soil micronutrient deficiency data |
| `dosage_rates` | 3 | ICAR GRD ±25% application rates per compound |
| `intake_batches` | 45 | Synthetic expired pharmaceutical batch data |

### Infrastructure Tables (created by `app.py` on startup)

| Table | Purpose | Key Columns |
|---|---|---|
| `audit_events` | SHA-256 hash-linked audit trail | `event_id`, `batch_id`, `event_type`, `event_hash`, `previous_event_hash` |
| `matches` | Soil-deficiency match records | `match_id`, `batch_id`, `target_state`, `severity`, `status`, `assigned_partner_id` |
| `partners` | Recovery/processing partner facilities | `partner_id`, `name`, `supported_compounds`, `capacity_kg`, `available_capacity_kg` |
| `soil_retests` | Post-application soil re-test feedback | `retest_id`, `match_id`, `initial_severity`, `after_value`, `improvement` |

### Entity Relationship

```
intake_batches (45 rows)
    │
    ├──► audit_events         (hash-linked chain per batch)
    │       event_hash ← SHA256(event_id|batch_id|event_type|timestamp|desc|prev_hash)
    │
    ├──► matches              (1 batch → 1 match, with dosage & target region)
    │       │
    │       ├──► partners     (assigned processing facility)
    │       │
    │       └──► soil_retests (post-application feedback loop)
    │
    ├──► compound_reference   (whitelist validation — FK lookup)
    │
    └──► soil_deficiency      (target region matching — 29 states)
              │
              └──► dosage_rates (ICAR GRD ±25% dosage lookup)
```

---

## 🔌 API Endpoints

### Pipeline Execution

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/process_batch/<batch_doc_id>` | Run full 4-step pipeline (idempotent) |
| `POST` | `/api/run_compliance` | Run compliance check on all pending batches |

### Batch Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/batches` | List all intake batches |
| `POST` | `/api/batches` | Log a new batch into intake |
| `GET` | `/api/batches/<id>` | Get single batch details |

### Match Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/matches` | List all active matches with dynamic stats |
| `GET` | `/api/matches/<id>` | Get single match detail with explanation |
| `POST` | `/api/matches/<id>/status` | Update match lifecycle status |
| `POST` | `/api/matches/<id>/assign-partner` | Assign a partner facility to a match |
| `POST` | `/api/matches/<id>/record-handoff` | Record material handoff completion |

### Partner Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/partners` | List all partner facilities |
| `GET` | `/api/partners/<id>` | Get single partner detail |
| `GET` | `/api/partners/eligible` | Eligible partners with capacity checks |

### Audit & Verification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/audit/<batch_id>` | Get audit timeline & verification status |
| `POST` | `/api/audit/<batch_id>/verify` | Perform SHA-256 chain integrity verification |

### Soil Re-Test Feedback

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/retests` | List all soil re-tests & statistics |
| `POST` | `/api/retests` | Schedule a new soil re-test |
| `POST` | `/api/retests/<id>/result` | Submit post-application re-test observation |

### Reference Data

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/compounds` | List approved compound whitelist |
| `GET` | `/api/soil_deficiency` | State-level soil deficiency data |
| `GET` | `/api/districts` | Illustrative district visualization layer |
| `GET` | `/api/stats` | Dynamic dashboard KPI statistics |

### Enhancement APIs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/impact_stats` | Environmental impact metrics (elemental yields, addressable farmland) |
| `GET` | `/api/network_data` | Recovery network map data (sources, deficiencies, partners) |
| `POST` | `/api/simulate_recovery` | What-If soil recovery simulator (compound + quantity + severity) |

---

## 🖥️ Web Interface (UI Pages)

The platform features **13 web pages** with a professional sidebar navigation:

### Core Operations

| Route | Page | Description |
|---|---|---|
| `/` | **Command Center Dashboard** | Hero banner, KPI row, 3 Chart.js visualizations, 4-stage circular economy snapshot, 12-step storytelling workflow, recent batches table |
| `/network` | **Recovery Network Map** | Leaflet.js interactive map of India with source markers (🟢), deficiency markers (🟠), partner markers (🔵), traceability flow lines, and compound filters |
| `/impact` | **Environmental Impact** | Elemental micronutrient breakdown (Fe 20.1%, Zn 21.0%/33.0%, K 52.4%), addressable farmland (ha) calculator, methodology transparency |
| `/simulator` | **Recovery Simulator** | What-If analysis engine — select compound + quantity + severity → instant addressable farmland & elemental yield calculation |

### Stock & Compliance

| Route | Page | Description |
|---|---|---|
| `/batches` | **Stock Ledger** | Full intake batch listing with status badges, search/filter, and one-click pipeline processing |
| `/compliance` | **Compliance Queue** | View and run compliance checks on pending batches |

### Deployment & Audit

| Route | Page | Description |
|---|---|---|
| `/matches` | **Active Matches** | Match listing with compound tabs, status lifecycle management, partner assignment |
| `/partners` | **Partner Facilities** | Recovery/processing partner directory with capacity indicators |
| `/retests` | **Soil Re-test Feedback** | Post-application monitoring with improvement tracking |
| `/audit` | **Audit Trail & Hashes** | SHA-256 hash chain viewer and integrity verification per batch |

### Reference

| Route | Page | Description |
|---|---|---|
| `/process/<batch_id>` | **Pipeline Runner** | Real-time pipeline processing view with step-by-step status updates |
| `/soil-map` | **State Soil Reference** | India-wide soil deficiency reference data by state |
| `/about` | **Methodology / About** | Platform methodology, data sources, and technical documentation |

---

## ✨ Key Features

### 1. Nirmūla Command Center Dashboard
- **Dynamic KPI Row**: Real-time metrics — Pharma Stock Tracked (kg), Approved Compounds (3), Deficient Soil Regions (29 states), Addressable Farmland Area (ha)
- **Circular Economy Impact Snapshot**: 4-stage visual flow (Pharma Waste → Micronutrients Recovered → Addressable Farmland → Deficiency Target Matches)
- **3 Chart.js Visualizations**:
  - Compound Stock Distribution (Donut Chart)
  - State Soil Deficiency Severity (Bar Chart)
  - Recovery Pipeline Progression (Horizontal Bar)
- **12-Step End-to-End Storytelling Workflow**: Visual lifecycle from expired stock intake to soil re-test feedback

### 2. Interactive Recovery Network Map
- **Leaflet.js Map** centered on India with OpenStreetMap tiles
- **Multi-layer markers**: Source (🟢), Deficiency (🟠), Partner (🔵) facilities
- **Traceability flow lines**: Visual connections between sources, targets, and partners
- **Compound filter bar**: Filter by FeSO₄, ZnSO₄, KCl with reset capability

### 3. Environmental Impact Calculator
- **Stoichiometric elemental yields**: Fe (20.1%), Zn (21.0%/33.0%), K (52.4%)
- **Addressable farmland estimation**: Based on ICAR GRD baseline application rates
- **Transparent methodology**: Full formula disclosure with agronomic disclaimers

### 4. What-If Soil Recovery Simulator
- **4-step wizard**: Compound → Quantity → Severity → Instant Results
- **Foliar spray branch**: Special handling for Ferrous Sulphate
- **Calculation breakdown**: Exact stoichiometric formula and reference rates

### 5. SHA-256 Cryptographic Audit Trail
- **Append-only event chain**: Every pipeline step generates a hash-linked audit event
- **Tamper detection**: Built-in chain integrity verification endpoint
- **Genesis event**: First event per batch with `previous_hash = "GENESIS"`

### 6. Partner Facility Management
- **Capacity tracking**: Real-time available vs. total capacity
- **Compound compatibility**: Partners support specific compound types
- **Assignment workflow**: Match → Assign Partner → Record Handoff

### 7. Soil Re-test Feedback Loop
- **Post-application monitoring**: Schedule re-tests after compound deployment
- **Improvement tracking**: Before/after severity comparison
- **Closed-loop validation**: Verify soil remediation effectiveness

---

## 📁 Project Structure

```
d:\SIH-2026\SIH-198\
│
├── README.md                                           # This file
├── PRD.md                                              # Product Requirements Document
├── AI_Build_Prompts.md                                 # Step-by-step build prompts
├── PROJECT_UNDERSTANDING.md                            # Detailed project analysis
├── Demo_Expired_Stock_Intake_Data_UPDATED.xlsx          # Reference Excel (3 sheets)
├── State_Soil_Deficiency_Medicine_Match_FILTERED.xlsx   # Reference Excel (2 sheets)
├── .gitignore                                          # Git ignore rules
│
└── starter_kit/
    └── starter/
        │
        ├── app.py                     # Flask application (1696 lines, 30+ routes)
        ├── app.db                     # SQLite database (8 tables, 45+ records)
        ├── load_data.py               # Database initializer script
        ├── requirements.txt           # Python dependencies (flask, indiapins)
        │
        ├── modules/                   # Core pipeline modules
        │   ├── __init__.py
        │   ├── intake.py              # Module 1: Intake & Compliance
        │   ├── geolocation.py         # Module 4: Geolocation Resolution
        │   ├── matching.py            # Module 2: Soil-Deficiency Matching
        │   └── dosage.py              # Module 3: Dosage Recommendation
        │
        ├── templates/                 # Jinja2 HTML templates (15 files)
        │   ├── base.html              # Base layout with sidebar navigation
        │   ├── index.html             # Command Center Dashboard
        │   ├── network.html           # Recovery Network Map (Leaflet.js)
        │   ├── impact.html            # Environmental Impact Calculator
        │   ├── simulator.html         # What-If Recovery Simulator
        │   ├── batches.html           # Stock Ledger
        │   ├── compliance.html        # Compliance Queue
        │   ├── matches.html           # Active Matches
        │   ├── partners.html          # Partner Facilities
        │   ├── retests.html           # Soil Re-test Feedback
        │   ├── audit.html             # Audit Trail & Hashes
        │   ├── process.html           # Pipeline Runner
        │   ├── soil_map.html          # State Soil Reference
        │   ├── about.html             # Methodology / About
        │   └── coming_soon.html       # Placeholder
        │
        ├── static/                    # Static assets
        │   ├── style.css              # Global stylesheet (19KB)
        │   └── script.js              # Client-side JavaScript
        │
        ├── data/                      # Reference data files
        │   ├── compound_list.json     # 3 approved compounds
        │   ├── dosage_table.json      # ICAR dosage rates + foliar spec
        │   ├── soil_deficiency.json   # 29 states, deficiency data
        │   └── demo_intake.csv        # 45 synthetic batch intake rows
        │
        └── tests/                     # Unit test suite (78 tests)
            ├── __init__.py
            ├── test_intake.py         # Module 1 tests (4 tests)
            ├── test_geolocation.py    # Module 4 tests (5 tests)
            ├── test_matching.py       # Module 2 tests (4 tests)
            ├── test_dosage.py         # Module 3 tests (6 tests)
            ├── test_pipeline.py       # End-to-end pipeline tests (7 tests)
            ├── test_phase2.py         # Phase 2 integration tests (4 tests)
            ├── test_phase3.py         # Phase 3: Match management tests (10 tests)
            ├── test_phase4.py         # Phase 4: Partner assignment tests (12 tests)
            ├── test_phase5.py         # Phase 5: Audit & re-test tests (20 tests)
            └── test_enhancements.py   # Enhancement API tests (6 tests)
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.10** or higher (tested with 3.10, 3.13)
- **pip** (Python package manager)
- **Git** (optional, for version control)

### Step-by-Step (Windows PowerShell)

```powershell
# 1. Navigate to the project
cd d:\SIH-2026\SIH-198\starter_kit\starter

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize the database (if app.db doesn't exist or needs a reset)
python load_data.py
```

### Step-by-Step (Linux/macOS)

```bash
# 1. Navigate to the project
cd SIH-198/starter_kit/starter

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize the database
python load_data.py
```

---

## ▶️ Running the Application

```powershell
# Make sure the virtual environment is activated
.\venv\Scripts\Activate.ps1

# Start the Flask development server
python app.py
```

The application starts at: **http://127.0.0.1:5000**

### Available URLs

| URL | Description |
|---|---|
| `http://127.0.0.1:5000/` | Command Center Dashboard |
| `http://127.0.0.1:5000/network` | Recovery Network Map |
| `http://127.0.0.1:5000/impact` | Environmental Impact |
| `http://127.0.0.1:5000/simulator` | Recovery Simulator |
| `http://127.0.0.1:5000/batches` | Stock Ledger |
| `http://127.0.0.1:5000/matches` | Active Matches |
| `http://127.0.0.1:5000/partners` | Partner Facilities |
| `http://127.0.0.1:5000/audit` | Audit Trail |

### Manual API Testing (PowerShell)

```powershell
# Process a batch through the full pipeline
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/process_batch/BATCH-ZI2026-1014"

# List all batches
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/batches"

# Get impact stats
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/impact_stats"

# Run the simulator
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/simulate_recovery" `
  -ContentType "application/json" `
  -Body '{"compound": "Zinc Sulphate", "quantity_kg": 100, "severity": "Medium"}'
```

### Manual API Testing (curl)

```bash
# Process a batch
curl -X POST http://127.0.0.1:5000/api/process_batch/BATCH-ZI2026-1014

# List all batches
curl http://127.0.0.1:5000/api/batches

# Get impact stats
curl http://127.0.0.1:5000/api/impact_stats

# Run the simulator
curl -X POST http://127.0.0.1:5000/api/simulate_recovery \
  -H "Content-Type: application/json" \
  -d '{"compound": "Zinc Sulphate", "quantity_kg": 100, "severity": "Medium"}'
```

---

## 🧪 Testing

The project includes **78 unit tests** across 10 test files:

```powershell
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_dosage.py -v

# Run with coverage (if pytest-cov installed)
python -m pytest tests/ --cov=modules --cov-report=term-missing
```

### Test Coverage

| Test File | Tests | Coverage Area |
|---|---|---|
| `test_intake.py` | 4 | Whitelist compliance, accept/reject logic |
| `test_geolocation.py` | 5 | Pincode resolution, Haversine distance, city lookup |
| `test_matching.py` | 4 | Same-state match, fallback match, rejected batch handling |
| `test_dosage.py` | 6 | Severity tiers, foliar spray branch, invalid inputs |
| `test_pipeline.py` | 7 | End-to-end pipeline scenarios |
| `test_phase2.py` | 4 | Data integrity, batch creation, idempotency |
| `test_phase3.py` | 10 | Match CRUD, status lifecycle, compound filtering |
| `test_phase4.py` | 12 | Partner assignment, capacity validation, reassignment |
| `test_phase5.py` | 20 | SHA-256 audit chain, tamper detection, re-test feedback |
| `test_enhancements.py` | 6 | Impact stats API, network data API, simulator API |
| **Total** | **78** | **Full pipeline + API + audit + enhancements** |

### Latest Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
collected 78 items

tests/test_dosage.py ......                                              [  7%]
tests/test_enhancements.py ......                                        [ 15%]
tests/test_geolocation.py .....                                          [ 21%]
tests/test_intake.py ....                                                [ 26%]
tests/test_matching.py ....                                              [ 32%]
tests/test_phase2.py ....                                                [ 37%]
tests/test_phase3.py ..........                                          [ 50%]
tests/test_phase4.py ............                                        [ 65%]
tests/test_phase5.py ....................                                [ 91%]
tests/test_pipeline.py .......                                           [100%]

============================= 78 passed in 15.56s =============================
```

---

## 📊 Data Sources & References

| Data | Source | Notes |
|---|---|---|
| **Soil Deficiency Data** | ICAR All India Soil Survey (2012–2018) | 29 states/UTs, Zn/Fe/K deficiency mapping |
| **Dosage Rates** | ICAR General Recommended Doses (GRD) | ±25% severity-adjusted application rates |
| **Ferrous Sulphate Foliar Spec** | ICAR Agronomic Guidelines | 1.0% FeSO₄ solution, 3–4 weekly sprays |
| **Expired Stock Data** | Synthetic demo data (45 batches) | Based on real pharmaceutical product references |
| **National Baseline** | Naik et al., 2024 | 49% Zn-deficient, >33% Fe-deficient nationally |

---

## ⚠️ Known Limitations & Scope

### Deliberately Out of Scope

- **Chemical Extraction**: Actual mineral extraction from expired medicines is assumed to be handled by certified partner facilities
- **Logistics & Transport**: Route optimization and material transport are not modeled
- **Combination Products**: Only single-compound medicines are supported (no multi-ingredient formulations)
- **Full ICAR STCR Equations**: Uses simplified GRD ±25% tables, not Soil Test Crop Response equations
- **Compounds Beyond 3**: Only Ferrous Sulphate, Zinc Sulphate, and Potassium Chloride are approved
- **AI/ML Components**: Core pipeline is intentionally rule-based for transparency and auditability

### Known Constraints

- **SQLite**: Single-writer concurrency model — suitable for demo/prototype, not production multi-user
- **Geolocation**: City lookup uses a manual table (~50 cities); pincodes use the `indiapins` package
- **Demo Partners**: Partner facilities are seeded as demo data, not real organizations
- **Soil Data**: Based on state-level aggregates, not field-level soil testing results

---

## 📜 License

This project was developed as part of the **Smart India Hackathon (SIH) 2026** competition.

---

<div align="center">

**Built with ❤️ for India's agricultural future**

*Nirmūla — Turning pharmaceutical waste into agricultural wealth*

</div>
]]>
