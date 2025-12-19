"""
GPS route simulator with real-time controls.
Simulates movement along a GPS route with pause, resume, and speed controls.
"""

import sys
import time
import termios
import tty
import select
import logging

from utils.platform import is_xcrun_available, is_adb_available, set_ios_location, set_android_location


def simulate_route(route, platform="ios", simulator_udid="booted", initial_delay=0.5, dwell_start_index=None):
    """
    Simulate movement along a GPS route with real-time controls.
    Supports both iOS simulators and Android emulators.
    
    Controls:
        - P: Pause simulation
        - R: Resume simulation
        - +: Increase speed (decrease delay)
        - -: Decrease speed (increase delay)
    
    Args:
        route (list): List of (lat, lon) waypoints
        platform (str): Platform type - 'ios' or 'android'
        simulator_udid (str): Simulator UDID for iOS (default: 'booted')
        initial_delay (float): Initial delay between points in seconds
        dwell_start_index (int): Index where dwell phase starts (slower speed)
    """
    # Validate platform availability before starting
    if platform == "ios":
        if not is_xcrun_available():
            return
    elif platform == "android":
        if not is_adb_available():
            return
    else:
        logging.error(f"Unknown platform: {platform}")
        return

    # Initialize simulation parameters
    current_delay = initial_delay
    min_delay, max_delay = 0.1, 5.0
    paused = False
    dwell_phase_entered = False

    # Setup terminal for non-blocking input
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setcbreak(fd)
        print("\nControls: [P]ause [R]esume [+]SpeedUp [-]SlowDown")

        # Iterate through each waypoint in the route
        for i, (lat, lon) in enumerate(route):
            # Check if entering dwell phase (simulating arrival at destination)
            if not dwell_phase_entered and dwell_start_index is not None and i >= dwell_start_index:
                dwell_phase_entered = True
                current_delay = max_delay  # Slow down at destination
            
            # Handle pause state
            while paused:
                if read_stdin() == 'r':
                    paused = False
                    print("Resumed")
                time.sleep(0.1)

            # Execute location update based on platform
            success = False
            if platform == "ios":
                success = set_ios_location(lat, lon, simulator_udid)
            elif platform == "android":
                success = set_android_location(lat, lon)
            
            # Display progress
            if success:
                sys.stdout.write(f"\rStep {i+1}/{len(route)} -> {lat:.5f}, {lon:.5f}")
                sys.stdout.flush()
            else:
                # Exit if location update failed
                return

            # Handle delay with real-time control checks
            start_time = time.time()
            while (time.time() - start_time) < current_delay:
                key = read_stdin()
                
                if key == 'p':
                    # Pause simulation
                    paused = True
                    print("\nPaused")
                    while paused:
                        if read_stdin() == 'r':
                            paused = False
                            print("Resumed")
                        time.sleep(0.1)
                
                elif key == '+':
                    # Increase speed (decrease delay)
                    new_delay = max(current_delay * 0.8, min_delay)
                    if new_delay != current_delay:
                        current_delay = new_delay
                        print(f"\nSpeed increased (delay: {current_delay:.2f}s)")
                
                elif key == '-':
                    # Decrease speed (increase delay)
                    new_delay = min(current_delay * 1.2, max_delay)
                    if new_delay != current_delay:
                        current_delay = new_delay
                        print(f"\nSpeed decreased (delay: {current_delay:.2f}s)")
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.05)

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nSimulation completed!")


def read_stdin():
    """
    Perform non-blocking read from stdin.
    
    Returns:
        str: Lowercase character if available, None otherwise
    """
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1).lower()
    return None
