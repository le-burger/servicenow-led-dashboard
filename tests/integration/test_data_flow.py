import pytest
import asyncio
from src.services.config_manager import ConfigManager
from src.services.plugin_manager import PluginManager
from src.controllers.dashboard import DashboardController


@pytest.mark.asyncio
class TestDataFlow:
    """Test complete data flow"""

    async def test_end_to_end_data_flow(self):
        """Test data flows from source to display"""
        # Setup
        config = ConfigManager('test')
        plugins = PluginManager(config)
        plugins.discover_plugins()

        # Create mock display
        mock_display = Mock()
        mock_display.render = asyncio.coroutine(Mock())

        # Create dashboard
        dashboard = DashboardController(config, plugins, mock_display)

        # Start dashboard (briefly)
        await dashboard.start()
        await asyncio.sleep(2)
        await dashboard.stop()

        # Verify display was called
        assert mock_display.render.called