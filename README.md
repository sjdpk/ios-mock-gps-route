# GPS Location Simulator

A comprehensive GPS location simulator for iOS simulators and Android emulators. Simulate realistic GPS routes with real-time controls for speed, pause, and resume.

## Features

- **Multi-Platform Support**: Works with both iOS simulators and Android emulators
- **Route Sources**:
  - Manual input with OSRM routing (OpenStreetMap)
  - CSV file input for custom routes
- **Real-Time Controls**:
  - Pause/Resume simulation
  - Adjust speed on the fly
- **Realistic Simulation**: 
  - Dwell points at destination to simulate GPS drift
  - Configurable delay between waypoints

## Project Structure

```
ios-mock-gps-route/
├── data/                   # Sample data files
│   └── sample_route.csv    # Sample GPS route
├── src/                    # Source code
│   ├── cli.py              # Main entry point and CLI
│   ├── simulator.py        # Core simulation logic
│   └── utils/              # Utility modules
│       ├── __init__.py
│       ├── platform.py     # Platform-specific operations
│       ├── geo.py          # Geographic and routing utilities
│       └── csv_reader.py   # CSV file reading
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Requirements

### General
- Python 3.7+
- Required Python packages (install via `pip install -r requirements.txt`)

### Platform-Specific

**For iOS:**
- macOS with Xcode Command Line Tools
- `xcrun` command available
- iOS Simulator running

**For Android:**
- Android SDK Platform Tools
- `adb` command available
- Android Emulator running

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ios-mock-gps-route
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure platform tools are installed:
   - **iOS**: `xcode-select --install`
   - **Android**: Install Android SDK Platform Tools

## Usage

### Basic Usage

Run the simulator:
```bash
python src/cli.py
```

Follow the interactive prompts:
1. Select platform (ios/android)
2. Choose input method (manual or CSV)
3. Configure simulation parameters

### CSV File Format

Create a CSV file with GPS coordinates:
```csv
lat,lon
37.7749,-122.4194
37.7755,-122.4190
37.7760,-122.4185
37.7765,-122.4180
```

Sample file available at `data/sample_route.csv`

### Simulation Controls

During simulation:
- **P**: Pause simulation
- **R**: Resume simulation
- **+**: Increase speed (decrease delay)
- **-**: Decrease speed (increase delay)
- **Ctrl+C**: Stop simulation

## Example

```bash
$ python src/cli.py

=== GPS Location Simulator ===
Enter PLATFORM (ios/android) [ios]: ios
Use CSV file? (yes/no) [no]: yes
Enter CSV file path: data/sample_route.csv
Route loaded with 4 waypoints
Trip: 37.77490,-122.41940 -> 37.77650,-122.41800
Enter INITIAL DELAY (0.1-5.0) [0.5]: 0.5

Controls: [P]ause [R]esume [+]SpeedUp [-]SlowDown
Step 1/14 -> 37.77490, -122.41940
```

## API Reference

### Core Modules

- **cli.py**: Command-line interface and main entry point
- **simulator.py**: Route simulation engine with real-time controls
- **utils/platform.py**: iOS and Android device operations
- **utils/geo.py**: Geographic calculations and OSRM routing
- **utils/csv_reader.py**: CSV file parsing and validation

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. with OSRM Routing

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
