import argparse
import subprocess
import time
import shutil
import logging
import requests
import sys
import termios
import tty
import select
import math
import random


# Configure logging with colors and better formatting
logging.basicConfig(
    format="\033[94m%(asctime)s\033[0m - \033[92m%(levelname)s\033[0m - %(message)s",
    level=logging.INFO,
)

def is_xcrun_available():
    """Check if xcrun is available on the system."""
    if shutil.which("xcrun") is None:
        logging.error("❌ 'xcrun' command not found. Install Xcode Command Line Tools.")
        return False
    return True

def generate_dwell_points(center, num_points=6, min_radius=0.002, max_radius=0.004):
    """
    Generates random points around a center location to simulate small movements.
    
    :param center: Tuple (lat, lon) of the center point
    :param num_points: Number of dwell points to generate
    :param min_radius: Minimum radius in meters (2 cm)
    :param max_radius: Maximum radius in meters (4 cm)
    :return: List of (lat, lon) points around the center
    """
    points = []
    lat, lon = center
    for _ in range(num_points):
        # Random angle and distance within the given radius range
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(min_radius, max_radius)
        
        # Convert meters to degrees
        # Latitude: 1 meter ≈ 1/111111 degrees
        delta_lat = (distance * math.sin(angle)) / 111111.0
        
        # Longitude: 1 meter ≈ 1/(111111 * cos(lat)) degrees
        delta_lon = (distance * math.cos(angle)) / (111111.0 * math.cos(math.radians(lat)))
        
        new_lat = lat + delta_lat
        new_lon = lon + delta_lon
        
        points.append((new_lat, new_lon))
    return points


def get_route_from_osrm(start, end, mode='driving'):
    """
    Fetches a realistic route from OSRM API.
    
    :param start: Tuple (lat, lon) of start location
    :param end: Tuple (lat, lon) of end location
    :param mode: Travel mode (driving, walking, cycling)
    :return: List of (lat, lon) waypoints
    """
    valid_modes = ['driving', 'walking', 'cycling']
    if mode not in valid_modes:
        logging.warning(f"⚠️ Invalid mode {mode}, defaulting to driving")
        mode = 'driving'

    base_url = f"https://router.project-osrm.org/route/v1/{mode}/"
    url = f"{base_url}{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ OSRM API Error: {str(e)}")
        return []

    route_data = response.json()
    
    # Error handling for OSRM response
    if not route_data.get('routes'):
        logging.error("❌ No route found - check locations are valid and reachable")
        return []
    if 'geometry' not in route_data['routes'][0]:
        logging.error("❌ Invalid route geometry from OSRM")
        return []

    route_geometry = route_data['routes'][0]['geometry']['coordinates']
    route_list = [(lat, lon) for lon, lat in route_geometry]  # Convert to (lat, lon)

    # Ensure endpoint is included
    if route_list[-1] != end:
        route_list.append(end)
        
    return route_list

def simulate_route(route, simulator_udid="booted", initial_delay=0.5, dwell_start_index=None):
    """
    Simulates movement with real-time controls.
    
    :param route: List of (lat, lon) waypoints
    :param simulator_udid: Simulator identifier
    :param initial_delay: Initial delay between points (seconds)
    :param dwell_start_index: Index where dwell phase starts
    """
    if not is_xcrun_available():
        return

    current_delay = initial_delay  # Mutable delay for speed control
    min_delay, max_delay = 0.1, 5.0
    paused = False
    dwell_phase_entered = False

    # Terminal setup
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setcbreak(fd)
        print("\n\033[95mControls: [P]ause [R]esume [+]SpeedUp [-]SlowDown\033[0m")

        for i, (lat, lon) in enumerate(route):
            # Check if we're entering dwell phase
            if not dwell_phase_entered and dwell_start_index is not None and i >= dwell_start_index:
                dwell_phase_entered = True
                current_delay = max_delay  # Set to minimum speed
            # Pause state machine
            while paused:
                if read_stdin() == 'r':
                    paused = False
                    print("\033[92m▶ Resumed\033[0m")
                time.sleep(0.1)

            # Execute location update
            try:
                cmd = ["xcrun", "simctl", "location", simulator_udid, "set", f"{lat},{lon}"]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                sys.stdout.write(f"\r🟢 Step {i+1}/{len(route)} → \033[92m{lat:.5f}, {lon:.5f}\033[0m")
                sys.stdout.flush()
            except subprocess.CalledProcessError as e:
                logging.error(f"\n❌ Command failed: {e.stderr.strip()}")
                return
            except Exception as e:
                logging.error(f"\n❌ Unexpected error: {str(e)}")
                return

            # Dynamic delay handling
            start_time = time.time()
            while (time.time() - start_time) < current_delay:
                key = read_stdin()
                
                if key == 'p':
                    paused = True
                    print("\n\033[93m⏸ Paused\033[0m")
                    while paused:
                        if read_stdin() == 'r':
                            paused = False
                            print("\033[92m▶ Resumed\033[0m")
                        time.sleep(0.1)
                elif key == '+':
                    new_delay = max(current_delay * 0.8, min_delay)
                    if new_delay != current_delay:
                        current_delay = new_delay
                        print(f"\n\033[95m⚡ Speed increased ({current_delay:.2f}s)\033[0m")
                elif key == '-':
                    new_delay = min(current_delay * 1.2, max_delay)
                    if new_delay != current_delay:
                        current_delay = new_delay
                        print(f"\n\033[95m🐢 Speed decreased ({current_delay:.2f}s)\033[0m")
                
                time.sleep(0.05)  # CPU throttle

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\n\033[92m✅ Simulation completed!\033[0m")

def read_stdin():
    """Non-blocking stdin read."""
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1).lower()
    return None

def validate_coords(input_str):
    """Validate and parse coordinate input."""
    try:
        lat, lon = map(float, input_str.split(','))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
        return (lat, lon)
    except:
        logging.error("❌ Invalid coordinates. Use decimal format: 37.7749,-122.4194")
        sys.exit(1)

def main():
    print("\n\033[95m🚀 GPS Location Simulator - Enhanced Edition\033[0m")

    # User input with validation
    start = validate_coords(get_input("🌍 Enter START (lat,lon)"))
    end = validate_coords(get_input("🎯 Enter DESTINATION (lat,lon)"))
    mode = get_input("🚴 Enter MODE (driving/walking/cycling) [driving]").lower() or 'driving'
    delay_input = get_input("⏳ Enter INITIAL DELAY (0.1-5.0) [0.5]") or "0.5"

    try:
        initial_delay = max(0.1, min(5.0, float(delay_input)))
    except ValueError:
        logging.error("❌ Invalid delay value. Using default 0.5s")
        initial_delay = 0.5

    # Route fetching
    route = get_route_from_osrm(start, end, mode)
    if not route:
        logging.error("❌ Aborting simulation due to route errors")
        return

    # Generate dwell points and track phase transition
    original_route_length = len(route)
    dwell_points = generate_dwell_points(end, num_points=10)
    route += dwell_points
    dwell_start_index = original_route_length

    simulate_route(route, initial_delay=initial_delay, dwell_start_index=dwell_start_index)

def get_input(prompt_text):
    """Styled input prompt."""
    return input(f"\033[96m{prompt_text}:\033[0m ").strip()

if __name__ == "__main__":
    main()