#!/usr/bin/env python3
"""
Test script for ServiceNow API connection
Improved version with detailed output and error handling
"""

import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
    import requests
    from servicenow_api import ServiceNowAPI

    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the virtual environment:")
    print("  source venv/bin/activate")
    sys.exit(1)


def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("\n🌐 Testing basic internet connectivity...")
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ Internet connection working")
            return True
        else:
            print(f"⚠️  Internet test returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Internet connectivity test failed: {e}")
        return False


def load_config():
    """Load and validate configuration"""
    print("\n📋 Loading configuration...")

    config_files = ['config.yaml', 'examples/config_example.yaml']
    config = None

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"📁 Found config file: {config_file}")
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                print("✅ Configuration loaded successfully")
                break
            except yaml.YAMLError as e:
                print(f"❌ Error parsing {config_file}: {e}")
                continue
            except Exception as e:
                print(f"❌ Error loading {config_file}: {e}")
                continue

    if not config:
        print("❌ No valid configuration file found")
        print("Available files:", [f for f in config_files if os.path.exists(f)])
        return None

    # Validate config structure
    if 'servicenow' not in config:
        print("❌ Configuration missing 'servicenow' section")
        return None

    sn_config = config['servicenow']
    required_fields = ['instance_url', 'username', 'password']

    for field in required_fields:
        if field not in sn_config:
            print(f"❌ Configuration missing required field: servicenow.{field}")
            return None
        if not sn_config[field] or sn_config[field] == f"your_{field}_here":
            print(f"❌ Please set servicenow.{field} in config.yaml")
            return None

    print("✅ Configuration validation passed")
    return config


def test_servicenow_connection(config):
    """Test ServiceNow API connection"""
    print("\n🔗 Testing ServiceNow API connection...")

    sn_config = config['servicenow']

    # Print connection details (hide password)
    print(f"🏢 Instance: {sn_config['instance_url']}")
    print(f"👤 Username: {sn_config['username']}")
    print(f"🔒 Password: {'*' * len(sn_config['password'])}")

    try:
        # Initialize API client
        api_config = {
            'instance_url': sn_config['instance_url'],
            'username': sn_config['username'],
            'password': sn_config['password'],
            'verify_ssl': sn_config.get('verify_ssl', True),
            'timeout': sn_config.get('timeout', 30)
        }
        api = ServiceNowAPI(**api_config)
        print("✅ ServiceNow API client initialized")

        # Test basic connection
        print("🧪 Testing API connection...")
        if api.test_connection():
            print("✅ ServiceNow API connection successful!")
            return api
        else:
            print("❌ ServiceNow API connection failed")
            return None

    except Exception as e:
        print(f"❌ Error initializing ServiceNow API: {e}")
        print(f"🔍 Error details: {traceback.format_exc()}")
        return None


def test_manual_api_call(config):
    """Test manual API call to troubleshoot"""
    print("\n🔧 Testing manual API call...")

    sn_config = config['servicenow']
    url = f"{sn_config['instance_url']}/api/now/table/incident"

    try:
        response = requests.get(
            url,
            auth=(sn_config['username'], sn_config['password']),
            params={'sysparm_limit': 1},
            timeout=30,
            verify=sn_config.get('verify_ssl', True)
        )

        print(f"📡 Response status: {response.status_code}")
        print(f"📏 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Manual API call successful!")
            print(f"📊 Returned {len(data.get('result', []))} records")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check username/password")
        elif response.status_code == 403:
            print("❌ Access denied - user may lack required roles")
        else:
            print(f"❌ API call failed: {response.text}")

    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("💡 Try setting verify_ssl: false in config for testing")
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - check instance URL")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("💡 Check if the instance URL is correct")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    return False


def test_data_fetching(api):
    """Test actual data fetching"""
    print("\n📊 Testing data fetching...")

    try:
        # Get dashboard data
        print("🔄 Fetching dashboard data...")
        data = api.get_dashboard_data()

        if data and data.get('status') == 'success':
            print("✅ Dashboard data fetched successfully!")

            # Print summary
            incidents = data.get('incidents', {})
            kpis = data.get('kpis', {})

            print(f"\n📈 Data Summary:")
            print(f"   📅 Timestamp: {data.get('timestamp', 'Unknown')}")
            print(f"   🎫 Total Incidents: {incidents.get('total_incidents', 0)}")
            print(f"   🚨 Critical/High (P1/P2): {kpis.get('critical_open', 0)}")
            print(f"   📂 Open Incidents: {kpis.get('total_open', 0)}")
            print(f"   ✅ Resolution Rate: {kpis.get('resolution_rate', 0)}%")
            print(f"   💚 System Health: {kpis.get('health_percentage', 0)}%")

            # Show priority breakdown
            by_priority = incidents.get('by_priority', {})
            if by_priority:
                print(f"\n🎯 Incident Priority Breakdown:")
                for priority in ['1', '2', '3', '4', '5']:
                    count = by_priority.get(priority, 0)
                    priority_name = {
                        '1': 'Critical', '2': 'High', '3': 'Medium',
                        '4': 'Low', '5': 'Planning'
                    }.get(priority, f'P{priority}')
                    print(f"   P{priority} ({priority_name}): {count}")

            # Show assignment groups
            groups = incidents.get('assignment_groups', {})
            if groups:
                print(f"\n👥 Top Assignment Groups:")
                sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:5]
                for group, count in sorted_groups:
                    print(f"   {group}: {count}")

            return True

        else:
            print("❌ Failed to fetch dashboard data")
            if 'error' in data:
                print(f"🔍 Error: {data['error']}")
            return False

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print(f"🔍 Error details: {traceback.format_exc()}")
        return False


def main():
    """Main test function"""
    print("🚀 ServiceNow LED Dashboard API Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("\n❌ Basic connectivity failed - check internet connection")
        return False

    # Test 2: Load configuration
    config = load_config()
    if not config:
        print("\n❌ Configuration test failed")
        print("💡 Copy examples/config_example.yaml to config.yaml and edit it")
        return False

    # Test 3: Manual API call
    if not test_manual_api_call(config):
        print("\n❌ Manual API test failed")
        return False

    # Test 4: ServiceNow connection
    api = test_servicenow_connection(config)
    if not api:
        print("\n❌ ServiceNow connection test failed")
        return False

    # Test 5: Data fetching
    if not test_data_fetching(api):
        print("\n❌ Data fetching test failed")
        return False

    # All tests passed
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ ServiceNow API connection is working correctly")
    print("✅ Data can be fetched successfully")
    print("✅ Dashboard should work properly")
    print("\n🚀 You can now run the full dashboard:")
    print("   python servicenow_dashboard.py")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        sys.exit(1)