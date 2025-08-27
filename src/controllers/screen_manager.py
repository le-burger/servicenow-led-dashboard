import logging
from typing import List, Optional


class ScreenManager:
    """Manages screen rotation and lifecycle"""

    def __init__(self, plugin_manager, config):
        self.plugin_manager = plugin_manager
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.screens = []
        self.current_index = 0
        self.enabled_screens = config.get('display.screens', [])

    def load_screens(self):
        """Load all configured screens"""
        self.screens = []

        for screen_name in self.enabled_screens:
            try:
                screen = self.plugin_manager.get_plugin('screens', screen_name)
                self.screens.append(screen)
                self.logger.info(f"Loaded screen: {screen_name}")
            except Exception as e:
                self.logger.error(f"Failed to load screen {screen_name}: {e}")

        self.logger.info(f"Loaded {len(self.screens)} screens")

    def get_next_screen(self):
        """Get the next screen in rotation"""
        if not self.screens:
            return None

        screen = self.screens[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.screens)
        return screen

    def get_current_screen(self):
        """Get current screen without advancing"""
        if not self.screens:
            return None

        return self.screens[self.current_index]