import os
from datetime import datetime
from influxdb_client import InfluxDBClient, WritePrecision, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

# Configure a standard logger for database_manager.py
db_manager_logger = logging.getLogger('db_manager_logger')
db_manager_logger.setLevel(logging.INFO)

# Correct the file path to point to the logs folder and the expected log file
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'database_logger.log')
handler = logging.FileHandler(log_file_path)  # Log to a file inside the logs folder

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
db_manager_logger.addHandler(handler)

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database_manager.log')
handler = logging.FileHandler('database_logger.log') 

# Read from environment variables or use default values
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your-default-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

class DatabaseManager:
    
    def __init__(self, network_state=None):
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = INFLUXDB_BUCKET
        self.network_state = network_state

    def set_network_state(self, network_state):
        """Sets the network state for the database manager."""
        self.network_state = network_state

    def test_connection(self):
        """Test if the connection to the database is successful."""
        try:
            self.client.ping()
            db_manager_logger.info("Database connection successful.")
            return True
        except Exception as e:
            db_manager_logger.error(f"Database connection test failed: {e}")
            return False

    def insert_data_batch(self, points):
        """Inserts a batch of Point objects into InfluxDB."""
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            db_manager_logger.info("Batch data inserted into InfluxDB")
        except Exception as e:
            db_manager_logger.error(f"Failed to insert batch data into InfluxDB: {e}")

    def insert_data(self, measurement_or_point, tags=None, fields=None, timestamp=None):
        """Inserts data into InfluxDB. Can handle both Point objects and separate parameters."""
        try:
            if isinstance(measurement_or_point, Point):
                # If a Point object is provided
                point = measurement_or_point
                if timestamp:
                    point.time(timestamp)
            else:
                # If separate parameters are provided
                measurement = measurement_or_point
                timestamp = timestamp if timestamp is not None else int(datetime.utcnow().timestamp())
                point = Point(measurement)
                for tag_key, tag_value in (tags or {}).items():
                    point.tag(tag_key, tag_value)
                for field_key, field_value in (fields or {}).items():
                    point.field(field_key, field_value)
                point.time(timestamp, WritePrecision.S)

            self.write_api.write(bucket=self.bucket, record=point)
            # Log the measurement and the tags for context
            tags_description = ", ".join([f"{k}={v}" for k, v in point._tags.items()])
            db_manager_logger.info(f"Data inserted for measurement {point._name} with tags {tags_description}")

        except Exception as e:
            db_manager_logger.error(f"Failed to insert data into InfluxDB: {e}")

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

    def insert_log(self, log_point):
        """Inserts log data into the logs bucket in InfluxDB."""
        log_bucket = 'RAN_logs' 
        try:
            self.write_api.write(bucket=log_bucket, record=log_point)
            db_manager_logger.info(f"Log data inserted into bucket {log_bucket}")
        except Exception as e:
            db_manager_logger.error(f"Failed to insert log data into InfluxDB: {e}")
