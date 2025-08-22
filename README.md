# ServiceNow LED Dashboard

Display live ServiceNow performance metrics on an LED matrix driven by a Raspberry Pi. Shows incident counts, service request status, system health metrics, and more on a real-time dashboard.

## Features
- Real-time ServiceNow incident tracking by priority
- Service request status monitoring  
- System health display
- Assignment group workload visualization
- Customizable display screens and colors
- Auto-refresh with configurable intervals

## Hardware Requirements
- Raspberry Pi (Zero 2W, 3, 4, or 5)
- Adafruit RGB Matrix Bonnet or HAT
- 32x64 HUB75 RGB LED Matrix
- 5V 4A+ Power Supply

## Quick Start
1. Flash Raspberry Pi OS Lite to SD card
2. Clone this repository: `git clone https://github.com/yourusername/servicenow-led-dashboard.git`
3. Run installation: `cd servicenow-led-dashboard && sudo ./install.sh`
4. Configure ServiceNow connection in `config.yaml`
5. Test: `python servicenow_dashboard.py`
6. Enable auto-start: Follow installation guide

## Configuration
Edit `config.yaml` to set:
- ServiceNow instance URL and credentials
- Display preferences and colors
- Hardware settings for your LED matrix
- Custom metrics and thresholds

See [CONFIGURATION.md](docs/CONFIGURATION.md) for detailed setup.

## Based On
This project is inspired by [rpi-led-nhl-scoreboard](https://github.com/gidger/rpi-led-nhl-scoreboard) and uses the same LED matrix control libraries.