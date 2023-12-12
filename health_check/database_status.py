#database_status.py is located in health check directory
from database.database_manager import DatabaseManager

def check_database_status():
    # Placeholder for actual database status check logic
    db_manager = DatabaseManager()
    connected = db_manager.test_connection()
    return {
        'status': 'UP' if connected else 'DOWN',
        'details': 'Successfully connected to the database' if connected else 'Failed to connect to the database'
    }

if __name__ == "__main__":
    status = check_database_status()
    print(status)