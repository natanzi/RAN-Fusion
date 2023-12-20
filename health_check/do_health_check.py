# do_health_check.py located in health_check directory
import sys
import time
from .server_status import check_server_status
from .database_status import check_database_status
from .system_resources import check_system_resources
from database.time_utils import get_current_time_ntp, server_pools

# Configuration for database retries
MAX_RETRIES = 3
RETRY_INTERVAL = 5  # in seconds

def check_time_utility():
    try:
        time = current_time = get_current_time_ntp()
        return {'status': 'UP', 'time': time}
    except Exception as e:
        return {'status': 'DOWN', 'error': str(e)}

def perform_health_check(network_state):
    print("Performing health check...waiting for all components to be up...")
    server_status = check_server_status()
    system_resources = check_system_resources()
    time_utility_status = check_time_utility()

    # Attempt to check database status with retries
    database_status = None
    for attempt in range(MAX_RETRIES):
        database_status = check_database_status(network_state)
        if database_status.get('status') == 'UP':
            break
        print(f"Database check failed, attempt {attempt + 1}/{MAX_RETRIES}. Retrying in {RETRY_INTERVAL} seconds...")
        time.sleep(RETRY_INTERVAL)

    print("Server Status:", server_status)
    print("Database Status:", database_status)
    print("System Resources:", system_resources)
    print("Time Utility Status:", time_utility_status)

    if (server_status.get('status') != 'UP' or
        database_status.get('status') != 'UP' or
        system_resources.get('status') != 'UP' or
        time_utility_status.get('status') != 'UP'):
        print("Health check failed. Exiting...")
        sys.exit(1)
    else:
        print("All systems are operational.")
        return True
