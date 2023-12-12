#do_health_check.py located in health_check directory
from .server_status import check_server_status
from .database_status import check_database_status
from .system_resources import check_system_resources

def perform_health_check():
    print("Performing health check...")
    print("Server Status:", check_server_status())
    print("Database Status:", check_database_status())
    print("System Resources:", check_system_resources())

if __name__ == "__main__":
    perform_health_check()