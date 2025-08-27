#!/bin/bash
# Development environment setup

echo "🚀 Setting up development environment..."

# Check Python version
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create necessary directories
mkdir -p logs
mkdir -p plugins/{screens,data_sources}
mkdir -p tests/fixtures

# Copy example config
if [ ! -f config/user.yaml ]; then
    cp config/development.yaml config/user.yaml
    echo "📝 Created config/user.yaml - please update with your settings"
fi

# Run tests
echo "🧪 Running tests..."
pytest tests/

echo "✅ Development setup complete!"
echo "Run with: python main.py --env development"