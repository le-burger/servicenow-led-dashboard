import asyncio
import logging
import time
from typing import Optional

class DashboardController:
    """Main dashboard controller that orchestrates everything"""

    def __init__(self, config, plugins, display):
        self.config = config
        self.plugins = plugins
        self.display = display
        self.logger = logging.getLogger(__name__)

        # Components
        self.screen_manager = None
        self.alert_manager = None
        self.data_manager = None

        # State
        self.is_running = False
        self.current_screen = None
        self.last_screen_change = 0
        self.rotation_interval = config.get('display.rotation_time', 10)

    async def start(self):
        """Start the dashboard"""
        self.logger.info("Starting dashboard...")

        # Initialize components
        from .screen_manager import ScreenManager
        from .alert_manager import AlertManager
        from ..services.data_manager import DataManager

        self.screen_manager = ScreenManager(self.plugins, self.config)
        self.alert_manager = AlertManager(self.config)
        self.data_manager = DataManager(self.plugins)

        # Initialize data sources
        data_sources = self.config.get('data_sources.enabled', ['mock'])
        await self.data_manager.initialize(data_sources)
        await self.data_manager.connect_all()

        # Load screens
        self.screen_manager.load_screens()

        # Start main loop
        self.is_running = True
        asyncio.create_task(self._run_loop())

        self.logger.info("Dashboard started")

    async def stop(self):
        """Stop the dashboard"""
        self.logger.info("Stopping dashboard...")
        self.is_running = False

        if self.data_manager:
            await self.data_manager.disconnect_all()

        await asyncio.sleep(1)  # Allow tasks to complete
        self.logger.info("Dashboard stopped")

    async def _run_loop(self):
        """Main dashboard loop"""
        while self.is_running:
            try:
                # Get current screen
                current_time = time.time()

                if (self.current_screen is None or
                    current_time - self.last_screen_change >= self.rotation_interval):

                    self.current_screen = self.screen_manager.get_next_screen()
                    self.last_screen_change = current_time

                    if self.current_screen:
                        self.rotation_interval = self.current_screen.get_display_duration()

                if self.current_screen:
                    # Get required metrics
                    required_metrics = self.current_screen.get_required_metrics()

                    # Fetch data
                    data = await self.data_manager.fetch_metrics(required_metrics)

                    # Process data
                    screen_data = self.current_screen.process_data(data)

                    # Check for alerts
                    alerts = self.alert_manager.check_alerts(data)
                    if alerts:
                        screen_data.alerts = alerts

                    # Render
                    await self.display.render(screen_data)

                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in dashboard loop: {e}", exc_info=True)
                await asyncio.sleep(1)