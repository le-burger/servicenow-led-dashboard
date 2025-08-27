#!/bin/bash
# Install on Raspberry Pi

set -e

echo "🔧 Installing ServiceNow Dashboard on Raspberry Pi..."

# Update system
sudo apt-get update -y

# Install system dependencies
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    build-essential

# Install RGB Matrix library if not present
if [ ! -d "lib/rpi-rgb-led-matrix" ]; then
    echo "📦 Installing RGB LED Matrix library..."
    mkdir -p lib
    cd lib
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    cd rpi-rgb-led-matrix
    make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)
    cd ../..
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-pi.txt

# Set permissions
chmod +x main.py

echo "✅ Installation complete!"