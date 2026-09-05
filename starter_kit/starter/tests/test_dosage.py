"""
Test script for Module 3: Dosage Recommendation

Tests:
1. Zinc Sulphate "Low" -> soil_application, rate = 37.5 * 1.25 = 46.875
2. Ferrous Sulphate "Medium" -> foliar_spray, NOT crash/null
3. Potassium Chloride "High" -> soil_application, rate = 30 * 0.75 = 22.5
4. All severity tiers for Ferrous Sulphate (none should crash)
5. Invalid severity tier -> error
6. Invalid compound -> error
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.dosage import get_dosage


def test_zinc_sulphate_low():
    """Test 1: Zinc Sulphate at Low severity."""
    print("=" * 60)
    print("TEST 1: Zinc Sulphate, Low severity")
    print("=" * 60)

    result = get_dosage("Zinc Sulphate", "Low")
    print(f"  Type: {result.get('type')}")
    print(f"  Base rate: {result.get('base_rate_kg_ha')}")
    print(f"  Multiplier: {result.get('severity_multiplier')}")
    print(f"  Adjusted rate: {result.get('rate_kg_ha')}")
    print(f"  Unit: {result.get('unit')}")

    assert result["type"] == "soil_application"
    assert result["rate_kg_ha"] == 46.88 or abs(result["rate_kg_ha"] - 46.875) < 0.01
    assert result["severity_multiplier"] == 1.25
    print("  PASSED - Zinc Sulphate Low = GRD + 25%\n")


def test_ferrous_sulphate_medium():
    """Test 2: Ferrous Sulphate at Medium severity -> foliar spray, NOT crash."""
    print("=" * 60)
    print("TEST 2: Ferrous Sulphate, Medium severity (CRITICAL)")
    print("=" * 60)

    result = get_dosage("Ferrous Sulphate", "Medium")
    print(f"  Type: {result.get('type')}")
    print(f"  Spec: {result.get('spec')}")
    print(f"  Note: {result.get('note')}")
    print(f"  Source: {result.get('source')}")

    assert "error" not in result, f"Should not error: {result.get('error')}"
    assert result["type"] == "foliar_spray", f"Should be foliar_spray, got {result['type']}"
    assert result["spec"] is not None, "Foliar spec should not be None"
    assert "1.0%" in result["spec"], "Should contain 1.0% concentration"
    print("  PASSED - Ferrous Sulphate returns foliar spec (not crash/null)\n")


def test_potassium_chloride_high():
    """Test 3: Potassium Chloride at High severity."""
    print("=" * 60)
    print("TEST 3: Potassium Chloride, High severity")
    print("=" * 60)

    result = get_dosage("Potassium Chloride", "High")
    print(f"  Type: {result.get('type')}")
    print(f"  Base rate: {result.get('base_rate_kg_ha')}")
    print(f"  Multiplier: {result.get('severity_multiplier')}")
    print(f"  Adjusted rate: {result.get('rate_kg_ha')}")

    assert result["type"] == "soil_application"
    assert result["rate_kg_ha"] == 22.5
    assert result["severity_multiplier"] == 0.75
    print("  PASSED - Potassium Chloride High = GRD - 25%\n")


def test_ferrous_sulphate_all_tiers():
    """Test 4: Ferrous Sulphate should return foliar_spray for ALL severity tiers."""
    print("=" * 60)
    print("TEST 4: Ferrous Sulphate at all severity tiers")
    print("=" * 60)

    for tier in ["Low", "Medium", "High"]:
        result = get_dosage("Ferrous Sulphate", tier)
        print(f"  {tier}: type={result.get('type')}, spec={result.get('spec', 'N/A')[:50]}")
        assert "error" not in result, f"Error at {tier}: {result.get('error')}"
        assert result["type"] == "foliar_spray", f"Should be foliar at {tier}"

    print("  PASSED - All tiers return foliar spec without crash\n")


def test_invalid_severity():
    """Test 5: Invalid severity tier should return error."""
    print("=" * 60)
    print("TEST 5: Invalid severity tier")
    print("=" * 60)

    result = get_dosage("Zinc Sulphate", "Critical")
    print(f"  Error: {result.get('error')}")
    assert "error" in result
    print("  PASSED - Invalid severity handled\n")


def test_invalid_compound():
    """Test 6: Invalid compound should return error."""
    print("=" * 60)
    print("TEST 6: Invalid compound name")
    print("=" * 60)

    result = get_dosage("Zincovit", "Medium")
    print(f"  Error: {result.get('error')}")
    assert "error" in result
    print("  PASSED - Invalid compound handled\n")


if __name__ == "__main__":
    print("\n--- Running Module 3 (Dosage Recommendation) Tests ---\n")

    test_zinc_sulphate_low()
    test_ferrous_sulphate_medium()
    test_potassium_chloride_high()
    test_ferrous_sulphate_all_tiers()
    test_invalid_severity()
    test_invalid_compound()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
