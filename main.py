#!/usr/bin/env python3
"""
ServiceNow LED Dashboard - Main Application
Modular, extensible, environment-aware
"""

import asyncio
import signal
import sys
import os
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.config_manager import ConfigManager
from src.services.plugin_manager import PluginManager
from src.controllers.dashboard import DashboardController
from src.displays.factory import DisplayFactory
import logging


class Application:
    """Main application class"""

    def __init__(self, environment: Optional[str] = None):
        # Determine environment
        self.environment = environment or os.getenv('DASHBOARD_ENV', 'development')

        # Initialize configuration
        self.config_manager = ConfigManager(self.environment)

        # Setup logging
        self._setup_logging()

        # Initialize plugin manager
        self.plugin_manager = PluginManager(self.config_manager)
        self.plugin_manager.discover_plugins()

        # Create display
        display_config = self.config_manager.get('display', {})
        self.display = DisplayFactory.create_display(display_config, self.environment)

        # Create dashboard controller
        self.dashboard = DashboardController(
            config=self.config_manager,
            plugins=self.plugin_manager,
            display=self.display
        )

        # Setup signal handlers
        self._setup_signals()

    def _setup_logging(self):
        """Configure logging based on environment"""
        log_config = self.config_manager.get('logging', {})
        log_level = log_config.get('level', 'INFO')

        if self.environment == 'development':
            log_level = 'DEBUG'

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    log_config.get('file', f'dashboard_{self.environment}.log')
                )
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting ServiceNow Dashboard in {self.environment} mode")

    def _setup_signals(self):
        """Setup signal handlers for graceful shutdown"""
        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, self._handle_signal)

    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())

    async def run(self):
        """Run the application"""
        try:
            # Initialize display
            if not await self.display.initialize(self.config_manager.get('display', {})):
                raise RuntimeError("Failed to initialize display")

            # Start dashboard
            await self.dashboard.start()

            # Keep running until shutdown
            while self.dashboard.is_running:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)

        finally:
            await self.shutdown()

    async def shutdown(self):
        """Clean shutdown"""
        self.logger.info("Shutting down application...")

        # Stop dashboard
        if hasattr(self, 'dashboard'):
            await self.dashboard.stop()

        # Shutdown display
        if hasattr(self, 'display'):
            await self.display.shutdown()

        self.logger.info("Application shut down complete")


async def main():
    """Main entry point"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='ServiceNow LED Dashboard')
    parser.add_argument('--env', choices=['development', 'production', 'test'],
                        default=None, help='Environment to run in')
    parser.add_argument('--config', help='Path to config file')
    args = parser.parse_args()

    # Create and run application
    app = Application(environment=args.env)
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())