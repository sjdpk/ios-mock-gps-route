# GPS Location Simulator with OSRM Routing

This project allows you to simulate a realistic GPS location journey by fetching a driving route from the [OSRM API](https://project-osrm.org/) and simulating movement on an iOS simulator.

## Features:

- Fetches a driving route between two locations using OSRM's API.
- Simulates GPS location updates along the route on an iOS simulator.
- Customizable delay between movements to mimic real-world driving speed.
- Pause/Resume functionality to GPS location simulation
- Enhance GPS simulator with route validation, travel modes, and improved controls

## Requirements:

- Python 3.x
- Xcode Command Line Tools (for `xcrun` utility)
- Internet connection to fetch routes from OSRM API

## Installation Steps:

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/sjdpk/ios-mock-gps-route.git
cd ios-mock-gps-route/
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install requests
```

### 4. Ensure Xcode Command Line Tools Are Installed

The script requires `xcrun` (Xcode command-line tools) for simulating GPS locations. You can install it by running:

```bash
xcode-select --install
```

### 5. Run the Script

To run the GPS location simulator:

```bash
python3 gps_simulator.py
```

### 6. Follow the Prompts

The script will prompt you to enter the start and destination GPS coordinates (latitude, longitude), as well as a delay between location updates. After entering these details, it will fetch the route from OSRM and simulate the movement on your simulator.

## Example Usage:

1. **Start Location**:  
   Enter the starting latitude and longitude, e.g., `37.7749,-122.4194` (San Francisco).

2. **Destination Location**:  
   Enter the destination latitude and longitude, e.g., `34.0522,-118.2437` (Los Angeles).

3. **Delay**:  
   Enter a delay in seconds between movements (e.g., `0.5`). Leave blank to use the default value of `0.5`.
