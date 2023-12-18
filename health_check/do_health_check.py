# do_health_check.py located in health_check directory
import sys
from .server_status import check_server_status
from .database_status import check_database_status
from .system_resources import check_system_resources

def perform_health_check(network_state):
    print("Performing health check...")
    server_status = check_server_status()
    database_status = check_database_status(network_state)  # Pass network_state here
    system_resources = check_system_resources()

    print("Server Status:", server_status)
    print("Database Status:", database_status)
    print("System Resources:", system_resources)

    # Check if any of the components report a status other than 'UP'
    if server_status.get('status') != 'UP' or database_status.get('status') != 'UP':
        print("Health check failed. Exiting...")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    else:
        return True  # Add this line to indicate the health check passed