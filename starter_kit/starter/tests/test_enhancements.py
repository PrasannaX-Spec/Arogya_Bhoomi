"""
test_enhancements.py — Unit tests for Nirmūla Platform UI & Analytics Enhancements
Tests:
  1. GET /api/impact_stats — Environmental & Agricultural Impact Metrics
  2. GET /api/network_data — Recovery Network Geo-nodes & Traceability Flows
  3. POST /api/simulate_recovery — What-If Simulator (Soil Application & Foliar Branch)
  4. POST /api/simulate_recovery — Input validation & error handling
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_impact_stats_api(client):
    """Test 1: Verify GET /api/impact_stats returns dynamic impact metrics."""
    response = client.get('/api/impact_stats')
    assert response.status_code == 200
    data = response.get_json()

    assert "pharma_stock_tracked_kg" in data
    assert data["pharma_stock_tracked_kg"] > 0
    assert "batches_processed" in data
    assert data["batches_processed"] == 45

    assert "elemental_nutrients_kg" in data
    elem = data["elemental_nutrients_kg"]
    assert "iron_fe" in elem
    assert "zinc_zn" in elem
    assert "potassium_k" in elem
    assert "total_elemental" in elem

    assert "addressable_hectares" in data
    assert data["addressable_hectares"] > 0
    assert "disclaimer" in data


def test_network_data_api(client):
    """Test 2: Verify GET /api/network_data returns geo-referenced network nodes & flows."""
    response = client.get('/api/network_data')
    assert response.status_code == 200
    data = response.get_json()

    assert "sources" in data
    assert len(data["sources"]) > 0
    assert "deficiencies" in data
    assert len(data["deficiencies"]) > 0
    assert "partners" in data
    assert len(data["partners"]) > 0
    assert "flows" in data

    sample_src = data["sources"][0]
    assert "latitude" in sample_src
    assert "longitude" in sample_src
    assert "compound" in sample_src
    assert "quantity_kg" in sample_src


def test_simulator_api_valid_zinc_sulphate(client):
    """Test 3: Verify POST /api/simulate_recovery for Zinc Sulphate medium severity."""
    payload = {
        "compound_name": "Zinc Sulphate",
        "quantity_kg": 500.0,
        "severity": "Medium"
    }
    response = client.post('/api/simulate_recovery', json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["compound_name"] == "Zinc Sulphate"
    assert data["type"] == "soil_application"
    assert data["base_rate_kg_ha"] == 37.5
    assert data["potential_addressable_ha"] == round(500.0 / 37.5, 1)
    assert data["elemental_nutrient"]["elemental_kg"] == 105.0
    assert "calculation_breakdown" in data


def test_simulator_api_valid_ferrous_sulphate_foliar(client):
    """Test 4: Verify POST /api/simulate_recovery for Ferrous Sulphate foliar spray branch."""
    payload = {
        "compound_name": "Ferrous Sulphate",
        "quantity_kg": 500.0,
        "severity": "High"
    }
    response = client.post('/api/simulate_recovery', json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["compound_name"] == "Ferrous Sulphate"
    assert data["type"] == "foliar_spray"
    assert "foliar_spec" in data
    assert data["elemental_nutrient"]["symbol"] == "Fe"
    assert data["elemental_nutrient"]["elemental_kg"] == round(500.0 * 0.201, 2)
    assert data["potential_addressable_ha"] > 0


def test_simulator_api_valid_potassium_chloride(client):
    """Test 5: Verify POST /api/simulate_recovery for Potassium Chloride low severity."""
    payload = {
        "compound_name": "Potassium Chloride",
        "quantity_kg": 1000.0,
        "severity": "Low"
    }
    response = client.post('/api/simulate_recovery', json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["compound_name"] == "Potassium Chloride"
    assert data["type"] == "soil_application"
    assert data["base_rate_kg_ha"] == 30.0
    assert data["potential_addressable_ha"] == round(1000.0 / 30.0, 1)
    assert data["elemental_nutrient"]["symbol"] == "K"
    assert data["elemental_nutrient"]["elemental_kg"] == 524.0


def test_simulator_api_invalid_inputs(client):
    """Test 6: Verify error handling for invalid simulator inputs."""
    # Invalid compound name
    res1 = client.post('/api/simulate_recovery', json={"compound_name": "Zincovit", "quantity_kg": 500, "severity": "Medium"})
    assert res1.status_code == 400
    assert "Invalid compound" in res1.get_json()["error"]

    # Zero or negative quantity
    res2 = client.post('/api/simulate_recovery', json={"compound_name": "Zinc Sulphate", "quantity_kg": -10, "severity": "Medium"})
    assert res2.status_code == 400
    assert "positive number" in res2.get_json()["error"]

    # Invalid severity tier
    res3 = client.post('/api/simulate_recovery', json={"compound_name": "Zinc Sulphate", "quantity_kg": 500, "severity": "Critical"})
    assert res3.status_code == 400
    assert "Invalid severity tier" in res3.get_json()["error"]
