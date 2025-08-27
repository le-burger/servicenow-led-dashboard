import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from src.core.interfaces import DataPoint


class DataManager:
    """Manages data sources and caching"""

    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.logger = logging.getLogger(__name__)
        self.data_sources = {}
        self.cache = {}
        self.cache_ttl = 60  # seconds
        self.connected = False

    async def initialize(self, sources: List[str]):
        """Initialize data sources"""
        for source_name in sources:
            try:
                source = self.plugin_manager.get_plugin('data_sources', source_name)
                self.data_sources[source_name] = source
                self.logger.info(f"Initialized data source: {source_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {source_name}: {e}")

    async def connect_all(self) -> bool:
        """Connect to all data sources"""
        if not self.data_sources:
            self.logger.warning("No data sources to connect")
            return False

        results = await asyncio.gather(
            *[source.connect() for source in self.data_sources.values()],
            return_exceptions=True
        )

        success = all(r is True or r is None for r in results if not isinstance(r, Exception))
        self.connected = success

        if success:
            self.logger.info("Connected to all data sources")
        else:
            self.logger.warning("Some data sources failed to connect")

        return success

    async def fetch_metrics(self, metrics: List[str]) -> Dict[str, DataPoint]:
        """Fetch metrics from appropriate sources"""
        result = {}

        # Check cache first
        now = time.time()
        for metric in metrics:
            cache_key = f"metric:{metric}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if now - timestamp < self.cache_ttl:
                    result[metric] = cached_data

        # Fetch missing metrics
        missing_metrics = [m for m in metrics if m not in result]
        if missing_metrics:
            # Group metrics by source
            metrics_by_source = self._group_metrics_by_source(missing_metrics)

            # Fetch from each source
            fetch_tasks = []
            for source_name, source_metrics in metrics_by_source.items():
                if source_name in self.data_sources:
                    source = self.data_sources[source_name]
                    fetch_tasks.append(source.fetch_data(source_metrics))

            # Gather results
            if fetch_tasks:
                fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

                # Process results
                for fetch_result in fetch_results:
                    if not isinstance(fetch_result, Exception):
                        for metric, data_point in fetch_result.items():
                            result[metric] = data_point
                            # Update cache
                            self.cache[f"metric:{metric}"] = (data_point, now)

        return result

    def _group_metrics_by_source(self, metrics: List[str]) -> Dict[str, List[str]]:
        """Group metrics by their source prefix"""
        grouped = {}

        for metric in metrics:
            # For mock data source, all metrics go to mock
            if 'mock' in self.data_sources:
                if 'mock' not in grouped:
                    grouped['mock'] = []
                grouped['mock'].append(metric)
            else:
                # Extract source from metric name (e.g., 'servicenow.incidents.total')
                parts = metric.split('.')
                if len(parts) >= 2:
                    source = parts[0]
                    if source not in grouped:
                        grouped[source] = []
                    grouped[source].append(metric)

        return grouped

    async def disconnect_all(self):
        """Disconnect from all data sources"""
        if self.data_sources:
            await asyncio.gather(
                *[source.disconnect() for source in self.data_sources.values()],
                return_exceptions=True
            )
        self.connected = False
        self.logger.info("Disconnected from all data sources")