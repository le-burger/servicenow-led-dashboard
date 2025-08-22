#!/bin/bash
# ServiceNow LED Dashboard Installation Script

set -e

echo "🚀 Installing ServiceNow LED Dashboard..."

# Check if running as root for some commands
if [[ $EUID -eq 0 ]]; then
   echo "Please run this script as a regular user (not root)"
   echo "The script will prompt for sudo when needed"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install required system packages
echo "📦 Installing system dependencies..."
sudo apt-get install -y git python3-dev python3-pip python3-venv build-essential

# Clone RGB LED matrix library if not exists
if [ ! -d "submodules" ]; then
    echo "📦 Cloning RGB LED matrix library..."
    mkdir -p submodules
    cd submodules
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    cd ..
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Build and install LED matrix library
echo "🔨 Building LED matrix library..."
cd submodules/rpi-rgb-led-matrix
make build-python PYTHON=$(which python)
sudo make install-python PYTHON=$(which python)
cd ../..

# Copy example config if config doesn't exist
if [ ! -f "config.yaml" ]; then
    echo "📝 Creating default configuration..."
    cp examples/config_example.yaml config.yaml
    echo "⚠️  Please edit config.yaml with your ServiceNow details"
fi

# Make scripts executable
chmod +x start-dashboard.sh

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your ServiceNow instance details"
echo "2. Test the connection: python examples/test_api.py"
echo "3. Run the dashboard: ./start-dashboard.sh"
echo "4. Set up auto-start with: sudo crontab -e"
echo "   Add: @reboot /home/pi/servicenow-led-dashboard/start-dashboard.sh"