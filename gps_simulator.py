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

# Configure logging with colors and better formatting
logging.basicConfig(
    format="\033[94m%(asctime)s\033[0m - \033[92m%(levelname)s\033[0m - %(message)s",
    level=logging.INFO,
)

def is_xcrun_available():
    """Check if xcrun is available on the system."""
    return shutil.which("xcrun") is not None

def get_route_from_osrm(start, end):
    """
    Fetches a realistic driving route from OSRM API.

    :param start: Tuple (lat, lon) of the starting location
    :param end: Tuple (lat, lon) of the ending location
    :return: List of (lat, lon) waypoints along the route
    """
    base_url = "https://router.project-osrm.org/route/v1/driving/"
    url = f"{base_url}{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"

    print("⏳ Fetching route from OSRM...")
    response = requests.get(url)
    
    if response.status_code == 200:
        route_data = response.json()
        route_geometry = route_data["routes"][0]["geometry"]["coordinates"]
        route_list = [(lat, lon) for lon, lat in route_geometry]  # Convert to (lat, lon)

        # ✅ Append exact end location as the final step
        if route_list[-1] != end:
            route_list.append(end)
        return route_list
    else:
        logging.error(f"❌ Failed to fetch route from OSRM: {response.text}")
        return []

def simulate_route(route, simulator_udid="booted", delay=0.5):
    """
    Simulates movement along a realistic route with pause/resume functionality.

    :param route: List of (lat, lon) waypoints
    :param simulator_udid: Identifier of the simulator
    :param delay: Time delay between location updates
    """
    if not is_xcrun_available():
        logging.error("❌ 'xcrun' command is not available. Ensure Xcode Command Line Tools are installed.")
        return

    print("🌍 Moving through route...")

    # Save original terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)  # Enter raw mode to read single key presses
        print("\n\033[95mPress 'p' to pause, 'r' to resume...\033[0m")

        paused = False

        for i, (lat, lon) in enumerate(route):
            # Check if paused before processing waypoint
            while paused:
                # Check for resume key
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    if key == 'r':
                        paused = False
                        print("\n\033[92m▶ Simulation resumed.\033[0m")
                time.sleep(0.1)

            # Send location command
            try:
                command = ["xcrun", "simctl", "location", simulator_udid, "set", f"{lat},{lon}"]
                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode == 0:
                    sys.stdout.write(f"\r🟢 Step {i+1}/{len(route)} → Moved to \033[92m({lat}, {lon})\033[0m ✅")
                    sys.stdout.flush()
                else:
                    logging.error(f"\n❌ Step {i+1}/{len(route)}: Failed to set location. Error: {result.stderr.strip()}")

            except Exception as e:
                logging.exception(f"\n❌ Exception occurred at step {i+1}/{len(route)}: {e}")

            # Handle delay with pause checks
            start_time = time.time()
            while (time.time() - start_time) < delay:
                # Check for pause key
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    if key == 'p' or key == 'P':
                        paused = True
                        print("\n\033[93m⏸ Simulation paused. Press 'r' to resume...\033[0m")
                        while paused:
                            if select.select([sys.stdin], [], [], 0)[0]:
                                key_resume = sys.stdin.read(1)
                                if key_resume == 'r' or key_resume == 'R':
                                    paused = False
                                    print("\033[92m▶ Simulation resumed.\033[0m")
                                    # Adjust remaining delay
                                    remaining = delay - (time.time() - start_time)
                                    if remaining > 0:
                                        time.sleep(remaining)
                                    break
                            time.sleep(0.1)
                # Sleep a small interval to prevent high CPU usage
                time.sleep(0.05)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\033[0m")  # Reset any text formatting

    print("🎉 \033[92mLocation simulation completed!\033[0m 🚀\n")

def get_input(prompt_text):
    """Helper function to get user input with styling"""
    return input(f"\033[96m{prompt_text}:\033[0m ").strip()

def main():
    print("\n\033[95m🚗 GPS Location Simulation - OSRM Based Routing\033[0m")

    # Ask for Start Location (comma-separated)
    start_input = get_input("🔹 Enter Start Location (lat, lon)")
    start_lat, start_lon = map(float, start_input.split(","))

    # Ask for Destination Location (comma-separated)
    end_input = get_input("🔹 Enter Destination Location (lat, lon)")
    end_lat, end_lon = map(float, end_input.split(","))

    # Ask for delay
    delay_input = get_input("⏳ Enter Delay Between Movements (default: 0.5 sec)")
    delay = float(delay_input) if delay_input else 0.5

    start_location = (start_lat, start_lon)
    end_location = (end_lat, end_lon)

    # Fetch Route
    route = get_route_from_osrm(start_location, end_location)

    if route:
        # Simulate Route
        simulate_route(route, delay=delay)
    else:
        logging.error("\n❌ No route data available. Simulation aborted.")

if __name__ == "__main__":
    main()