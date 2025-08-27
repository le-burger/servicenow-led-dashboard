import os
import platform
from typing import Dict, Any


class EnvironmentDetector:
    """Detect and configure for current environment"""

    @staticmethod
    def detect() -> Dict[str, Any]:
        """Detect current environment and capabilities"""
        info = {
            'platform': platform.system(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'is_raspberry_pi': False,
            'has_gpio': False,
            'has_led_matrix': False,
            'recommended_display': 'terminal'
        }

        # Check if running on Raspberry Pi
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                if 'Raspberry Pi' in model:
                    info['is_raspberry_pi'] = True
                    info['pi_model'] = model.strip()
        except:
            pass

        # Check for GPIO availability
        try:
            import RPi.GPIO
            info['has_gpio'] = True
        except ImportError:
            pass

        # Check for LED matrix library
        try:
            import rgbmatrix
            info['has_led_matrix'] = True
            info['recommended_display'] = 'led_matrix'
        except ImportError:
            pass

        # Determine best display type
        if not info['has_led_matrix']:
            if 'SSH_CONNECTION' in os.environ:
                info['recommended_display'] = 'terminal'
            elif 'DISPLAY' in os.environ:
                info['recommended_display'] = 'simulator'
            else:
                info['recommended_display'] = 'terminal'

        return info