"""
Geographic and routing utilities.
Handles coordinate generation, route fetching, and location lookups.
"""

import math
import random
import logging
import requests


def generate_dwell_points(center, num_points=6, min_radius=0.002, max_radius=0.004):
    """
    Generate random GPS points around a center location to simulate small movements.
    Useful for simulating a stationary device with minor GPS drift.
    
    Args:
        center (tuple): (lat, lon) tuple of the center point
        num_points (int): Number of dwell points to generate
        min_radius (float): Minimum radius in meters (default 2cm)
        max_radius (float): Maximum radius in meters (default 4cm)
    
    Returns:
        list: List of (lat, lon) tuples around the center point
    """
    points = []
    lat, lon = center
    
    for _ in range(num_points):
        # Generate random angle and distance within the given radius range
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(min_radius, max_radius)
        
        # Convert meters to degrees
        # Latitude: 1 meter approximately equals 1/111111 degrees
        delta_lat = (distance * math.sin(angle)) / 111111.0
        
        # Longitude: 1 meter approximately equals 1/(111111 * cos(lat)) degrees
        delta_lon = (distance * math.cos(angle)) / (111111.0 * math.cos(math.radians(lat)))
        
        new_lat = lat + delta_lat
        new_lon = lon + delta_lon
        
        points.append((new_lat, new_lon))
    
    return points


def get_location_name(lat, lon):
    """
    Get human-readable location name from coordinates using OpenStreetMap Nominatim API.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    
    Returns:
        str: Location name or coordinates if lookup fails
    """
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en"
    headers = {
        "User-Agent": "GPS-Location-Simulator/1.0",  # Required by Nominatim Terms of Service
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "address" in data:
            # Try to create a concise address with key components
            address_parts = []
            address_keys = list(data["address"].keys())
            
            if address_keys and address_keys[0] in data["address"]:
                first_component = data["address"][address_keys[0]]
                address_parts.append(first_component)
            
            if "city" in data["address"]:
                address_parts.append(data["address"]["city"])
            
            if "country" in data["address"]:
                address_parts.append(data["address"]["country"])
            
            if address_parts:
                return " - ".join(address_parts)
        
        # Fallback to display_name or coordinates if the above fails
        if "display_name" in data:
            return data["display_name"]
        
        return f"{lat:.5f}, {lon:.5f}"
    
    except Exception as e:
        logging.warning(f"Could not get location name: {str(e)}")
        return f"{lat:.5f}, {lon:.5f}"


def get_route_from_osrm(start, end, mode='driving'):
    """
    Fetch a realistic route from Open Source Routing Machine (OSRM) API.
    
    Args:
        start (tuple): (lat, lon) tuple of start location
        end (tuple): (lat, lon) tuple of end location
        mode (str): Travel mode - 'driving', 'walking', or 'cycling'
    
    Returns:
        list: List of (lat, lon) waypoints forming the route, or empty list on error
    """
    valid_modes = ['driving', 'walking', 'cycling']
    
    if mode not in valid_modes:
        logging.warning(f"Invalid mode {mode}, defaulting to driving")
        mode = 'driving'

    # Construct OSRM API URL
    base_url = f"https://router.project-osrm.org/route/v1/{mode}/"
    url = f"{base_url}{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"OSRM API Error: {str(e)}")
        return []

    route_data = response.json()
    
    # Validate OSRM response
    if not route_data.get('routes'):
        logging.error("No route found - check locations are valid and reachable")
        return []
    
    if 'geometry' not in route_data['routes'][0]:
        logging.error("Invalid route geometry from OSRM")
        return []

    # Extract coordinates and convert from GeoJSON format (lon, lat) to (lat, lon)
    route_geometry = route_data['routes'][0]['geometry']['coordinates']
    route_list = [(lat, lon) for lon, lat in route_geometry]

    # Ensure endpoint is included in the route
    if route_list[-1] != end:
        route_list.append(end)
    
    return route_list


def validate_coords(input_str):
    """
    Validate and parse coordinate input string.
    
    Args:
        input_str (str): Coordinate string in format "lat,lon"
    
    Returns:
        tuple: (lat, lon) tuple
    
    Raises:
        SystemExit: If coordinates are invalid
    """
    try:
        lat, lon = map(float, input_str.split(','))
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
        
        return (lat, lon)
    except:
        logging.error("Invalid coordinates. Use decimal format: 37.7749,-122.4194")
        raise SystemExit(1)
