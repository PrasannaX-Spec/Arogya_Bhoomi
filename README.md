# 🌱 Nirmūla Recovery Platform (SIH-198)

> **Traceable Recovery & Deployment Platform for Micronutrient Compounds from Expired Pharmaceuticals**  
> *Smart India Hackathon (SIH) 2026 — Problem Statement ID: 198*

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-78%20Passed-brightgreen?logo=pytest&logoColor=white)

---

## 📌 Overview

India faces a dual challenge: tons of expired single-compound pharmaceutical stock are discarded annually, while Indian agricultural soils suffer from widespread micronutrient deficiencies (**49% Zinc deficient, >33% Iron deficient**).

**Nirmūla** creates a verifiable, rule-based circular economy bridge. It collects expired single-compound medicines (Ferrous Sulphate, Zinc Sulphate, Potassium Chloride), verifies their composition, matches them to deficient agricultural regions, and calculates safe, ICAR-compliant dosage recommendations.

---

## 🔄 4-Stage Recovery Pipeline

```
[1. Intake & Whitelist] ──► [2. Geolocation] ──► [3. Soil Matching] ──► [4. ICAR Dosage]
  Exact compound match        Pincode/City GPS     Deficient region      Application rate &
  (FeSO₄, ZnSO₄, KCl)        resolution           matching              Foliar spray spec
```

1. **Intake & Whitelist Compliance**: Accepts approved single-compound minerals; rejects combination products.
2. **Geolocation Resolution**: Resolves pincodes and cities to GPS coordinates for proximity calculations.
3. **Soil-Deficiency Matching**: Pairs stock with deficient Indian states (same-state priority or nearest fallback).
4. **Dosage Recommendation**: Computes ICAR GRD rates (±25% severity adjustment) and foliar spray specs.

---

## ✨ Key Platform Features

- **Command Center Dashboard (`/`)**: Live KPI metrics, 4-stage circular snapshot, Chart.js visualizations, and end-to-end recovery workflow.
- **Interactive Recovery Map (`/network`)**: Leaflet.js map showing pharma sources, deficiency targets, partner facilities, and flow lines.
- **Environmental Impact Calculator (`/impact`)**: Stoichiometric elemental yields (Fe, Zn, K) and addressable farmland area (ha).
- **What-If Soil Recovery Simulator (`/simulator`)**: Scenario simulator calculating land remediation capacity for any stock volume.
- **Cryptographic Audit Trail (`/audit`)**: SHA-256 hash-linked append-only event logging for end-to-end batch traceability.
- **Soil Re-Test Feedback Loop (`/retests`)**: Post-deployment tracking to monitor soil remediation progress.

---

## 💻 Tech Stack

- **Backend**: Python 3.10+, Flask 3.0+, SQLite3
- **Frontend**: HTML5, Vanilla CSS, Jinja2, Chart.js 4, Leaflet.js 1.9
- **Geolocation**: `indiapins` package & Haversine distance formula
- **Testing**: `pytest` (78 tests, 100% pass rate)

---

## 🚀 Quick Start Guide

### 1. Installation

```bash
# Navigate to project root
cd starter_kit/starter

# Create & activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database & Start Server

```bash
# Populate SQLite database from reference datasets
python load_data.py

# Launch Flask Application
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Running Tests

```bash
# Run complete test suite (78 tests)
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```text
SIH-198/
├── README.md                      # Project documentation
├── PRD.md                         # Product Requirements Document
├── PROJECT_UNDERSTANDING.md       # Technical specification
└── starter_kit/starter/
    ├── app.py                     # Main Flask Application & REST API
    ├── app.db                     # SQLite Database
    ├── load_data.py               # Database Initializer Script
    ├── modules/                   # Pipeline Modules
    │   ├── intake.py              # Module 1: Whitelist & Compliance
    │   ├── geolocation.py         # Module 4: Geolocation Resolution
    │   ├── matching.py            # Module 2: Soil Matching
    │   └── dosage.py              # Module 3: ICAR Dosage Calculator
    ├── templates/                 # UI HTML Templates (Dashboard, Map, Impact, etc.)
    ├── static/                    # CSS Stylesheets & JavaScript
    ├── data/                      # JSON & CSV Reference Datasets
    └── tests/                     # 78 Automated Unit & API Tests
```

---

## 🌐 Key API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/api/process_batch/<id>` | `POST` | Run 4-stage pipeline for a batch |
| `/api/batches` | `GET / POST` | List or log intake batches |
| `/api/matches` | `GET` | Retrieve matched batches and state targets |
| `/api/impact_stats` | `GET` | Get total elemental nutrient yield & hectares |
| `/api/network_data` | `GET` | Map nodes (sources, targets, partners) |
| `/api/simulate_recovery` | `POST` | Run What-If soil remediation simulator |
| `/api/audit/<batch_id>` | `GET` | Fetch SHA-256 hash-linked audit trail |

---

<div align="center">
  <sub>SIH 2026 — Problem Statement 198 | Built for Sustainable Agricultural Remediation</sub>
</div>
