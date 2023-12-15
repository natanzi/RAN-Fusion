# database_manager.py, this file located in database folder
import os
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, WritePrecision, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
from logs.logger_config import database_logger

# Configure logging
logging.basicConfig(filename='database_manager.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            logging.info("Database connection successful.")
            return True
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False
###################################################################################################################################        
    def insert_data_batch(self, points):
        """Inserts a batch of Point objects into InfluxDB."""
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            database_logger.info("Batch data inserted into InfluxDB")
        except Exception as e:
            database_logger.error(f"Failed to insert batch data into InfluxDB: {e}")
##################################################################################################################################            
    #to Write data into influx BD
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
            database_logger.info(f"Data inserted for measurement {point._name} with tags {tags_description}")

        except Exception as e:
            database_logger.error(f"Failed to insert data into InfluxDB: {e}")

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()
################################################################################################################################
    #To write log data into influx db for further analysis
    def insert_log(self, log_point):
        """Inserts log data into the logs bucket in InfluxDB."""
        log_bucket = 'RAN_logs' 
        try:
            self.write_api.write(bucket=log_bucket, record=log_point)
            database_logger.info(f"Log data inserted into bucket {log_bucket}")
        except Exception as e:
            database_logger.error(f"Failed to insert log data into InfluxDB: {e}")
