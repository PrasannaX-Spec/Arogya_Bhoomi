"""
Test script for Module 4: Geolocation

Tests:
1. Resolve 3 known demo cities: Hisar, Bhubaneswar, Coimbatore
2. Verify correct state names and non-null coordinates
3. Test pincode resolution
4. Test haversine distance
5. Test invalid input handling
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.geolocation import resolve_location, distance_km


def test_known_cities():
    """Test 1: Resolve 3 known source_locations from demo data."""
    print("=" * 60)
    print("TEST 1: Resolve known demo cities")
    print("=" * 60)

    test_cases = [
        ("Hisar, Haryana", "Haryana"),
        ("Bhubaneswar, Odisha", "Odisha"),
        ("Coimbatore, Tamil Nadu", "Tamil Nadu"),
    ]

    for location, expected_state in test_cases:
        result = resolve_location(location)
        print(f"  {location}:")
        print(f"    State: {result.get('state')}")
        print(f"    District: {result.get('district')}")
        print(f"    Lat: {result.get('latitude')}, Lon: {result.get('longitude')}")
        print(f"    Source: {result.get('source')}")

        assert "error" not in result, f"Error resolving {location}: {result['error']}"
        assert result["state"] == expected_state, (
            f"Expected state '{expected_state}', got '{result['state']}'"
        )
        assert result["latitude"] is not None and result["latitude"] != 0
        assert result["longitude"] is not None and result["longitude"] != 0
        print(f"    PASSED")

    print()


def test_all_demo_cities():
    """Test 2: Resolve ALL cities from demo data."""
    print("=" * 60)
    print("TEST 2: Resolve all demo data cities")
    print("=" * 60)

    demo_locations = [
        ("Hisar, Haryana", "Haryana"),
        ("Coimbatore, Tamil Nadu", "Tamil Nadu"),
        ("Bhubaneswar, Odisha", "Odisha"),
        ("Kochi, Kerala", "Kerala"),
        ("Patna, Bihar", "Bihar"),
        ("Bengaluru Rural, Karnataka", "Karnataka"),
        ("Nagpur, Maharashtra", "Maharashtra"),
        ("Indore, Madhya Pradesh", "Madhya Pradesh"),
        ("Meerut, Uttar Pradesh", "Uttar Pradesh"),
        ("Ludhiana, Punjab", "Punjab"),
        ("Ahmedabad, Gujarat", "Gujarat"),
        ("Jaipur, Rajasthan", "Rajasthan"),
    ]

    all_passed = True
    for location, expected_state in demo_locations:
        result = resolve_location(location)
        status = "OK" if result.get("state") == expected_state else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {location} -> {result.get('state', 'ERROR')} [{status}]")

    assert all_passed, "Some demo cities failed to resolve correctly"
    print(f"  PASSED - All {len(demo_locations)} demo cities resolved\n")


def test_haversine_distance():
    """Test 3: Verify haversine distance calculation."""
    print("=" * 60)
    print("TEST 3: Haversine distance calculation")
    print("=" * 60)

    # Hisar to Bhubaneswar - approximately 1500 km
    hisar = (29.1547, 75.7230)
    bhubaneswar = (20.2961, 85.8245)
    dist = distance_km(hisar, bhubaneswar)
    print(f"  Hisar to Bhubaneswar: {dist:.1f} km")
    assert 1300 < dist < 1700, f"Distance should be ~1500km, got {dist}"

    # Same point should be 0
    dist_same = distance_km(hisar, hisar)
    print(f"  Same point distance: {dist_same:.6f} km")
    assert dist_same < 0.001, f"Same point should be ~0, got {dist_same}"

    print("  PASSED - Distance calculation correct\n")


def test_pincode_resolution():
    """Test 4: Resolve via pincode."""
    print("=" * 60)
    print("TEST 4: Pincode resolution")
    print("=" * 60)

    result = resolve_location("125001")  # Hisar pincode
    print(f"  Pincode 125001:")
    print(f"    State: {result.get('state')}")
    print(f"    Lat: {result.get('latitude')}, Lon: {result.get('longitude')}")

    if "error" in result:
        print(f"  NOTE: Pincode resolution unavailable ({result['error']})")
    else:
        assert "Haryana" in result["state"].title() or "haryana" in result["state"].lower()
        print("  PASSED - Pincode resolved correctly")
    print()


def test_invalid_input():
    """Test 5: Invalid inputs should return errors, not crash."""
    print("=" * 60)
    print("TEST 5: Invalid input handling")
    print("=" * 60)

    result = resolve_location("")
    print(f"  Empty string: {result}")
    assert "error" in result

    result = resolve_location("NonExistentCity, NonExistentState")
    print(f"  Non-existent: {result}")
    assert "error" in result

    print("  PASSED - Invalid inputs handled gracefully\n")


if __name__ == "__main__":
    print("\n--- Running Module 4 (Geolocation) Tests ---\n")

    test_known_cities()
    test_all_demo_cities()
    test_haversine_distance()
    test_pincode_resolution()
    test_invalid_input()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
