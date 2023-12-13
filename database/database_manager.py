# database_manager.py, this file located in database folder
import os
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, WritePrecision, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

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

    def test_connection(self):
        """Test if the connection to the database is successful."""
        try:
            self.client.ping()
            logging.info("Database connection successful.")
            return True
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False

    def insert_data(self, measurement, tags, fields, timestamp=None):
        """Inserts data into InfluxDB."""
        timestamp = timestamp if timestamp is not None else int(datetime.utcnow().timestamp())  # Current time in seconds
        point = Point(measurement)
        for tag_key, tag_value in tags.items():
            point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            point.field(field_key, field_value)
        point.time(timestamp, WritePrecision.S)  # Use seconds precision
    
        try:
            self.write_api.write(bucket=self.bucket, record=point)
        except Exception as e:
            logging.error(f"Failed to insert data into InfluxDB: {e}")

    def insert_cell_data(self, cell):
        """Inserts a row of Cell KPI data into the cell_metrics measurement."""
        current_ue_count = cell.update_ue_count()  # This method should return the current UE count
        total_throughput = cell.calculate_total_throughput()  # You need to implement this method in the Cell class
        cell_load = self.network_state.get_cell_load(cell)

        tags = {
            'cell_id': cell.ID,
            'gnodeb_id': cell.gNodeB_ID
        }
        fields = {
            'max_connect_ues': cell.MaxConnectedUEs,
            'current_ue_count': current_ue_count,
            'total_throughput': total_throughput,
            'cell_load': cell_load  # Add the cell load to the fields
        }
        timestamp = time.time_ns()  # Current time in nanoseconds

        self.insert_data('cell_metrics', tags, fields, timestamp)

            
    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

