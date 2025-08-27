from typing import Dict, Any
from src.core.interfaces import IDisplay


class DisplayFactory:
    """Factory for creating display instances based on environment"""

    @staticmethod
    def create_display(config: Dict[str, Any], environment: str) -> IDisplay:
        """Create appropriate display for environment"""

        if environment == 'production':
            try:
                from src.displays.led_matrix import LEDMatrixDisplay
                return LEDMatrixDisplay(config)
            except ImportError:
                print("LED Matrix not available, falling back to terminal")
                from src.displays.terminal import TerminalDisplay
                return TerminalDisplay(config)

        elif environment == 'development':
            display_type = config.get('development', {}).get('display_type', 'terminal')

            if display_type == 'web':
                from src.displays.web import WebDisplay
                return WebDisplay(config)
            elif display_type == 'simulator':
                from src.displays.simulator import SimulatorDisplay
                return SimulatorDisplay(config)
            else:
                from src.displays.terminal import TerminalDisplay
                return TerminalDisplay(config)

        else:
            from src.displays.terminal import TerminalDisplay
            return TerminalDisplay(config)