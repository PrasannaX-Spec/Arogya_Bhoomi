# 🌱 Arogya Bhoomi

> **Healthy Soil • Healthy Life**  
> *Traceable Recovery & Deployment Platform for Micronutrient Compounds from Expired Pharmaceuticals*  
> *Smart India Hackathon (SIH) 2026 — Problem Statement ID: 198*

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-4.2+-red?logo=adobe&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-88%20Passed-brightgreen?logo=pytest&logoColor=white)

---

## 📌 Problem Being Solved

India faces a dual agricultural and pharmaceutical management challenge:
- Tons of single-compound expired pharmaceutical stocks are discarded annually without structured circular utilization.
- Indian agricultural soils suffer from severe micronutrient deficiencies (**49% Zinc deficient**, **>33% Iron deficient**, and **significant Potassium deficits**).

**Arogya Bhoomi** creates a transparent, verifiable, rule-based circular recovery bridge. It registers expired pharmaceutical stock, validates chemical composition against an approved single-compound whitelist, resolves source locations, pairs inventory with documented state-level soil deficiency requirements, calculates agronomic dosage recommendations, assigns certified partner processing facilities, and logs every step in a tamper-evident audit ledger.

---

## 🧪 Core Approved Compounds

Arogya Bhoomi exclusively processes three high-purity single-compound micronutrient salts:

1. **Ferrous Sulphate ($\text{FeSO}_4 \cdot 7\text{H}_2\text{O}$)** — Target Nutrients: **Iron (Fe)** — *20.1% Elemental Fe*
2. **Zinc Sulphate ($\text{ZnSO}_4 \cdot 7\text{H}_2\text{O}$)** — Target Nutrients: **Zinc (Zn)** — *21.0% Elemental Zn*
3. **Potassium Chloride ($\text{KCl}$)** — Target Nutrients: **Potassium (K)** — *52.4% Elemental K*

> **Scope Boundary**: Combination products, multi-vitamin formulations, and complex active pharmaceutical ingredients (APIs) are strictly excluded at intake compliance.

---

## 🔄 Project Recovery Workflow

```text
Expired Pharmaceutical Stock
        ↓
Stock & Compliance
        ↓
Compound Validation
        ↓
Recovery Pipeline
        ↓
Location / Region Identification
        ↓
Soil Deficiency Matching
        ↓
Recovery Eligibility
        ↓
Partner Assignment
        ↓
Recovery / Handoff
        ↓
Audit Trail
        ↓
Acknowledgement PDF
        ↓
Recovery Map / Monitoring
```

---

## 🛠️ Key Platform Features & Core Capabilities

### 1. Stock & Compliance (`/stock`)
- Manages pharmaceutical inventory intake ledgers.
- Validates single-compound whitelist compliance and rejects multi-API combination drugs.
- Tracks manufacturing dates, expiry dates, batch quantities, and source locations across 45 demo intake records.

### 2. Recovery Pipeline (`/pipeline`)
- Automates the 4-stage recovery flow:
  1. **Intake & Compliance Check**: Validates batch single-compound purity.
  2. **Geolocation Resolution**: Resolves pincodes and source locations to geographic coordinates.
  3. **Soil Deficiency Search & Matching**: Pairs stock with deficient Indian state target regions.
  4. **Dosage Recommendation**: Generates application rates and foliar spray guidance.
- Assigns available certified partner facilities for reprocessing.
- **Individual Acknowledgement PDF Download**: Successful pipeline completions present a direct `📄 Download Acknowledgement PDF` button for that specific batch.

### 3. Rule-Based Dosage Calculator (`/dosage`)
- Employs a **Rule-Based Soil-Deficiency Dosage Adjustment Model** adjusting recommended base rates according to deficiency severity tiers (Low, Medium, High).
- **Soil Application Compounds (Zinc Sulphate & Potassium Chloride)**:
  - Zinc Sulphate: Base rate $37.5 \text{ kg/ha}$ (Severity multipliers: Low $0.75\times$, Medium $1.0\times$, High $1.25\times$).
  - Potassium Chloride: Base rate $40.0 \text{ kg/ha}$ (Severity multipliers: Low $0.75\times$, Medium $1.0\times$, High $1.25\times$).
- **Foliar Spray Compound (Ferrous Sulphate)**:
  - Specific Agronomic Guidance: **"3–4 sprays of 1.0% ferrous sulphate (FeSO4, 20% Fe) at weekly intervals."**

### 4. Interactive Recovery Map (`/soil-map`)
- Visualizes **29 soil-deficiency areas** across Indian states using Leaflet.js.
- **Element-Color Coded Markers**:
  - 🟢 **Zinc (Zn)**: Green (`#22c55e`)
  - 🔵 **Iron (Fe)**: Blue (`#2563eb`)
  - 🟠 **Potassium (K)**: Orange (`#f97316`)
  - ⚪ **Non-Usable Region**: Gray (`#6b7280`)
- Interactive click popups displaying State Name, Key Deficient Nutrients, Usable Compounds, and Element Badge.
- Includes coordinate jitter handling to separate overlapping state centroids and a clear visual map legend.

### 5. Tamper-Evident Audit Trail (`/audit`)
- Provides an **application-level tamper-evident hash-linked audit trail** using SHA-256 chain linkage (`previous_event_hash` $\to$ `event_hash`).
- Re-verifies mathematical chain integrity upon request.

### 6. Individual PDF Acknowledgement Generation
- Generates downloadable, in-memory PDF acknowledgement reports using ReportLab (`GET /api/reports/pdf/<batch_id>`).
- Includes batch metadata, compliance verification, soil match details, dosage recommendations, partner assignment, and audit events.
- Strictly validated: Only available for valid, successful, and matched pipeline operations.

---

## 🚫 Important Scope Boundaries & Clarifications

To maintain project transparency and evaluation integrity:

| Feature Area | Implementation Status | Clarification / Detail |
|---|---|---|
| **Combination Drugs** | ❌ Excluded | Only single-compound salts (FeSO₄, ZnSO₄, KCl) are accepted. |
| **Chemical Extraction** | 🛠️ External Workflow | Physical re-processing/extraction occurs at certified external partner facilities. |
| **Logistics Optimization** | ❌ Excluded | Vehicle routing & fleet logistics are outside current software scope. |
| **AI / ML Predictions** | ❌ Excluded | Platform uses transparent, deterministic, rule-based matching and ICAR dosage models. |
| **Blockchain** | ❌ Excluded | Audit trail uses an application-level SHA-256 hash chain, not distributed blockchain ledger. |
| **Live External APIs** | ❌ Excluded | Datasets (CPCB, ICAR deficiency data, pin codes) are built-in authoritative reference baselines. |
| **Reports Page / Dashboard** | ❌ Removed | There is **no separate `/reports` page or report table**. Only individual PDF downloads on `/pipeline`. |

---

## 💻 Navigation & Web UI Structure

- **Dashboard (`/`)**: High-level platform KPIs, circular recovery overview, and workflow guide.
- **Stock & Compliance (`/stock`)**: Stock ledger, batch registration, and compliance queue.
- **Recovery Pipeline (`/pipeline`)**: Step-by-step batch execution, soil matching, partner assignment, and PDF download.
- **Dosage Calculator (`/dosage`)**: Independent What-If recovery simulator and ICAR dosage guide.
- **Recovery Map (`/soil-map`)**: Interactive map with 29 color-coded deficiency area markers.
- **About (`/about`)**: Methodology, chemical standards, regulatory compliance, and project scope details.

---

## 💻 Tech Stack

- **Backend**: Python 3.10+, Flask 3.0+, SQLite3
- **PDF Generation**: ReportLab 4.2+
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+), Leaflet.js 1.9
- **Geolocation**: `indiapins` dataset & Haversine distance formula
- **Testing**: `pytest` 9.1+ (**88 unit & API tests, 100% pass rate**)

---

## 🚀 Quick Start Guide

### 1. Installation

```bash
# Navigate to application directory
cd starter_kit/starter

# Create & activate Python virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database & Start Server

```bash
# Seed SQLite database with reference datasets (29 deficiency regions, 45 demo batches, 6 partners)
python load_data.py

# Launch Flask development server
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Running Automated Tests

```bash
# Run full automated test suite (88 tests)
python -m pytest tests
```

---

## 📁 Repository & Project Structure

```text
SIH-198/
├── README.md                           # Master project documentation
└── starter_kit/starter/
    ├── app.py                          # Main Flask Application & REST API endpoints
    ├── app.db                          # SQLite Database
    ├── load_data.py                    # Database initializer & seeder script
    ├── requirements.txt                # Python dependencies (Flask, ReportLab, pytest)
    ├── modules/                        # Business Logic Modules
    │   ├── intake.py                   # Module 1: Whitelist & Compliance
    │   ├── geolocation.py              # Module 4: Geolocation Resolution
    │   ├── matching.py                 # Module 2: Soil Matching Engine
    │   └── dosage.py                   # Module 3: Rule-Based Dosage Calculator
    ├── templates/                      # UI Templates
    │   ├── base.html                   # Master layout with sidebar navigation
    │   ├── index.html                  # Dashboard
    │   ├── stock.html                  # Stock & Compliance Ledger
    │   ├── pipeline.html               # Recovery Pipeline & PDF Download
    │   ├── dosage.html                 # Dosage Calculator & Simulator
    │   ├── soil_map.html               # Recovery Map with 29 Deficiency Markers
    │   └── about.html                  # Methodology & System Specs
    ├── static/                         # CSS Stylesheets & JavaScript Assets
    │   ├── style.css                   # Custom CSS Design System
    │   └── script.js                  # Frontend Interactivity
    ├── data/                           # JSON Reference Datasets
    │   ├── compounds.json              # Whitelisted mineral salts
    │   └── soil_deficiency.json        # 29 State soil deficiency baseline
    └── tests/                          # Automated Test Suite (88 tests)
        ├── test_dosage.py
        ├── test_enhancements.py
        ├── test_final_restructure.py   # Web routes, PDF download & eligibility tests
        ├── test_geolocation.py
        ├── test_intake.py
        ├── test_matching.py
        ├── test_phase2.py
        ├── test_phase3.py
        ├── test_phase4.py
        ├── test_phase5.py
        └── test_pipeline.py
```

---

## 🔍 Feature Matrix: Implemented vs Future Scope

### Currently Implemented
- ✅ Whitelist compliance engine for single-compound salts
- ✅ Pincode to coordinate resolution & distance calculation
- ✅ State-level soil-deficiency matching engine
- ✅ Rule-based dosage calculation model with severity multipliers
- ✅ Ferrous Sulphate foliar spray guidance
- ✅ Interactive 29 deficiency markers map with element color coding
- ✅ Tamper-evident SHA-256 hash-linked audit chain
- ✅ Individual Acknowledgement PDF download for successful pipeline batches
- ✅ Certified partner capacity tracking & handoff logging

### Future Scope (Post-Hackathon)
- 🔮 Real-time CPCB / FDA portal API integration
- 🔮 Automated logistics & route optimization
- 🔮 Soil sensor IoT integration for live post-remediation feedback
- 🔮 Multi-facility enterprise access control (RBAC)

---

<div align="center">
  <sub>Smart India Hackathon (SIH) 2026 — Problem Statement 198 | Arogya Bhoomi — Healthy Soil • Healthy Life</sub>
</div>
