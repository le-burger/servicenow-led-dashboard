import logging
from typing import Dict, List, Any

import requests


class ServiceNowAPI:
    """Fully modular ServiceNow API client that's entirely config-driven"""

    def __init__(self, instance_url: str, username: str, password: str,
                 verify_ssl: bool = True, timeout: int = 30):
        self.instance_url = instance_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Session for connection reuse
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to ServiceNow API"""
        url = f"{self.instance_url}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise

    def get_data_from_table(self, table_name: str, fields: List[str] = None,
                            query: str = None, limit: int = 50) -> List[Dict]:
        """Generic method to fetch data from any ServiceNow table"""
        params = {
            'sysparm_limit': limit
        }

        if fields:
            params['sysparm_fields'] = ','.join(fields)
        if query:
            params['sysparm_query'] = query

        try:
            response = self._make_request(f"/api/now/table/{table_name}", params)
            return response.get('result', [])
        except Exception as e:
            self.logger.warning(f"Failed to fetch data from table '{table_name}': {e}")
            return []


class ConfigDrivenDashboard:
    """Config-driven dashboard that dynamically handles data sources"""

    def __init__(self, config: Dict, api: ServiceNowAPI):
        self.config = config
        self.api = api
        self.logger = logging.getLogger(__name__)

        # Define available data source handlers
        self.data_handlers = {
            'incidents': self._get_incidents,
            'service_requests': self._get_service_requests,
            'system_health': self._get_system_health,
            'custom_metrics': self._get_custom_metrics
        }

        # Define data processors
        self.data_processors = {
            'incidents': self._process_incidents,
            'service_requests': self._process_service_requests,
            'system_health': self._process_system_health,
            'custom_metrics': self._process_custom_metrics
        }

    def get_configured_tables(self) -> Dict[str, str]:
        """Get all configured tables from config"""
        return self.config.get('servicenow', {}).get('tables', {})

    def get_configured_custom_metrics(self) -> Dict[str, Dict]:
        """Get all configured custom metrics from config"""
        return self.config.get('custom_metrics', {})

    def get_configured_screens(self) -> List[str]:
        """Get all configured display screens from config"""
        return self.config.get('display', {}).get('screens', [])

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Dynamically fetch only configured data sources"""
        dashboard_data = {}
        tables = self.get_configured_tables()
        custom_metrics = self.get_configured_custom_metrics()

        self.logger.info("Fetching ServiceNow dashboard data...")

        # Process standard tables
        for data_type, table_name in tables.items():
            if data_type in self.data_handlers:
                try:
                    self.logger.debug(f"Fetching {data_type} from table {table_name}")
                    raw_data = self.data_handlers[data_type](table_name)
                    dashboard_data[data_type] = raw_data
                except Exception as e:
                    self.logger.error(f"Failed to fetch {data_type}: {e}")
                    dashboard_data[data_type] = []

        # Process custom metrics
        if custom_metrics:
            dashboard_data['custom_metrics'] = {}
            for metric_name, metric_config in custom_metrics.items():
                try:
                    self.logger.debug(f"Fetching custom metric: {metric_name}")
                    raw_data = self._get_custom_metric(metric_name, metric_config)
                    dashboard_data['custom_metrics'][metric_name] = raw_data
                except Exception as e:
                    self.logger.error(f"Failed to fetch custom metric {metric_name}: {e}")
                    dashboard_data['custom_metrics'][metric_name] = []

        # Process the raw data into display-ready format
        processed_data = self._process_dashboard_data(dashboard_data)

        return processed_data

    def _process_dashboard_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Process raw data into display-ready format"""
        processed = {}

        for data_type, data in raw_data.items():
            if data_type in self.data_processors:
                try:
                    processed[data_type] = self.data_processors[data_type](data)
                except Exception as e:
                    self.logger.error(f"Failed to process {data_type}: {e}")
                    processed[data_type] = self._get_default_processed_data(data_type)
            else:
                # Pass through unprocessed data
                processed[data_type] = data

        return processed

    def _get_default_processed_data(self, data_type: str) -> Dict:
        """Return safe default data structure for failed processing"""
        defaults = {
            'incidents': {'total': 0, 'by_priority': {}, 'by_state': {}},
            'service_requests': {'total': 0, 'by_state': {}},
            'system_health': {'total_systems': 0, 'healthy_systems': 0, 'health_percentage': 100}
        }
        return defaults.get(data_type, {})

    # Data fetching handlers
    def _get_incidents(self, table_name: str) -> List[Dict]:
        """Fetch incident data"""
        fields = ['number', 'priority', 'state', 'short_description', 'assignment_group', 'opened_at']
        query = 'state!=6^state!=7'  # Exclude resolved/closed
        return self.api.get_data_from_table(table_name, fields, query, limit=100)

    def _get_service_requests(self, table_name: str) -> List[Dict]:
        """Fetch service request data"""
        fields = ['number', 'state', 'short_description', 'assignment_group', 'opened_at']
        query = 'state!=3^state!=4'  # Exclude closed/cancelled
        return self.api.get_data_from_table(table_name, fields, query, limit=100)

    def _get_system_health(self, table_name: str) -> List[Dict]:
        """Fetch system health data"""
        fields = ['name', 'status', 'last_check', 'response_time']
        return self.api.get_data_from_table(table_name, fields, limit=50)

    def _get_custom_metrics(self, data: Dict) -> Dict:
        """Process all custom metrics"""
        return data

    def _get_custom_metric(self, metric_name: str, metric_config: Dict) -> List[Dict]:
        """Fetch a single custom metric"""
        table = metric_config.get('table')
        query = metric_config.get('query', '')
        fields = metric_config.get('fields', ['number', 'state', 'short_description'])

        if not table:
            self.logger.warning(f"No table specified for custom metric: {metric_name}")
            return []

        return self.api.get_data_from_table(table, fields, query, limit=50)

    # Data processing handlers
    def _process_incidents(self, incidents: List[Dict]) -> Dict:
        """Process incident data for display"""
        if not incidents:
            return {'total': 0, 'by_priority': {}, 'by_state': {}}

        by_priority = {}
        by_state = {}
        by_group = {}

        for incident in incidents:
            # Priority breakdown
            priority = incident.get('priority', 'Unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1

            # State breakdown  
            state = incident.get('state', 'Unknown')
            by_state[state] = by_state.get(state, 0) + 1

            # Assignment group breakdown
            group = incident.get('assignment_group', {}).get('display_value', 'Unassigned')
            by_group[group] = by_group.get(group, 0) + 1

        return {
            'total': len(incidents),
            'by_priority': by_priority,
            'by_state': by_state,
            'by_assignment_group': by_group,
            'raw_data': incidents
        }

    def _process_service_requests(self, requests: List[Dict]) -> Dict:
        """Process service request data for display"""
        if not requests:
            return {'total': 0, 'by_state': {}}

        by_state = {}
        by_group = {}

        for request in requests:
            # State breakdown
            state = request.get('state', 'Unknown')
            by_state[state] = by_state.get(state, 0) + 1

            # Assignment group breakdown
            group = request.get('assignment_group', {}).get('display_value', 'Unassigned')
            by_group[group] = by_group.get(group, 0) + 1

        return {
            'total': len(requests),
            'by_state': by_state,
            'by_assignment_group': by_group,
            'raw_data': requests
        }

    def _process_system_health(self, health_data: List[Dict]) -> Dict:
        """Process system health data for display"""
        if not health_data:
            return {
                'total_systems': 0,
                'healthy_systems': 0,
                'health_percentage': 100,
                'by_status': {}
            }

        total_systems = len(health_data)
        by_status = {}
        healthy_statuses = ['active', 'healthy', 'up', 'online', 'ok']
        healthy_systems = 0

        for system in health_data:
            status = system.get('status', 'unknown').lower()
            by_status[status] = by_status.get(status, 0) + 1

            if status in healthy_statuses:
                healthy_systems += 1

        health_percentage = int((healthy_systems / total_systems) * 100) if total_systems > 0 else 100

        return {
            'total_systems': total_systems,
            'healthy_systems': healthy_systems,
            'health_percentage': health_percentage,
            'by_status': by_status,
            'raw_data': health_data
        }

    def _process_custom_metrics(self, custom_data: Dict) -> Dict:
        """Process custom metrics data"""
        processed = {}

        for metric_name, data in custom_data.items():
            processed[metric_name] = {
                'count': len(data) if isinstance(data, list) else 0,
                'raw_data': data
            }

        return processed

    def get_available_screens(self) -> List[str]:
        """Get list of screens that can be displayed based on available data"""
        available_screens = []
        configured_screens = self.get_configured_screens()
        tables = self.get_configured_tables()
        custom_metrics = self.get_configured_custom_metrics()

        # Map screen names to required data
        screen_requirements = {
            'incident_summary': 'incidents',
            'priority_breakdown': 'incidents',
            'assignment_groups': ['incidents', 'service_requests'],
            'service_requests': 'service_requests',
            'system_health': 'system_health'
        }

        for screen in configured_screens:
            if screen in screen_requirements:
                required = screen_requirements[screen]
                if isinstance(required, list):
                    # Screen needs any of the required data types
                    if any(req in tables for req in required):
                        available_screens.append(screen)
                else:
                    # Screen needs specific data type
                    if required in tables:
                        available_screens.append(screen)
            elif screen.startswith('custom_'):
                # Custom metric screen
                metric_name = screen.replace('custom_', '')
                if metric_name in custom_metrics:
                    available_screens.append(screen)
            else:
                # Unknown screen, include it anyway (might be handled elsewhere)
                available_screens.append(screen)

        return available_screens

    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate configuration and return any issues"""
        issues = {
            'warnings': [],
            'errors': []
        }

        tables = self.get_configured_tables()
        screens = self.get_configured_screens()
        custom_metrics = self.get_configured_custom_metrics()

        # Check if any screens won't work
        screen_requirements = {
            'incident_summary': 'incidents',
            'priority_breakdown': 'incidents',
            'assignment_groups': ['incidents', 'service_requests'],
            'service_requests': 'service_requests',
            'system_health': 'system_health'
        }

        for screen in screens:
            if screen in screen_requirements:
                required = screen_requirements[screen]
                if isinstance(required, list):
                    if not any(req in tables for req in required):
                        issues['warnings'].append(
                            f"Screen '{screen}' requires one of {required} but none are configured"
                        )
                else:
                    if required not in tables:
                        issues['warnings'].append(
                            f"Screen '{screen}' requires '{required}' table but it's not configured"
                        )

        # Check custom metrics
        for metric_name, config in custom_metrics.items():
            if 'table' not in config:
                issues['errors'].append(f"Custom metric '{metric_name}' missing required 'table' field")

        return issues