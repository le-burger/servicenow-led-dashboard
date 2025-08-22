#!/bin/bash
# ServiceNow Dashboard Startup Script

cd /home/pi/servicenow-led-dashboard
source venv/bin/activate

# Optional: Auto-update on start (uncomment if desired)
# git pull origin main
# pip install -r requirements.txt

# Retry logic in case of temporary failures
n=0
until [ $n -ge 10 ]
do
    sudo /home/pi/servicenow-led-dashboard/venv/bin/python servicenow_dashboard.py && break
    n=$[$n+1]
    echo "Dashboard failed, retrying in 10 seconds... (attempt $n)"
    sleep 10
done