"""
Platform-specific utilities for iOS and Android simulators/emulators.
Handles device detection and location setting operations.
"""

import subprocess
import logging
import shutil


def is_xcrun_available():
    """
    Check if xcrun command is available on the system.
    
    Returns:
        bool: True if xcrun is installed, False otherwise
    """
    if shutil.which("xcrun") is None:
        logging.error("'xcrun' command not found. Install Xcode Command Line Tools.")
        return False
    return True


def is_adb_available():
    """
    Check if adb (Android Debug Bridge) is available on the system.
    
    Returns:
        bool: True if adb is installed, False otherwise
    """
    if shutil.which("adb") is None:
        logging.error("'adb' command not found. Install Android SDK Platform Tools.")
        return False
    return True


def list_ios_simulators():
    """
    List all currently booted iOS simulators.
    
    Returns:
        str: Output of simctl list command, or None if command fails
    """
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def list_android_emulators():
    """
    List all connected Android devices and emulators.
    
    Returns:
        str: Output of adb devices command, or None if command fails
    """
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def set_android_location(lat, lon):
    """
    Set GPS location on Android emulator using adb geo fix command.
    Note: adb geo fix expects longitude first, then latitude.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    
    Returns:
        bool: True if location was set successfully, False otherwise
    """
    try:
        cmd = ["adb", "emu", "geo", "fix", str(lon), str(lat)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"ADB command failed: {e.stderr.strip()}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return False


def set_ios_location(lat, lon, simulator_udid="booted"):
    """
    Set GPS location on iOS simulator using xcrun simctl.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        simulator_udid (str): Simulator UDID or 'booted' for currently running simulator
    
    Returns:
        bool: True if location was set successfully, False otherwise
    """
    try:
        cmd = ["xcrun", "simctl", "location", simulator_udid, "set", f"{lat},{lon}"]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e.stderr.strip()}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return False
