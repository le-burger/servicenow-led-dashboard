import logging
from typing import List, Dict, Any
from src.core.interfaces import Alert, DataPoint


class AlertManager:
    """Manages alert detection and notifications"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.thresholds = config.get('alerts.thresholds', {})
        self.active_alerts = {}

    def check_alerts(self, data: Dict[str, DataPoint]) -> List[Alert]:
        """Check data for alert conditions"""
        alerts = []

        # Check critical incidents threshold
        critical_metric = 'servicenow.incidents.critical'
        if critical_metric in data:
            critical_count = data[critical_metric].value
            threshold = self.thresholds.get('critical_incidents', 5)

            if critical_count >= threshold:
                alert = Alert(
                    level='critical',
                    message=f'{critical_count} critical incidents!',
                    source='incidents'
                )
                alerts.append(alert)
                self.active_alerts['critical_incidents'] = alert
            elif 'critical_incidents' in self.active_alerts:
                del self.active_alerts['critical_incidents']

        # Check system health threshold
        health_metric = 'servicenow.system_health.percentage'
        if health_metric in data:
            health_pct = data[health_metric].value
            threshold = self.thresholds.get('system_health', 90)

            if health_pct < threshold:
                alert = Alert(
                    level='warning',
                    message=f'System health: {health_pct}%',
                    source='system_health'
                )
                alerts.append(alert)
                self.active_alerts['system_health'] = alert
            elif 'system_health' in self.active_alerts:
                del self.active_alerts['system_health']

        return alerts

    def clear_alert(self, alert_id: str):
        """Clear a specific alert"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            self.logger.info(f"Cleared alert: {alert_id}")

    def clear_all_alerts(self):
        """Clear all active alerts"""
        self.active_alerts.clear()
        self.logger.info("Cleared all alerts")