#!/usr/bin/env python3
"""
Enhanced API test script for the modular ServiceNow LED Dashboard
Tests the config-driven approach and validates configuration
"""

import sys
import os
import yaml
import requests
import logging
from datetime import datetime
from typing import Dict, Any

# Add the project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header():
    """Print test header"""
    print("✅ Successfully imported required modules")
    print("🚀 ServiceNow LED Dashboard API Test (Enhanced)")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def test_internet_connection():
    """Test basic internet connectivity"""
    print("\n🌐 Testing basic internet connectivity...")
    try:
        response = requests.get("https://www.google.com", timeout=10)
        response.raise_for_status()
        print("✅ Internet connection working")
        return True
    except Exception as e:
        print(f"❌ Internet connection failed: {e}")
        return False


def load_and_validate_config():
    """Load and validate configuration"""
    print("\n📋 Loading configuration...")

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return None

    print(f"📁 Found config file: {os.path.basename(config_path)}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Configuration loaded successfully")

        # Basic validation
        required_sections = ['servicenow', 'display', 'matrix']
        missing_sections = [s for s in required_sections if s not in config]

        if missing_sections:
            print(f"❌ Missing required config sections: {missing_sections}")
            return None

        sn_config = config.get('servicenow', {})
        required_fields = ['instance_url', 'username', 'password']
        missing_fields = [f for f in required_fields if not sn_config.get(f)]

        if missing_fields:
            print(f"❌ Missing required ServiceNow fields: {missing_fields}")
            return None

        print("✅ Configuration validation passed")
        return config

    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None


def test_manual_api_call(config: Dict[str, Any]):
    """Test manual API call to verify credentials work"""
    print("\n🔧 Testing manual API call...")

    sn_config = config['servicenow']

    url = f"{sn_config['instance_url'].rstrip('/')}/api/now/table/incident"
    params = {'sysparm_limit': 1}
    auth = (sn_config['username'], sn_config['password'])

    try:
        response = requests.get(
            url,
            params=params,
            auth=auth,
            verify=sn_config.get('verify_ssl', True),
            timeout=sn_config.get('timeout', 30)
        )

        print(f"📡 Response status: {response.status_code}")
        print(f"📏 Response headers: {dict(response.headers)}")

        response.raise_for_status()
        data = response.json()

        print("✅ Manual API call successful!")
        print(f"📊 Returned {len(data.get('result', []))} records")
        return True

    except Exception as e:
        print(f"❌ Manual API call failed: {e}")
        return False


def test_modular_api_connection(config: Dict[str, Any]):
    """Test the new modular API system"""
    print("\n🔗 Testing modular ServiceNow API connection...")

    try:
        # Import the new modular classes
        from servicenow_api import ServiceNowAPI, ConfigDrivenDashboard

        sn_config = config['servicenow']

        print(f"🏢 Instance: {sn_config['instance_url']}")
        print(f"👤 Username: {sn_config['username']}")
        print("🔒 Password: **********")

        # Create API instance (only with connection parameters)
        api_params = {
            'instance_url': sn_config['instance_url'],
            'username': sn_config['username'],
            'password': sn_config['password'],
            'verify_ssl': sn_config.get('verify_ssl', True),
            'timeout': sn_config.get('timeout', 30)
        }

        api = ServiceNowAPI(**api_params)
        print("✅ ServiceNow API instance created successfully!")

        # Create config-driven dashboard
        dashboard = ConfigDrivenDashboard(config, api)
        print("✅ Config-driven dashboard created successfully!")

        return dashboard

    except Exception as e:
        print(f"❌ Error creating modular API: {e}")
        print(f"🔍 Error details: {str(e)}")
        return None


def test_configuration_validation(dashboard):
    """Test configuration validation"""
    print("\n🔍 Testing configuration validation...")

    try:
        issues = dashboard.validate_configuration()

        if issues['errors']:
            print("❌ Configuration errors found:")
            for error in issues['errors']:
                print(f"   • {error}")
        else:
            print("✅ No configuration errors found")

        if issues['warnings']:
            print("⚠️ Configuration warnings:")
            for warning in issues['warnings']:
                print(f"   • {warning}")
        else:
            print("✅ No configuration warnings")

        return len(issues['errors']) == 0

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def test_table_discovery(dashboard):
    """Test what tables are actually configured and available"""
    print("\n📋 Testing configured data sources...")

    try:
        tables = dashboard.get_configured_tables()
        custom_metrics = dashboard.get_configured_custom_metrics()
        screens = dashboard.get_configured_screens()
        available_screens = dashboard.get_available_screens()

        print(f"📊 Configured tables: {len(tables)}")
        for data_type, table_name in tables.items():
            print(f"   • {data_type}: {table_name}")

        print(f"📈 Configured custom metrics: {len(custom_metrics)}")
        for metric_name, config in custom_metrics.items():
            print(f"   • {metric_name}: {config.get('table', 'No table')}")

        print(f"🖥️ Configured screens: {len(screens)}")
        for screen in screens:
            print(f"   • {screen}")

        print(f"✅ Available screens (with data): {len(available_screens)}")
        for screen in available_screens:
            print(f"   • {screen}")

        unavailable = set(screens) - set(available_screens)
        if unavailable:
            print(f"⚠️ Unavailable screens (missing data): {list(unavailable)}")

        return True

    except Exception as e:
        print(f"❌ Table discovery failed: {e}")
        return False


def test_data_fetching(dashboard):
    """Test fetching data using the modular approach"""
    print("\n📊 Testing modular data fetching...")

    try:
        print("🔄 Fetching dashboard data (config-driven)...")
        data = dashboard.get_dashboard_data()

        print(f"✅ Successfully fetched {len(data)} data types:")

        for data_type, content in data.items():
            if isinstance(content, dict):
                if 'total' in content:
                    print(f"   • {data_type}: {content['total']} items")
                elif 'raw_data' in content:
                    raw_count = len(content['raw_data']) if isinstance(content['raw_data'], list) else 0
                    print(f"   • {data_type}: {raw_count} raw items")
                else:
                    print(f"   • {data_type}: {len(content)} fields")
            elif isinstance(content, list):
                print(f"   • {data_type}: {len(content)} items")
            else:
                print(f"   • {data_type}: {type(content).__name__}")

        # Show some sample data if available
        if 'incidents' in data and data['incidents'].get('total', 0) > 0:
            incidents = data['incidents']
            print(f"   📋 Incident breakdown:")
            if 'by_priority' in incidents:
                for priority, count in incidents['by_priority'].items():
                    print(f"      Priority {priority}: {count}")

        if 'system_health' in data:
            health = data['system_health']
            print(f"   🏥 System health: {health.get('health_percentage', 'N/A')}%")

        return True

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print(f"🔍 Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_tables(dashboard):
    """Test individual table access"""
    print("\n🔧 Testing individual table access...")

    try:
        tables = dashboard.get_configured_tables()
        api = dashboard.api

        for data_type, table_name in tables.items():
            print(f"📊 Testing table: {table_name} (for {data_type})")

            try:
                # Test with minimal fields to reduce data transfer
                data = api.get_data_from_table(table_name, ['sys_id', 'number'], limit=1)
                print(f"   ✅ {table_name}: {len(data)} records")
            except Exception as e:
                print(f"   ❌ {table_name}: {str(e)}")

        return True

    except Exception as e:
        print(f"❌ Individual table testing failed: {e}")
        return False


def main():
    """Main test function"""
    print_header()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    all_tests_passed = True

    # Test 1: Internet connectivity
    if not test_internet_connection():
        print("\n💀 Cannot continue without internet connection")
        return False

    # Test 2: Load configuration
    config = load_and_validate_config()
    if not config:
        print("\n💀 Cannot continue without valid configuration")
        return False

    # Test 3: Manual API call
    if not test_manual_api_call(config):
        print("\n💀 Cannot continue - API credentials appear to be invalid")
        return False

    # Test 4: Modular API connection
    dashboard = test_modular_api_connection(config)
    if not dashboard:
        print("\n💀 Cannot continue - modular API creation failed")
        return False

    # Test 5: Configuration validation
    if not test_configuration_validation(dashboard):
        print("\n⚠️ Configuration has errors, but continuing...")
        all_tests_passed = False

    # Test 6: Table discovery
    if not test_table_discovery(dashboard):
        print("\n⚠️ Table discovery failed, but continuing...")
        all_tests_passed = False

    # Test 7: Individual table testing
    if not test_individual_tables(dashboard):
        print("\n⚠️ Some individual tables failed, but continuing...")
        all_tests_passed = False

    # Test 8: Full data fetching
    if not test_data_fetching(dashboard):
        print("\n❌ Data fetching failed")
        all_tests_passed = False

    # Final results
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Your modular ServiceNow LED Dashboard is ready!")
    else:
        print("⚠️ Some tests failed, but basic functionality works.")
        print("Check the warnings above and adjust your configuration as needed.")

    print("🔧 Next steps:")
    print("   1. Review any configuration warnings above")
    print("   2. Test the LED matrix display")
    print("   3. Run the main dashboard application")

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)