from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio


# Data Models
@dataclass
class DataPoint:
    """Single data point from a source"""
    source: str
    metric: str
    value: Any
    timestamp: float
    metadata: Dict[str, Any] = None


@dataclass
class Alert:
    """Alert information"""
    level: str  # critical, warning, info
    message: str
    source: str = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class ScreenData:
    """Data structure for screen rendering"""
    title: str
    data: Dict[str, Any]
    alerts: List[Alert] = None
    refresh_rate: int = 10

    def __post_init__(self):
        if self.alerts is None:
            self.alerts = []

# Interfaces
class IDataSource(ABC):
    """Interface for all data sources"""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source"""
        pass

    @abstractmethod
    async def fetch_data(self, metrics: List[str]) -> Dict[str, DataPoint]:
        """Fetch specified metrics"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up connection"""
        pass

    @abstractmethod
    def get_available_metrics(self) -> List[str]:
        """Return list of available metrics"""
        pass


class IScreen(ABC):
    """Interface for all screens"""

    @abstractmethod
    def get_required_metrics(self) -> List[str]:
        """Return list of required metrics"""
        pass

    @abstractmethod
    def process_data(self, data: Dict[str, DataPoint]) -> ScreenData:
        """Process raw data for display"""
        pass

    @abstractmethod
    def get_display_duration(self) -> int:
        """Return how long to display this screen"""
        pass


class IDisplay(ABC):
    """Interface for all display types"""

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize display hardware/software"""
        pass

    @abstractmethod
    async def render(self, screen_data: ScreenData) -> None:
        """Render screen data"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear the display"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean shutdown"""
        pass


class IPlugin(ABC):
    """Interface for plugins"""

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Return plugin information"""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with config"""
        pass