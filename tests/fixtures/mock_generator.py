import random
import time
from typing import Dict, List
from src.core.interfaces import DataPoint


class MockDataGenerator:
    """Generate realistic mock data for testing"""

    @staticmethod
    def generate_incident_data() -> Dict[str, DataPoint]:
        """Generate mock incident data"""
        base_time = time.time()

        return {
            'incidents.total': DataPoint(
                source='mock',
                metric='incidents.total',
                value=random.randint(20, 100),
                timestamp=base_time
            ),
            'incidents.critical': DataPoint(
                source='mock',
                metric='incidents.critical',
                value=random.randint(0, 10),
                timestamp=base_time
            ),
            'incidents.open': DataPoint(
                source='mock',
                metric='incidents.open',
                value=random.randint(10, 50),
                timestamp=base_time
            ),
            'incidents.resolution_rate': DataPoint(
                source='mock',
                metric='incidents.resolution_rate',
                value=random.uniform(30, 95),
                timestamp=base_time
            )
        }