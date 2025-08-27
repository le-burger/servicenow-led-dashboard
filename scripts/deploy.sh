#!/bin/bash
# Deploy to Raspberry Pi

set -e

# Configuration
PI_HOST="${1:-raspberrypi.local}"
PI_USER="${2:-pi}"
DEPLOY_PATH="/home/${PI_USER}/servicenow-dashboard"

echo "🚀 Deploying to ${PI_USER}@${PI_HOST}:${DEPLOY_PATH}"

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf deploy.tar.gz \
    src/ \
    config/base.yaml \
    config/production.yaml \
    main.py \
    requirements.txt \
    requirements-pi.txt \
    scripts/install_pi.sh

# Copy to Pi
echo "📤 Copying to Raspberry Pi..."
scp deploy.tar.gz ${PI_USER}@${PI_HOST}:/tmp/

# Install on Pi
echo "🔧 Installing on Raspberry Pi..."
ssh ${PI_USER}@${PI_HOST} << 'ENDSSH'
    # Create directory
    mkdir -p ${DEPLOY_PATH}
    cd ${DEPLOY_PATH}

    # Extract files
    tar -xzf /tmp/deploy.tar.gz

    # Run installation
    bash scripts/install_pi.sh

    # Setup systemd service
    sudo cp scripts/servicenow-dashboard.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable servicenow-dashboard
    sudo systemctl start servicenow-dashboard
ENDSSH

# Cleanup
rm deploy.tar.gz

echo "✅ Deployment complete!"
echo "View logs: ssh ${PI_USER}@${PI_HOST} 'journalctl -u servicenow-dashboard -f'"