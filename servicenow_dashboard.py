#!/usr/bin/env python3
"""
ServiceNow LED Dashboard - Main Application
Based on the NHL scoreboard architecture
"""

import time
import sys
import os
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import signal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from servicenow_api import ServiceNowAPI
from display_renderer import DisplayRenderer


class ServiceNowDashboard:
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the ServiceNow dashboard"""
        self.config = self.load_config(config_path)
        self.setup_logging()

        self.logger = logging.getLogger(__name__)
        self.running = True

        # Initialize API client
        self.api = ServiceNowAPI(**self.config['servicenow'])

        # Initialize display renderer
        self.renderer = DisplayRenderer(self.config)

        # Data cache
        self.dashboard_data = {}
        self.last_update = {}

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"❌ Configuration file {config_path} not found")
            print("Copy examples/config_example.yaml to config.yaml and customize it")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing configuration file: {e}")
            sys.exit(1)

    def setup_logging(self):
        """Setup logging based on configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    log_config.get('file', 'servicenow_dashboard.log')
                )
            ]
        )

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def should_update_data(self, data_type: str) -> bool:
        """Check if data should be updated based on refresh intervals"""
        if data_type not in self.last_update:
            return True

        intervals = self.config['servicenow'].get('refresh_intervals', {})
        interval = intervals.get(data_type, 60)  # Default 60 seconds

        time_since_update = time.time() - self.last_update[data_type]
        return time_since_update >= interval

    def update_dashboard_data(self):
        """Update dashboard data from ServiceNow API"""
        try:
            # Check if we need to update data
            if not self.should_update_data('incidents'):
                return

            self.logger.info("Fetching fresh data from ServiceNow...")

            # Get fresh data from API
            new_data = self.api.get_dashboard_data()

            if new_data.get('status') == 'success':
                self.dashboard_data = new_data
                self.last_update['incidents'] = time.time()

                # Log summary
                incidents = new_data['incidents']
                self.logger.info(
                    f"Data updated - Incidents: {incidents['total_incidents']}, "
                    f"Critical: {new_data['kpis']['critical_open']}, "
                    f"Open: {incidents['open_incidents']}"
                )

                # Check for alerts
                self.check_alerts(new_data)

            else:
                self.logger.warning("Failed to fetch data from ServiceNow API")

        except Exception as e:
            self.logger.error(f"Error updating dashboard data: {e}")

    def check_alerts(self, data: Dict[str, Any]):
        """Check for alert conditions and notify renderer"""
        behavior = self.config.get('behavior', {})
        thresholds = behavior.get('thresholds', {})

        alerts = []

        # Check critical incident threshold
        critical_threshold = thresholds.get('critical_incidents', 5)
        critical_count = data['kpis']['critical_open']
        if critical_count >= critical_threshold:
            alerts.append({
                'type': 'critical_incidents',
                'message': f'{critical_count} critical incidents!',
                'level': 'critical'
            })

        # Check system health threshold
        health_threshold = thresholds.get('system_health_warning', 90)
        health_pct = data['kpis']['health_percentage']
        if health_pct < health_threshold:
            alerts.append({
                'type': 'system_health',
                'message': f'System health: {health_pct}%',
                'level': 'warning'
            })

        # Send alerts to renderer
        if alerts:
            self.renderer.set_alerts(alerts)
            self.logger.warning(f"Alerts triggered: {[a['message'] for a in alerts]}")
        else:
            self.renderer.clear_alerts()

    def run_main_loop(self):
        """Main dashboard loop - similar to NHL scoreboard main loop"""
        self.logger.info("🚀 Starting ServiceNow LED Dashboard")

        # Initial API connection test
        if not self.api.test_connection():
            self.logger.error("❌ Cannot connect to ServiceNow API")
            return

        self.logger.info("✅ ServiceNow API connection successful")

        # Get initial data
        self.update_dashboard_data()

        if not self.dashboard_data:
            self.logger.error("❌ No initial data available")
            return

        # Start display
        self.renderer.start_display()

        # Main loop
        display_config = self.config.get('display', {})
        screen_rotation_time = display_config.get('screen_rotation_time', 10)
        last_screen_change = time.time()
        current_screen_index = 0
        screens = display_config.get('screens', ['incident_summary'])

        try:
            while self.running:
                # Update data periodically
                self.update_dashboard_data()

                # Rotate screens
                now = time.time()
                if now - last_screen_change >= screen_rotation_time:
                    current_screen_index = (current_screen_index + 1) % len(screens)
                    last_screen_change = now

                current_screen = screens[current_screen_index]

                # Render current screen
                if self.dashboard_data:
                    self.renderer.render_screen(current_screen, self.dashboard_data)

                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.logger.info("Dashboard stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up...")
        self.renderer.cleanup()
        self.logger.info("ServiceNow LED Dashboard stopped")


def main():
    """Main entry point"""
    # Check command line arguments
    config_file = 'config.yaml'
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    try:
        # Create and run dashboard
        dashboard = ServiceNowDashboard(config_file)
        dashboard.run_main_loop()

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()