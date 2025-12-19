"""
Command-line interface for GPS location simulator.
Main entry point for the application.
"""

import sys
import logging

from utils.platform import is_xcrun_available, is_adb_available
from utils.geo import get_route_from_osrm, get_location_name, validate_coords, generate_dwell_points
from utils.csv_reader import read_route_from_csv
from simulator import simulate_route


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def get_input(prompt_text):
    """
    Get user input with a formatted prompt.
    
    Args:
        prompt_text (str): Text to display as prompt
    
    Returns:
        str: User input string (stripped)
    """
    return input(f"{prompt_text}: ").strip()


def main():
    """
    Main function to run the GPS location simulator.
    Handles user input and coordinates the simulation.
    """
    try:
        print("\n=== GPS Location Simulator ===")

        # Step 1: Platform selection
        platform_input = get_input("Enter PLATFORM (ios/android) [ios]").lower() or 'ios'
        if platform_input not in ['ios', 'android']:
            logging.error("Invalid platform. Choose 'ios' or 'android'")
            return
        
        # Check if platform tools are available
        if platform_input == 'ios':
            if not is_xcrun_available():
                return
        elif platform_input == 'android':
            if not is_adb_available():
                return

        # Step 2: Input mode selection (CSV or manual)
        use_csv = get_input("Use CSV file? (yes/no) [no]").lower() in ['yes', 'y']
        
        route = None
        start = None
        end = None
        
        if use_csv:
            # CSV mode - read coordinates from file
            # Default to sample_route.csv in data folder
            default_csv = "data/sample_route.csv"
            csv_path = get_input(f"Enter CSV file path [{default_csv}]") or default_csv
            route = read_route_from_csv(csv_path)
            
            if not route:
                logging.error("Aborting simulation due to CSV errors")
                return
            
            # Get start and end points from route
            start = route[0]
            end = route[-1]
            
            print(f"Route loaded with {len(route)} waypoints")
            print(f"Trip: {start[0]:.5f},{start[1]:.5f} -> {end[0]:.5f},{end[1]:.5f}")
        
        else:
            # Manual mode - get coordinates and fetch route from OSRM
            start_coords = get_input("Enter START (lat,lon)")
            start = validate_coords(start_coords)
            
            end_coords = get_input("Enter DESTINATION (lat,lon)")
            end = validate_coords(end_coords)
            
            mode = get_input("Enter MODE (driving/walking/cycling) [driving]").lower() or 'driving'
            
            # Fetch route from OSRM API
            print("Fetching route...")
            route = get_route_from_osrm(start, end, mode)
            
            if not route:
                logging.error("Aborting simulation due to route errors")
                return

            # Get human-readable location names
            start_location = get_location_name(start[0], start[1])
            end_location = get_location_name(end[0], end[1])

            print(f"Route found with {len(route)} waypoints")
            print(f"Trip: {start_location} -> {end_location}")
        
        # Step 3: Get simulation speed (delay between points)
        delay_input = get_input("Enter INITIAL DELAY (0.1-5.0) [0.5]") or "0.5"
        
        try:
            initial_delay = max(0.1, min(5.0, float(delay_input)))
        except ValueError:
            logging.error("Invalid delay value. Using default 0.5s")
            initial_delay = 0.5

        # Step 4: Generate dwell points at destination
        # These simulate small GPS movements when stationary
        original_route_length = len(route)
        dwell_points = generate_dwell_points(end, num_points=10)
        route += dwell_points
        dwell_start_index = original_route_length

        # Step 5: Start simulation
        simulate_route(
            route,
            platform=platform_input,
            initial_delay=initial_delay,
            dwell_start_index=dwell_start_index
        )
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
