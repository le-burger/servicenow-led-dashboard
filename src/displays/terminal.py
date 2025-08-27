import asyncio
from typing import Dict, Any
from datetime import datetime
from src.core.interfaces import IDisplay, ScreenData


class TerminalDisplay(IDisplay):
    """Terminal-based display for development"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.width = self.config.get('width', 64)
        self.height = self.config.get('height', 32)
        self.clear_screen = self.config.get('clear_screen', True)

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize terminal display"""
        print(f"Terminal Display initialized ({self.width}x{self.height})")
        return True

    async def render(self, screen_data: ScreenData) -> None:
        """Render screen data to terminal"""
        if self.clear_screen:
            print('\033[2J\033[H')  # Clear screen and move cursor to top

        # Render border
        print('╔' + '═' * (self.width + 20) + '╗')

        # Render title
        title = f" {screen_data.title} - {datetime.now().strftime('%H:%M:%S')} "
        print(f"║{title.center(self.width + 20)}║")
        print('╟' + '─' * (self.width + 20) + '╢')

        # Render alerts
        if screen_data.alerts:
            for alert in screen_data.alerts:
                level = alert['level'].upper()
                message = alert['message']
                color = self._get_color(alert['level'])
                print(f"║ {color}[{level}]{self._reset()} {message.ljust(self.width + 10)} ║")
            print('╟' + '─' * (self.width + 20) + '╢')

        # Render sections
        for section in screen_data.data.get('sections', []):
            if section['type'] == 'title':
                color = self._get_color(section.get('color', 'white'))
                text = section['text']
                print(f"║ {color}{text}{self._reset()}".ljust(self.width + 31) + "║")

            elif section['type'] == 'metric':
                label = section['label']
                value = section['value']
                color = self._get_color(section.get('color', 'white'))
                print(f"║   {label}: {color}{value}{self._reset()}".ljust(self.width + 31) + "║")

        # Render footer
        print('╚' + '═' * (self.width + 20) + '╝')

    async def clear(self) -> None:
        """Clear the display"""
        if self.clear_screen:
            print('\033[2J\033[H')

    async def shutdown(self) -> None:
        """Clean shutdown"""
        await self.clear()
        print("Terminal Display shut down")

    def _get_color(self, color_name: str) -> str:
        """Get ANSI color code"""
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'white': '\033[97m',
            'critical': '\033[91m',
            'warning': '\033[93m',
            'healthy': '\033[92m'
        }
        return colors.get(color_name, '\033[97m')

    def _reset(self) -> str:
        """Reset ANSI color"""
        return '\033[0m'