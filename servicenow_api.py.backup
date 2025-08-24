#!/usr/bin/env python3
"""
ServiceNow API Client for LED Scoreboard
Fetches performance metrics and incident data from ServiceNow
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import base64


class ServiceNowAPI:
    def __init__(self, instance_url: str, username: str, password: str,
                 verify_ssl: bool = True, timeout: int = 30):
        """
        Initialize ServiceNow API client

        Args:
            instance_url: ServiceNow instance URL (e.g., 'https://yourinstance.service-now.com')
            username: ServiceNow username
            password: ServiceNow password
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.instance_url = instance_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Setup session with authentication
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to ServiceNow API"""
        url = f"{self.instance_url}/api/now/{endpoint}"

        try:
            response = self.session.get(
                url,
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return {"result": [], "error": str(e)}

    def get_incident_metrics(self) -> Dict:
        """
        Get current incident metrics similar to NHL game data
        Returns incident counts by priority and state
        """
        # Get incidents from last 24 hours
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        params = {
            'sysparm_query': f'opened_at>={yesterday.strftime("%Y-%m-%d %H:%M:%S")}',
            'sysparm_fields': 'priority,state,opened_at,resolved_at,assignment_group,short_description',
            'sysparm_limit': '1000'
        }

        data = self._make_request('table/incident', params)

        if 'error' in data:
            return self._get_empty_metrics()

        incidents = data.get('result', [])

        # Process incidents into metrics
        metrics = {
            'total_incidents': len(incidents),
            'by_priority': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'by_state': {
                'new': 0,
                'in_progress': 0,
                'on_hold': 0,
                'resolved': 0,
                'closed': 0,
                'canceled': 0
            },
            'open_incidents': 0,
            'resolved_today': 0,
            'assignment_groups': {},
            'last_updated': now.strftime('%Y-%m-%d %H:%M:%S')
        }

        state_mapping = {
            '1': 'new',
            '2': 'in_progress',
            '3': 'on_hold',
            '6': 'resolved',
            '7': 'closed',
            '8': 'canceled'
        }

        for incident in incidents:
            # Count by priority
            priority = incident.get('priority', '5')
            if priority in metrics['by_priority']:
                metrics['by_priority'][priority] += 1

            # Count by state
            state_num = incident.get('state', '1')
            state_name = state_mapping.get(state_num, 'new')
            if state_name in metrics['by_state']:
                metrics['by_state'][state_name] += 1

            # Count open incidents (states 1, 2, 3)
            if state_num in ['1', '2', '3']:
                metrics['open_incidents'] += 1

            # Count resolved today
            if state_num in ['6', '7'] and incident.get('resolved_at'):
                resolved_date = incident.get('resolved_at', '')[:10]
                if resolved_date == now.strftime('%Y-%m-%d'):
                    metrics['resolved_today'] += 1

            # Count by assignment group
            group = incident.get('assignment_group', {}).get('display_value', 'Unassigned')
            metrics['assignment_groups'][group] = metrics['assignment_groups'].get(group, 0) + 1

        return metrics

    def get_service_request_metrics(self) -> Dict:
        """Get service request metrics"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        params = {
            'sysparm_query': f'opened_at>={yesterday.strftime("%Y-%m-%d %H:%M:%S")}',
            'sysparm_fields': 'state,approval,opened_at,assignment_group',
            'sysparm_limit': '1000'
        }

        data = self._make_request('table/sc_request', params)

        if 'error' in data:
            return {'total_requests': 0, 'by_state': {}, 'by_approval': {}}

        requests_data = data.get('result', [])

        metrics = {
            'total_requests': len(requests_data),
            'by_state': {},
            'by_approval': {},
            'pending_approval': 0,
            'in_progress': 0,
            'fulfilled': 0
        }

        for req in requests_data:
            state = req.get('state', 'unknown')
            approval = req.get('approval', 'not_requested')

            metrics['by_state'][state] = metrics['by_state'].get(state, 0) + 1
            metrics['by_approval'][approval] = metrics['by_approval'].get(approval, 0) + 1

            if approval == 'requested':
                metrics['pending_approval'] += 1
            elif state in ['2', '3']:  # Work in Progress, Pending
                metrics['in_progress'] += 1
            elif state == '3':  # Fulfilled
                metrics['fulfilled'] += 1

        return metrics

    def get_system_health_metrics(self) -> Dict:
        """
        Get system health metrics - customize based on your monitoring setup
        This is a template - you'll need to adapt to your specific health checks
        """
        # Example: Query custom health check table or use Performance Analytics
        params = {
            'sysparm_fields': 'name,status,last_check,response_time',
            'sysparm_limit': '50'
        }

        # Replace 'u_system_health' with your actual health monitoring table
        data = self._make_request('table/u_system_health', params)

        if 'error' in data:
            return {'systems_up': 0, 'systems_down': 0, 'avg_response_time': 0}

        systems = data.get('result', [])

        metrics = {
            'systems_up': 0,
            'systems_down': 0,
            'total_systems': len(systems),
            'avg_response_time': 0,
            'systems_status': {}
        }

        total_response_time = 0

        for system in systems:
            status = system.get('status', 'unknown')
            name = system.get('name', 'unknown')
            response_time = float(system.get('response_time', 0))

            metrics['systems_status'][name] = status

            if status.lower() in ['up', 'online', 'active']:
                metrics['systems_up'] += 1
            else:
                metrics['systems_down'] += 1

            total_response_time += response_time

        if len(systems) > 0:
            metrics['avg_response_time'] = round(total_response_time / len(systems), 2)

        return metrics

    def get_dashboard_data(self) -> Dict:
        """
        Get all dashboard data in one call - similar to NHL API returning all games
        This is the main method that will be called by the display logic
        """
        self.logger.info("Fetching ServiceNow dashboard data...")

        dashboard_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'incidents': self.get_incident_metrics(),
            'service_requests': self.get_service_request_metrics(),
            'system_health': self.get_system_health_metrics(),
            'status': 'success'
        }

        # Add some calculated KPIs
        incidents = dashboard_data['incidents']
        dashboard_data['kpis'] = {
            'critical_open': incidents['by_priority']['1'] + incidents['by_priority']['2'],
            'resolution_rate': self._calculate_resolution_rate(incidents),
            'total_open': incidents['open_incidents'],
            'health_percentage': self._calculate_health_percentage(dashboard_data['system_health'])
        }

        self.logger.info(f"Dashboard data updated: {incidents['total_incidents']} incidents, "
                         f"{dashboard_data['service_requests']['total_requests']} requests")

        return dashboard_data

    def _calculate_resolution_rate(self, incidents: Dict) -> float:
        """Calculate resolution rate percentage"""
        total = incidents['total_incidents']
        if total == 0:
            return 0.0
        resolved = incidents['resolved_today']
        return round((resolved / total) * 100, 1)

    def _calculate_health_percentage(self, health: Dict) -> float:
        """Calculate overall system health percentage"""
        total = health['total_systems']
        if total == 0:
            return 100.0
        up = health['systems_up']
        return round((up / total) * 100, 1)

    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics structure when API fails"""
        return {
            'total_incidents': 0,
            'by_priority': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'by_state': {
                'new': 0, 'in_progress': 0, 'on_hold': 0,
                'resolved': 0, 'closed': 0, 'canceled': 0
            },
            'open_incidents': 0,
            'resolved_today': 0,
            'assignment_groups': {},
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': True
        }

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Simple test query
            params = {'sysparm_limit': '1'}
            result = self._make_request('table/incident', params)
            return 'error' not in result
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


# Example usage and configuration
if __name__ == "__main__":
    # Configuration - in real use, load from config file
    config = {
        'instance_url': 'https://yourinstance.service-now.com',
        'username': 'your_username',
        'password': 'your_password',
        'verify_ssl': True
    }

    # Initialize API client
    sn_api = ServiceNowAPI(**config)

    # Test connection
    if sn_api.test_connection():
        print("✅ ServiceNow connection successful")

        # Get dashboard data
        data = sn_api.get_dashboard_data()

        # Print summary
        print(f"\n📊 Dashboard Summary:")
        print(f"   Total Incidents: {data['incidents']['total_incidents']}")
        print(f"   Critical/High Priority: {data['kpis']['critical_open']}")
        print(f"   Open Incidents: {data['kpis']['total_open']}")
        print(f"   Resolution Rate: {data['kpis']['resolution_rate']}%")
        print(f"   System Health: {data['kpis']['health_percentage']}%")

        # Print detailed breakdown
        print(f"\n🚨 Incidents by Priority:")
        for priority, count in data['incidents']['by_priority'].items():
            print(f"   P{priority}: {count}")

        print(f"\n📋 Service Requests: {data['service_requests']['total_requests']}")

    else:
        print("❌ ServiceNow connection failed - check credentials and URL")