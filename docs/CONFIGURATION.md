## Configuration

### ServiceNow Setup

1. **Create Integration User**
   ```
   In ServiceNow:
   1. Go to User Administration > Users
   2. Create new user (e.g., 'dashboard_user')
   3. Assign roles: itil, rest_service
   4. Set password
   ```

2. **Test API Access**
   ```bash
   # Test connection manually
   curl -u dashboard.user:Welkom123! https://dev265074.service-now.com/api/now/table/incident?sysparm_limit=1
   ```

### Dashboard Configuration

1. **Copy and Edit Config**
   ```bash
   cp examples/config_example.yaml config.yaml
   nano config.yaml
   ```

2. **Essential Settings**
   ```yaml
   servicenow:
     instance_url: "https://yourinstance.service-now.com"
     username: "dashboard_user"
     password: "your_password"
   
   matrix:
     led_rows: 32
     led_cols: 64
     hardware_mapping: 'adafruit-hat-pwm'  # or 'adafruit-hat'
     gpio_slowdown: 1  # Adjust for your Pi model
   ```

3. **Hardware-Specific Adjustments**

   **For Pi Zero 2W/3B:**
   ```yaml
   matrix:
     gpio_slowdown: 2  # or 3 if flickering
   ```

   **If NO GPIO4-GPIO18 jumper:**
   ```yaml
   matrix:
     hardware_mapping: 'adafruit-hat'  # Remove '-pwm'
   ```

### Testing Installation

```bash
# Activate environment
source venv/bin/activate

# Test ServiceNow API
python examples/test_api.py

# Test display (simulation mode if no hardware)
python display_renderer.py

# Run dashboard
python servicenow_dashboard.py
```

### Auto-Start Setup

1. **Make startup script executable**
   ```bash
   chmod +x start-dashboard.sh
   ```

2. **Add to crontab**
   ```bash
   sudo crontab -e
   # Add this line:
   @reboot /home/pi/servicenow-led-dashboard/start-dashboard.sh > /home/pi/cron.log 2>&1
   ```

3. **Test auto-start**
   ```bash
   sudo reboot
   # Dashboard should start automatically after boot
   ```

## Troubleshooting

### Common Issues

**"Permission denied" errors**
```bash
# Make sure scripts are executable
chmod +x start-dashboard.sh install.sh

# Check file ownership
sudo chown -R pi:pi /home/pi/servicenow-led-dashboard/
```

**Display flickering**
```yaml
# In config.yaml, try increasing gpio_slowdown:
matrix:
  gpio_slowdown: 2  # Try 2, 3, or 4
```

**"Module not found" errors**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

**ServiceNow connection fails**
```bash
# Test manually
curl -u "user:pass" "https://instance.service-now.com/api/now/table/incident?sysparm_limit=1"

# Check config.yaml for typos
# Verify user has correct roles in ServiceNow
```

**LED Matrix not detected**
```bash
# Check connections
# Try different hardware_mapping values:
# - 'adafruit-hat'
# - 'adafruit-hat-pwm'  
# - 'regular'

# Check power supply (needs 5V 4A+)
```

### Debug Mode

```bash
# Run with debug logging
python servicenow_dashboard.py --debug

# Check logs
tail -f servicenow_dashboard.log

# Test individual components
python servicenow_api.py      # Test API only
python display_renderer.py    # Test display only
```

### Performance Tuning

**Optimize refresh rates:**
```yaml
servicenow:
  refresh_intervals:
    incidents: 30        # Faster updates for critical data
    service_requests: 120  # Slower for less critical
    system_health: 300   # Slowest for stable metrics
```

**Adjust display settings:**
```yaml
matrix:
  led_brightness: 40     # Lower for power savings
  led_limit_refresh: 60  # Lower for Pi Zero/3B
```

## Customization

### Adding Custom Screens

1. **Define in config.yaml:**
   ```yaml
   display:
     screens:
       - "incident_summary"
       - "my_custom_screen"
   ```

2. **Add render method in display_renderer.py:**
   ```python
   def render_my_custom_screen(self, data: Dict[str, Any]):
       # Your custom rendering logic
       pass
   ```

### Adding Custom Metrics

1. **Define in config.yaml:**
   ```yaml
   custom_metrics:
     my_metric:
       table: "incident"
       query: "priority=1^state!=6"
       display_name: "Critical Open"
   ```

2. **Update servicenow_api.py to fetch the metric**

### Changing Colors/Fonts

```yaml
display:
  colors:
    priority_1: [255, 0, 0]     # Bright red
    priority_2: [255, 100, 0]   # Orange-red
    
  fonts:
    small: "4x6.bdf"
    medium: "6x9.bdf"  # Different font
```

## Maintenance

### Log Rotation
```bash
# Logs are automatically rotated, but you can manually clean:
sudo logrotate -f /etc/logrotate.conf
```

### Updates
```bash
cd servicenow-led-dashboard
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo reboot
```

### Monitoring
```bash
# Check if dashboard is running
ps aux | grep servicenow_dashboard

# Check system resources
htop

# Check logs
tail -f servicenow_dashboard.log
```

## Security Considerations

1. **Use dedicated ServiceNow user** with minimal required permissions
2. **Secure config.yaml** with proper file permissions:
   ```bash
   chmod 600 config.yaml
   ```
3. **Use HTTPS** for ServiceNow connections (verify_ssl: true)
4. **Regular updates** of system packages and Python dependencies
5. **Network isolation** - consider dedicated VLAN for dashboard