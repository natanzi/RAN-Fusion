# do_health_check.py located in health_check directory
import sys
from .server_status import check_server_status
from .database_status import check_database_status
from .system_resources import check_system_resources
from database.time_utils import get_current_time_ntp, server_pools

def check_time_utility():
    try:
        # Attempt to fetch the time from the NTP server
        time = current_time = get_current_time_ntp(server_pools)
        # If the time is successfully fetched, the utility is considered 'UP'
        return {'status': 'UP', 'time': time}
    except Exception as e:
        # If there is an error, the utility is considered 'DOWN'
        return {'status': 'DOWN', 'error': str(e)}

def perform_health_check(network_state):
    print("Performing health check...waiting for all components to be up...")
    server_status = check_server_status()
    database_status = check_database_status(network_state)  
    system_resources = check_system_resources()
    time_utility_status = check_time_utility()  

    print("Server Status:", server_status)
    print("Database Status:", database_status)
    print("System Resources:", system_resources)
    print("Time Utility Status:", time_utility_status)  

    # Check if any of the components report a status other than 'UP'
    if (server_status.get('status') != 'UP' or
        database_status.get('status') != 'UP' or
        time_utility_status.get('status') != 'UP'):  
        print("Health check failed. Exiting...")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    else:
        print("All systems are operational.")
        return True  # Indicate the health check passed