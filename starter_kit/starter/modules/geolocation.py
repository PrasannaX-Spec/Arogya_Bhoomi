"""
Module 4: Geolocation
Resolves location strings (city/state or pincode) to coordinates.

The demo data uses "City, State" format strings. The indiapins package only
supports pincode lookup, so we use a hardcoded coordinate lookup for known
demo cities as a fallback.
"""

import math
import re

try:
    import indiapins
    INDIAPINS_AVAILABLE = True
except ImportError:
    INDIAPINS_AVAILABLE = False

# Hardcoded coordinates for the ~12 cities that appear in demo_intake.csv
# plus additional state capitals as fallback for matching.
# Sources: standard geographic coordinates.
CITY_COORDINATES = {
    # Demo data cities
    "hisar": {"district": "Hisar", "state": "Haryana", "latitude": 29.1547, "longitude": 75.7230},
    "coimbatore": {"district": "Coimbatore", "state": "Tamil Nadu", "latitude": 11.0168, "longitude": 76.9558},
    "bhubaneswar": {"district": "Khurda", "state": "Odisha", "latitude": 20.2961, "longitude": 85.8245},
    "kochi": {"district": "Ernakulam", "state": "Kerala", "latitude": 9.9312, "longitude": 76.2673},
    "patna": {"district": "Patna", "state": "Bihar", "latitude": 25.6093, "longitude": 85.1376},
    "bengaluru rural": {"district": "Bengaluru Rural", "state": "Karnataka", "latitude": 13.2257, "longitude": 77.5750},
    "bengaluru": {"district": "Bengaluru Urban", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946},
    "nagpur": {"district": "Nagpur", "state": "Maharashtra", "latitude": 21.1458, "longitude": 79.0882},
    "indore": {"district": "Indore", "state": "Madhya Pradesh", "latitude": 22.7196, "longitude": 75.8577},
    "meerut": {"district": "Meerut", "state": "Uttar Pradesh", "latitude": 28.9845, "longitude": 77.7064},
    "ludhiana": {"district": "Ludhiana", "state": "Punjab", "latitude": 30.9010, "longitude": 75.8573},
    "ahmedabad": {"district": "Ahmedabad", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714},
    "jaipur": {"district": "Jaipur", "state": "Rajasthan", "latitude": 26.9124, "longitude": 75.7873},
    # Additional state capitals for fallback matching
    "chandigarh": {"district": "Chandigarh", "state": "Chandigarh", "latitude": 30.7333, "longitude": 76.7794},
    "new delhi": {"district": "New Delhi", "state": "Delhi / NCR", "latitude": 28.6139, "longitude": 77.2090},
    "delhi": {"district": "New Delhi", "state": "Delhi / NCR", "latitude": 28.6139, "longitude": 77.2090},
    "mumbai": {"district": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777},
    "hyderabad": {"district": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867},
    "chennai": {"district": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707},
    "kolkata": {"district": "Kolkata", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639},
    "lucknow": {"district": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462},
    "bhopal": {"district": "Bhopal", "state": "Madhya Pradesh", "latitude": 23.2599, "longitude": 77.4126},
    "thiruvananthapuram": {"district": "Thiruvananthapuram", "state": "Kerala", "latitude": 8.5241, "longitude": 76.9366},
    "ranchi": {"district": "Ranchi", "state": "Jharkhand", "latitude": 23.3441, "longitude": 85.3096},
    "raipur": {"district": "Raipur", "state": "Chhattisgarh", "latitude": 21.2514, "longitude": 81.6296},
    "panaji": {"district": "North Goa", "state": "Goa", "latitude": 15.4909, "longitude": 73.8278},
    "srinagar": {"district": "Srinagar", "state": "Jammu & Kashmir", "latitude": 34.0837, "longitude": 74.7973},
    "guwahati": {"district": "Kamrup", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362},
    "dehradun": {"district": "Dehradun", "state": "Uttarakhand", "latitude": 30.3165, "longitude": 78.0322},
    "vijayawada": {"district": "Krishna", "state": "Andhra Pradesh", "latitude": 16.5062, "longitude": 80.6480},
    "gangtok": {"district": "East Sikkim", "state": "Sikkim", "latitude": 27.3314, "longitude": 88.6138},
}

# State centroid coordinates for fallback when city is not found
STATE_CENTROIDS = {
    "haryana": {"latitude": 29.0588, "longitude": 76.0856},
    "tamil nadu": {"latitude": 11.1271, "longitude": 78.6569},
    "odisha": {"latitude": 20.9517, "longitude": 85.0985},
    "kerala": {"latitude": 10.8505, "longitude": 76.2711},
    "bihar": {"latitude": 25.0961, "longitude": 85.3131},
    "karnataka": {"latitude": 15.3173, "longitude": 75.7139},
    "maharashtra": {"latitude": 19.7515, "longitude": 75.7139},
    "madhya pradesh": {"latitude": 22.9734, "longitude": 78.6569},
    "uttar pradesh": {"latitude": 26.8467, "longitude": 80.9462},
    "punjab": {"latitude": 31.1471, "longitude": 75.3412},
    "gujarat": {"latitude": 22.2587, "longitude": 71.1924},
    "rajasthan": {"latitude": 27.0238, "longitude": 74.2179},
    "delhi / ncr": {"latitude": 28.7041, "longitude": 77.1025},
    "andhra pradesh": {"latitude": 15.9129, "longitude": 79.7400},
    "telangana": {"latitude": 18.1124, "longitude": 79.0193},
    "chhattisgarh": {"latitude": 21.2787, "longitude": 81.8661},
    "goa": {"latitude": 15.2993, "longitude": 74.1240},
    "jammu & kashmir": {"latitude": 33.7782, "longitude": 76.5762},
    "west bengal": {"latitude": 22.9868, "longitude": 87.8550},
    "jharkhand": {"latitude": 23.6102, "longitude": 85.2799},
    "assam": {"latitude": 26.2006, "longitude": 92.9376},
    "uttarakhand": {"latitude": 30.0668, "longitude": 79.0193},
    "arunachal pradesh": {"latitude": 28.2180, "longitude": 94.7278},
    "manipur": {"latitude": 24.6637, "longitude": 93.9063},
    "meghalaya": {"latitude": 25.4670, "longitude": 91.3662},
    "mizoram": {"latitude": 23.1645, "longitude": 92.9376},
    "nagaland": {"latitude": 26.1584, "longitude": 94.5624},
    "tripura": {"latitude": 23.9408, "longitude": 91.9882},
    "sikkim": {"latitude": 27.5330, "longitude": 88.5122},
}


def _parse_location_string(location_string):
    """
    Parse a location string like "City, State" or "Pincode" into components.

    Returns:
        dict with 'type' ('city_state' or 'pincode'), and relevant fields.
    """
    location_string = location_string.strip()

    # Check if it's a 6-digit pincode
    if re.match(r'^\d{6}$', location_string):
        return {"type": "pincode", "pincode": location_string}

    # Try "City, State" format
    if "," in location_string:
        parts = [p.strip() for p in location_string.split(",", 1)]
        return {"type": "city_state", "city": parts[0], "state": parts[1]}

    # Single word — treat as city name
    return {"type": "city_state", "city": location_string, "state": None}


def _resolve_via_pincode(pincode):
    """Resolve a pincode using the indiapins package."""
    if not INDIAPINS_AVAILABLE:
        return None

    try:
        results = indiapins.matching(pincode)
        if results and len(results) > 0:
            first = results[0]
            return {
                "district": first.get("District", "").title(),
                "state": first.get("State", "").title(),
                "latitude": float(first.get("Latitude", 0)),
                "longitude": float(first.get("Longitude", 0)),
                "source": "indiapins",
            }
    except (ValueError, Exception):
        pass
    return None


def _resolve_via_city_lookup(city, state):
    """Resolve a city/state string using the hardcoded coordinate lookup."""
    city_lower = city.lower().strip()

    # Direct city match
    if city_lower in CITY_COORDINATES:
        entry = CITY_COORDINATES[city_lower]
        return {
            "district": entry["district"],
            "state": entry["state"],
            "latitude": entry["latitude"],
            "longitude": entry["longitude"],
            "source": "city_lookup",
        }

    # If city not found but state is known, use state centroid
    if state:
        state_lower = state.lower().strip()
        if state_lower in STATE_CENTROIDS:
            centroid = STATE_CENTROIDS[state_lower]
            return {
                "district": city,
                "state": state.strip(),
                "latitude": centroid["latitude"],
                "longitude": centroid["longitude"],
                "source": "state_centroid_fallback",
            }

    return None


def resolve_location(location_string):
    """
    Resolve a location string to geographic coordinates.

    Accepts:
    - "City, State" format (e.g., "Hisar, Haryana")
    - 6-digit Indian pincode (e.g., "125001")

    Returns:
        dict with 'district', 'state', 'latitude', 'longitude', 'source'
        or dict with 'error' if resolution fails.
    """
    if not location_string or not location_string.strip():
        return {"error": "Empty location string"}

    parsed = _parse_location_string(location_string)

    if parsed["type"] == "pincode":
        result = _resolve_via_pincode(parsed["pincode"])
        if result:
            return result
        return {"error": f"Could not resolve pincode '{parsed['pincode']}'"}

    # City/State resolution
    city = parsed["city"]
    state = parsed.get("state")

    result = _resolve_via_city_lookup(city, state)
    if result:
        return result

    return {"error": f"Could not resolve location '{location_string}'"}


def distance_km(loc1, loc2):
    """
    Compute the great-circle distance between two points using the Haversine formula.

    Args:
        loc1: tuple (latitude, longitude) in decimal degrees
        loc2: tuple (latitude, longitude) in decimal degrees

    Returns:
        Distance in kilometers.
    """
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in km
    r = 6371.0
    return r * c
