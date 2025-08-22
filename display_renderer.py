#!/usr/bin/env python3
"""
Display Renderer for ServiceNow LED Dashboard
Handles all LED matrix rendering logic
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

# Try to import RGB matrix library
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

    LED_MATRIX_AVAILABLE = True
except ImportError:
    LED_MATRIX_AVAILABLE = False
    print("⚠️  RGB Matrix library not available - running in simulation mode")


class DisplayRenderer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize display renderer"""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Matrix configuration
        self.matrix_config = config.get('matrix', {})
        self.display_config = config.get('display', {})

        # Initialize matrix
        self.matrix = None
        self.canvas = None
        self.font = None
        self.font_small = None
        self.font_large = None

        # Alert state
        self.alerts = []
        self.alert_flash_state = False
        self.last_alert_flash = time.time()

        # Colors
        self.colors = self.display_config.get('colors', {})

        self.setup_matrix()
        self.setup_fonts()

    def setup_matrix(self):
        """Setup RGB LED matrix"""
        if not LED_MATRIX_AVAILABLE:
            self.logger.warning("LED Matrix library not available - display simulation only")
            return

        options = RGBMatrixOptions()
        options.rows = self.matrix_config.get('led_rows', 32)
        options.cols = self.matrix_config.get('led_cols', 64)
        options.chain_length = self.matrix_config.get('led_chain', 1)
        options.parallel = self.matrix_config.get('led_parallel', 1)
        options.brightness = self.matrix_config.get('led_brightness', 60)
        options.limit_refresh_rate_hz = self.matrix_config.get('led_limit_refresh', 120)
        options.hardware_mapping = self.matrix_config.get('hardware_mapping', 'adafruit-hat')
        options.gpio_slowdown = self.matrix_config.get('gpio_slowdown', 1)

        # PWM options
        options.pwm_bits = self.matrix_config.get('led_pwm_bits', 11)
        options.pwm_lsb_nanoseconds = self.matrix_config.get('led_pwm_lsb_nanoseconds', 130)
        options.pwm_dither_bits = self.matrix_config.get('led_pwm_dither_bits', 0)

        try:
            self.matrix = RGBMatrix(options=options)
            self.canvas = self.matrix.CreateFrameCanvas()
            self.logger.info(f"✅ LED Matrix initialized: {options.cols}x{options.rows}")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize LED matrix: {e}")
            self.matrix = None

    def setup_fonts(self):
        """Setup fonts for display"""
        if not LED_MATRIX_AVAILABLE:
            return

        font_config = self.display_config.get('fonts', {})

        try:
            # Try to load BDF fonts (standard for LED matrices)
            font_path = "/home/pi/servicenow-led-dashboard/submodules/rpi-rgb-led-matrix/fonts/"

            # Load different font sizes
            small_font = font_config.get('small', '4x6.bdf')
            medium_font = font_config.get('medium', '5x8.bdf')
            large_font = font_config.get('large', '6x10.bdf')

            self.font_small = graphics.Font()
            self.font_small.LoadFont(os.path.join(font_path, small_font))

            self.font = graphics.Font()
            self.font.LoadFont(os.path.join(font_path, medium_font))

            self.font_large = graphics.Font()
            self.font_large.LoadFont(os.path.join(font_path, large_font))

            self.logger.info("✅ Fonts loaded successfully")

        except Exception as e:
            self.logger.error(f"⚠️  Could not load fonts: {e}")
            # Create default fonts
            self.font = graphics.Font()
            self.font_small = graphics.Font()
            self.font_large = graphics.Font()

    def get_color(self, color_name: str, default: Tuple[int, int, int] = (255, 255, 255)) -> graphics.Color:
        """Get color from configuration"""
        if not LED_MATRIX_AVAILABLE:
            return default

        color_rgb = self.colors.get(color_name, default)
        return graphics.Color(color_rgb[0], color_rgb[1], color_rgb[2])

    def clear_canvas(self):
        """Clear the display canvas"""
        if self.canvas:
            self.canvas.Clear()

    def draw_text(self, text: str, x: int, y: int, color: graphics.Color, font: graphics.Font = None):
        """Draw text on canvas"""
        if not self.canvas:
            return

        if font is None:
            font = self.font

        graphics.DrawText(self.canvas, font, x, y, color, text)

    def draw_rectangle(self, x: int, y: int, width: int, height: int, color: graphics.Color):
        """Draw filled rectangle"""
        if not self.canvas:
            return

        for py in range(y, y + height):
            for px in range(x, x + width):
                if 0 <= px < self.matrix_config.get('led_cols', 64) and 0 <= py < self.matrix_config.get('led_rows',
                                                                                                         32):
                    self.canvas.SetPixel(px, py, color.red, color.green, color.blue)

    def start_display(self):
        """Start the display"""
        if self.matrix:
            self.logger.info("🖥️  Display started")
        else:
            self.logger.info("🖥️  Display simulation mode started")

    def set_alerts(self, alerts: List[Dict[str, Any]]):
        """Set current alerts"""
        self.alerts = alerts

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []

    def should_flash_alerts(self) -> bool:
        """Check if alerts should be flashing"""
        if not self.alerts:
            return False

        # Flash every 0.5 seconds
        now = time.time()
        if now - self.last_alert_flash > 0.5:
            self.alert_flash_state = not self.alert_flash_state
            self.last_alert_flash = now

        return self.alert_flash_state

    def render_screen(self, screen_name: str, data: Dict[str, Any]):
        """Render a specific screen"""
        self.clear_canvas()

        # Handle alert flashing
        if self.alerts and self.should_flash_alerts():
            # Flash red background for critical alerts
            critical_alerts = [a for a in self.alerts if a.get('level') == 'critical']
            if critical_alerts:
                self.draw_rectangle(0, 0, 64, 32, self.get_color('critical', (255, 0, 0)))

        # Render specific screen content
        if screen_name == 'incident_summary':
            self.render_incident_summary(data)
        elif screen_name == 'priority_breakdown':
            self.render_priority_breakdown(data)
        elif screen_name == 'assignment_groups':
            self.render_assignment_groups(data)
        elif screen_name == 'service_requests':
            self.render_service_requests(data)
        elif screen_name == 'system_health':
            self.render_system_health(data)
        else:
            self.render_default_screen(data)

        # Update display
        if self.matrix:
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        else:
            # Simulation mode - just log what we would display
            self.logger.debug(f"Displaying screen: {screen_name}")

    def render_incident_summary(self, data: Dict[str, Any]):
        """Render incident summary screen"""
        incidents = data.get('incidents', {})
        kpis = data.get('kpis', {})

        # Title
        self.draw_text("INCIDENTS", 2, 6, self.get_color('healthy', (0, 255, 0)), self.font_small)

        # Total incidents
        total = incidents.get('total_incidents', 0)
        self.draw_text(f"Total: {total}", 2, 14, graphics.Color(255, 255, 255), self.font_small)

        # Critical/High priority
        critical = kpis.get('critical_open', 0)
        color = self.get_color('critical', (255, 0, 0)) if critical > 0 else graphics.Color(255, 255, 255)
        self.draw_text(f"P1/P2: {critical}", 2, 22, color, self.font_small)

        # Open incidents
        open_count = kpis.get('total_open', 0)
        self.draw_text(f"Open: {open_count}", 35, 14, graphics.Color(255, 255, 255), self.font_small)

        # Resolution rate
        res_rate = kpis.get('resolution_rate', 0)
        self.draw_text(f"Res: {res_rate}%", 35, 22, graphics.Color(255, 255, 255), self.font_small)

        # Last update time
        timestamp = data.get('timestamp', '')
        if timestamp:
            time_str = timestamp.split(' ')[1][:5]  # HH:MM
            self.draw_text(time_str, 40, 30, graphics.Color(128, 128, 128), self.font_small)

    def render_priority_breakdown(self, data: Dict[str, Any]):
        """Render priority breakdown screen"""
        incidents = data.get('incidents', {})
        by_priority = incidents.get('by_priority', {})

        # Title
        self.draw_text("PRIORITY", 2, 6, graphics.Color(255, 255, 255), self.font_small)

        # Priority levels
        priorities = [
            ('P1', '1', 'priority_1', (255, 0, 0)),
            ('P2', '2', 'priority_2', (255, 165, 0)),
            ('P3', '3', 'priority_3', (255, 255, 0)),
            ('P4', '4', 'priority_4', (0, 255, 0))
        ]

        y_pos = 12
        for label, key, color_key, default_color in priorities:
            count = by_priority.get(key, 0)
            color = self.get_color(color_key, default_color) if count > 0 else graphics.Color(128, 128, 128)

            # Draw priority indicator (small rectangle)
            if count > 0:
                self.draw_rectangle(2, y_pos - 3, 8, 4, color)

            # Draw text
            self.draw_text(f"{label}: {count}", 12, y_pos, color, self.font_small)
            y_pos += 5

    def render_assignment_groups(self, data: Dict[str, Any]):
        """Render assignment groups screen"""
        incidents = data.get('incidents', {})
        groups = incidents.get('assignment_groups', {})

        # Title
        self.draw_text("GROUPS", 2, 6, graphics.Color(255, 255, 255), self.font_small)

        # Show top 4 groups by incident count
        sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:4]

        y_pos = 12
        for group_name, count in sorted_groups:
            # Truncate long group names
            display_name = group_name[:10] if len(group_name) > 10 else group_name

            # Use group mappings if available
            group_mappings = self.config.get('group_mappings', {})
            display_name = group_mappings.get(group_name, display_name)

            color = graphics.Color(255, 255, 255) if count > 0 else graphics.Color(128, 128, 128)
            self.draw_text(f"{display_name}: {count}", 2, y_pos, color, self.font_small)
            y_pos += 5

    def render_service_requests(self, data: Dict[str, Any]):
        """Render service requests screen"""
        requests = data.get('service_requests', {})

        # Title
        self.draw_text("REQUESTS", 2, 6, graphics.Color(255, 255, 255), self.font_small)

        # Total requests
        total = requests.get('total_requests', 0)
        self.draw_text(f"Total: {total}", 2, 14, graphics.Color(255, 255, 255), self.font_small)

        # Pending approval
        pending = requests.get('pending_approval', 0)
        color = self.get_color('warning', (255, 255, 0)) if pending > 0 else graphics.Color(255, 255, 255)
        self.draw_text(f"Pending: {pending}", 2, 22, color, self.font_small)

        # In progress
        in_progress = requests.get('in_progress', 0)
        self.draw_text(f"Progress: {in_progress}", 35, 14, graphics.Color(255, 255, 255), self.font_small)

        # Fulfilled
        fulfilled = requests.get('fulfilled', 0)
        self.draw_text(f"Done: {fulfilled}", 35, 22, self.get_color('healthy', (0, 255, 0)), self.font_small)

    def render_system_health(self, data: Dict[str, Any]):
        """Render system health screen"""
        health = data.get('system_health', {})
        kpis = data.get('kpis', {})

        # Title
        self.draw_text("HEALTH", 2, 6, graphics.Color(255, 255, 255), self.font_small)

        # Overall health percentage
        health_pct = kpis.get('health_percentage', 0)
        if health_pct >= 95:
            color = self.get_color('healthy', (0, 255, 0))
        elif health_pct >= 85:
            color = self.get_color('warning', (255, 255, 0))
        else:
            color = self.get_color('critical', (255, 0, 0))

        self.draw_text(f"{health_pct}%", 25, 16, color, self.font_large)

        # Systems up/down
        up = health.get('systems_up', 0)
        down = health.get('systems_down', 0)

        self.draw_text(f"Up: {up}", 2, 26, self.get_color('healthy', (0, 255, 0)), self.font_small)
        self.draw_text(f"Down: {down}", 35, 26,
                       self.get_color('critical', (255, 0, 0)) if down > 0 else graphics.Color(255, 255, 255),
                       self.font_small)

        # Average response time
        avg_response = health.get('avg_response_time', 0)
        self.draw_text(f"Resp: {avg_response}ms", 2, 14, graphics.Color(255, 255, 255), self.font_small)

    def render_default_screen(self, data: Dict[str, Any]):
        """Render default screen when screen type is unknown"""
        self.draw_text("ServiceNow", 2, 10, graphics.Color(0, 255, 0), self.font)
        self.draw_text("Dashboard", 2, 20, graphics.Color(0, 255, 0), self.font)

        # Show timestamp
        timestamp = data.get('timestamp', '')
        if timestamp:
            time_str = timestamp.split(' ')[1][:5]  # HH:MM
            self.draw_text(time_str, 25, 30, graphics.Color(128, 128, 128), self.font_small)

    def cleanup(self):
        """Clean up display resources"""
        if self.matrix:
            self.matrix.Clear()
            self.logger.info("Display cleared")


# Simulation mode for testing without hardware
class DisplaySimulator:
    """Simulate LED display for testing purposes"""

    def __init__(self, width: int = 64, height: int = 32):
        self.width = width
        self.height = height
        self.logger = logging.getLogger(__name__)

    def simulate_render(self, screen_name: str, data: Dict[str, Any]):
        """Simulate rendering a screen"""
        incidents = data.get('incidents', {})
        kpis = data.get('kpis', {})

        print(f"\n{'=' * 50}")
        print(f"🖥️  SCREEN: {screen_name.upper()}")
        print(f"{'=' * 50}")

        if screen_name == 'incident_summary':
            print(f"📊 INCIDENT SUMMARY")
            print(f"   Total Incidents: {incidents.get('total_incidents', 0)}")
            print(f"   Critical/High (P1/P2): {kpis.get('critical_open', 0)}")
            print(f"   Open Incidents: {kpis.get('total_open', 0)}")
            print(f"   Resolution Rate: {kpis.get('resolution_rate', 0)}%")

        elif screen_name == 'priority_breakdown':
            print(f"🚨 PRIORITY BREAKDOWN")
            by_priority = incidents.get('by_priority', {})
            for p in ['1', '2', '3', '4', '5']:
                count = by_priority.get(p, 0)
                print(f"   P{p}: {count}")

        elif screen_name == 'system_health':
            health = data.get('system_health', {})
            print(f"💚 SYSTEM HEALTH")
            print(f"   Overall Health: {kpis.get('health_percentage', 0)}%")
            print(f"   Systems Up: {health.get('systems_up', 0)}")
            print(f"   Systems Down: {health.get('systems_down', 0)}")
            print(f"   Avg Response: {health.get('avg_response_time', 0)}ms")

        print(f"   Updated: {data.get('timestamp', 'Unknown')}")
        print(f"{'=' * 50}")


def test_display():
    """Test the display renderer with sample data"""
    # Sample configuration
    config = {
        'matrix': {
            'led_rows': 32,
            'led_cols': 64,
            'led_brightness': 60,
            'hardware_mapping': 'adafruit-hat',
            'gpio_slowdown': 1
        },
        'display': {
            'colors': {
                'priority_1': [255, 0, 0],
                'priority_2': [255, 165, 0],
                'priority_3': [255, 255, 0],
                'priority_4': [0, 255, 0],
                'healthy': [0, 255, 0],
                'warning': [255, 255, 0],
                'critical': [255, 0, 0]
            },
            'fonts': {
                'small': '4x6.bdf',
                'medium': '5x8.bdf',
                'large': '6x10.bdf'
            }
        }
    }

    # Sample data
    sample_data = {
        'timestamp': '2024-01-15 14:30:00',
        'incidents': {
            'total_incidents': 42,
            'by_priority': {'1': 2, '2': 5, '3': 15, '4': 18, '5': 2},
            'open_incidents': 25,
            'resolved_today': 17,
            'assignment_groups': {
                'L1 Support': 12,
                'L2 Support': 8,
                'DBA Team': 3,
                'Network': 2
            }
        },
        'service_requests': {
            'total_requests': 28,
            'pending_approval': 5,
            'in_progress': 12,
            'fulfilled': 11
        },
        'system_health': {
            'systems_up': 15,
            'systems_down': 1,
            'total_systems': 16,
            'avg_response_time': 245
        },
        'kpis': {
            'critical_open': 7,
            'resolution_rate': 40.5,
            'total_open': 25,
            'health_percentage': 93.8
        }
    }

    if LED_MATRIX_AVAILABLE:
        # Test with real hardware
        renderer = DisplayRenderer(config)
        renderer.start_display()

        screens = ['incident_summary', 'priority_breakdown', 'system_health']

        for screen in screens:
            print(f"Displaying: {screen}")
            renderer.render_screen(screen, sample_data)
            time.sleep(3)

        renderer.cleanup()
    else:
        # Test with simulator
        simulator = DisplaySimulator()
        screens = ['incident_summary', 'priority_breakdown', 'system_health']

        for screen in screens:
            simulator.simulate_render(screen, sample_data)
            time.sleep(2)


if __name__ == "__main__":
    test_display()