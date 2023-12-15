# database_manager.py, this file located in database folder
import os
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, WritePrecision, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point, WritePrecision
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
    #Modify the insert_data method to handle Point objects directly
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
                timestamp = timestamp if timestamp is not None else int(datetime.utcnow().timestamp())  # Current time in seconds
                point = Point(measurement)
                for tag_key, tag_value in (tags or {}).items():
                    point.tag(tag_key, tag_value)
                for field_key, field_value in (fields or {}).items():
                    point.field(field_key, field_value)
                point.time(timestamp, WritePrecision.S)  # Use seconds precision

            self.write_api.write(bucket=self.bucket, record=point)
            database_logger.info(f"Data inserted for measurement {point.measurement}")
        except Exception as e:
            database_logger.error(f"Failed to insert data into InfluxDB: {e}")
################################################################################################################################
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

    def insert_gnodeb_data(self, gnodeb):
        #"""Inserts a row of gNodeB KPI data into the gnodeb_metrics measurement."""
        # Assuming you have methods in the gNodeB class to get the required KPIs
        # You need to implement these methods in the gNodeB class
        total_ue_count = gnodeb.get_total_ue_count()
        total_throughput = gnodeb.get_total_throughput()
        operational_status = gnodeb.get_operational_status()  # This should return a boolean or a string

        tags = {
            'gnodeb_id': gnodeb.ID
        # Add other tags if needed
        }
        fields = {
            'total_ue_count': total_ue_count,
            'total_throughput': total_throughput,
            'operational_status': operational_status
        # Add other fields if needed
        }
        timestamp = time.time_ns()  # Current time in nanoseconds

        self.insert_data('gnodeb_metrics', tags, fields, timestamp)

    def insert_ue_data(self, ue):
        """Inserts a row of UE KPI data into the ue_metrics measurement."""
        # Directly access the attributes from the UE instance
        traffic_volume = ue.traffic_volume  # Assuming traffic_volume is an attribute of UE
        service_type = ue.ServiceType  # Assuming ServiceType is an attribute of UE
        timestamp = int(time.time() * 1e9)  # Current time in nanoseconds

        # Add a debug log to check the timestamp value
        logging.debug(f"Generated timestamp for UE data: {timestamp}")

        # Determine the connection status
        connection_status = 'connected' if ue.ConnectedCellID else 'disconnected'

        # Prepare tags and fields for InfluxDB
        tags = {
            'ue_id': ue.ID,
            'imei': ue.IMEI
            # Add other tags if needed
        }
        fields = {
            'traffic_volume': traffic_volume,
            'service_type': service_type,
            'connection_status': connection_status
            # Add other fields if needed
        }

        # Create a Point object for InfluxDB
        point = Point("ue_metrics")\
            .tag(tags)\
            .field(fields)\
            .time(timestamp, WritePrecision.NS)

        # Insert the data into InfluxDB
        try:
            self.write_api.write(bucket=self.bucket, record=point)
            logging.info("UE data inserted into InfluxDB")
        except Exception as e:
            logging.error(f"Failed to insert UE data into InfluxDB: {e}")

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

