import pytest
from unittest.mock import Mock
from src.screens.incident_summary import IncidentSummaryScreen
from src.core.interfaces import DataPoint


class TestIncidentSummaryScreen:
    """Test incident summary screen"""

    @pytest.fixture
    def screen(self):
        """Create screen instance"""
        config = {'duration': 10, 'critical_threshold': 3}
        return IncidentSummaryScreen(config)

    @pytest.fixture
    def mock_data(self):
        """Create mock data points"""
        return {
            'incidents.total': DataPoint(
                source='servicenow',
                metric='incidents.total',
                value=42,
                timestamp=1234567890
            ),
            'incidents.critical': DataPoint(
                source='servicenow',
                metric='incidents.critical',
                value=5,
                timestamp=1234567890
            )
        }

    def test_required_metrics(self, screen):
        """Test that screen requests correct metrics"""
        metrics = screen.get_required_metrics()
        assert 'incidents.total' in metrics
        assert 'incidents.critical' in metrics

    def test_process_data_with_alerts(self, screen, mock_data):
        """Test data processing with alert generation"""
        result = screen.process_data(mock_data)

        assert result.title == 'Incident Summary'
        assert len(result.alerts) > 0  # Should have alert for 5 critical
        assert result.alerts[0]['level'] == 'critical'

    def test_display_duration(self, screen):
        """Test display duration configuration"""
        assert screen.get_display_duration() == 10