# ServiceNow LED Dashboard - Installation Guide

## Hardware Setup

### Required Hardware
- **Raspberry Pi**: Zero 2W, 3B, 4, or 5 (recommended: Pi 4 or 5)
- **LED Matrix**: 32x64 HUB75 RGB LED Matrix Panel
- **Matrix Driver**: Adafruit RGB Matrix Bonnet or HAT + RTC
- **Power Supply**: 5V 4A minimum (8A recommended for stability)
- **MicroSD Card**: 32GB+ Class 10
- **Optional**: Short jumper wire for GPIO4-GPIO18 connection

### Hardware Assembly

1. **Flash Raspberry Pi OS**
   ```bash
   # Use Raspberry Pi Imager to flash Pi OS Lite
   # During setup:
   # - Enable SSH
   # - Set WiFi credentials  
   # - Set password for 'pi' user
   # - Set your timezone
   ```

2. **Hardware Assembly**
   - Connect RGB Matrix to Bonnet/HAT following Adafruit's guide
   - **Optional but recommended**: Solder jumper wire between GPIO4 and GPIO18
   - Connect power supply to matrix (NOT to Pi)
   - Insert SD card and power on Pi

3. **Initial Pi Configuration**
   ```bash
   # SSH into your Pi
   ssh pi@raspberrypi.local
   
   # Update system
   sudo apt-get update -y
   sudo apt-get upgrade -y
   
   # Disable audio (if you did GPIO4-GPIO18 mod)
   sudo nano /etc/modprobe.d/alsa-blacklist.conf
   # Add: blacklist snd_bcm2835
   
   sudo nano /boot/firmware/config.txt
   # Change: dtparam=audio=off
   
   # Disable WiFi power saving
   sudo nano /etc/rc.local
   # Add before "exit 0": /sbin/iw wlan0 set power_save off
   
   # Reboot
   sudo reboot
   ```

## Software Installation

### Automated Installation
```bash
# Clone repository
git clone --recursive https://github.com/le-burger/servicenow-led-dashboard.git
cd servicenow-led-dashboard

# Run installation script
sudo ./install.sh

# The installer will:
# - Install system dependencies
# - Clone RGB matrix library
# - Create Python virtual environment
# - Install Python packages
# - Build LED matrix library
# - Create default configuration
```

### Manual Installation
If the automated installer fails:

```bash
# Install dependencies
sudo apt-get install -y git python3-dev python3-pip python3-venv build-essential

# Clone RGB matrix library
mkdir -p submodules
cd submodules
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd ..

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Build LED matrix library
cd submodules/rpi-rgb-led-matrix
make build-python PYTHON=$(which python)
sudo make install-python PYTHON=$(which python)
cd ../..
```

