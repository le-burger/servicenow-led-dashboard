from typing import Dict, List
from src.core.interfaces import IScreen, DataPoint, ScreenData


class IncidentSummaryScreen(IScreen):
    """Display incident summary information"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.duration = self.config.get('duration', 10)

    def get_required_metrics(self) -> List[str]:
        """Metrics needed for this screen"""
        return [
            'incidents.total',
            'incidents.critical',
            'incidents.open',
            'incidents.resolution_rate',
            'incidents.by_priority'
        ]

    def process_data(self, data: Dict[str, DataPoint]) -> ScreenData:
        """Process raw data into display format"""

        # Extract values with defaults
        total = self._get_value(data, 'incidents.total', 0)
        critical = self._get_value(data, 'incidents.critical', 0)
        open_count = self._get_value(data, 'incidents.open', 0)
        resolution_rate = self._get_value(data, 'incidents.resolution_rate', 0)
        by_priority = self._get_value(data, 'incidents.by_priority', {})

        # Build display data
        display_data = {
            'sections': [
                {
                    'type': 'title',
                    'text': 'INCIDENTS',
                    'color': 'green' if critical == 0 else 'red'
                },
                {
                    'type': 'metric',
                    'label': 'Total',
                    'value': str(total),
                    'position': (2, 14)
                },
                {
                    'type': 'metric',
                    'label': 'P1/P2',
                    'value': str(critical),
                    'color': 'red' if critical > 0 else 'white',
                    'position': (2, 22)
                },
                {
                    'type': 'metric',
                    'label': 'Open',
                    'value': str(open_count),
                    'position': (35, 14)
                },
                {
                    'type': 'metric',
                    'label': 'Res',
                    'value': f'{resolution_rate}%',
                    'position': (35, 22)
                }
            ]
        }

        # Add alerts if needed
        alerts = []
        if critical > self.config.get('critical_threshold', 5):
            alerts.append({
                'level': 'critical',
                'message': f'{critical} critical incidents!'
            })

        return ScreenData(
            title='Incident Summary',
            data=display_data,
            alerts=alerts,
            refresh_rate=self.config.get('refresh_rate', 60)
        )

    def get_display_duration(self) -> int:
        """How long to show this screen"""
        return self.duration

    def _get_value(self, data: Dict[str, DataPoint], key: str, default: Any) -> Any:
        """Safely get value from data"""
        if key in data and data[key]:
            return data[key].value
        return default