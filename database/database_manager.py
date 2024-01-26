#This is database manager class database_manager.py located in datbase folder
import os
from influxdb_client import InfluxDBClient, WritePrecision, Point, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from logs.logger_config import database_logger  # Import the configured logger
from datetime import datetime

# Read from environment variables or use default values
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your-default-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

class DatabaseManager:

    def __init__(self):
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = INFLUXDB_BUCKET

    def test_connection(self):
        """Test if the connection to the database is successful."""
        try:
            self.client.ping()
            database_logger.info("Database connection successful.")
            return True
        except Exception as e:
            database_logger.error(f"Database connection test failed: {e}")
            return False

    def insert_data_batch(self, points):
        """Inserts a batch of Point objects into InfluxDB."""
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            #database_logger.info("Batch data inserted into InfluxDB")
        except Exception as e:
            database_logger.error(f"Failed to insert batch data into InfluxDB: {e}")

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
                point = Point(measurement)
                for tag_key, tag_value in (tags or {}).items():
                    point.tag(tag_key, tag_value)
                for field_key, field_value in (fields or {}).items():
                    point.field(field_key, field_value)
                # Convert the timestamp to the correct format for InfluxDB
                point.time(timestamp, WritePrecision.NS)

            self.write_api.write(bucket=self.bucket, record=point)
            # Log the measurement and the tags for context
            tags_description = ", ".join([f"{k}={v}" for k, v in point._tags.items()])
            #database_logger.info(f"Data inserted for measurement {point._name} with tags {tags_description}")

        except Exception as e:
            database_logger.error(f"Failed to insert data into InfluxDB: {e}")

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

    def get_all_ue_ids(self):
        """Retrieves all UE IDs from InfluxDB."""
        try:
            query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "ue_metrics") |> keep(columns: ["ue_id"])'
            result = self.query_api.query(query=query, org=INFLUXDB_ORG)
            ue_ids = [record.get_value() for table in result for record in table.records]
            return ue_ids
        except Exception as e:
            database_logger.error(f"Failed to retrieve UE IDs from InfluxDB: {e}")
            return []

    def insert_log(self, log_point):
        """Inserts log data into the logs bucket in InfluxDB."""
        log_bucket = 'RAN_logs'
        try:
            self.write_api.write(bucket=log_bucket, record=log_point)
            database_logger.info(f"Log data inserted into bucket {log_bucket}")
        except Exception as e:
            database_logger.error(f"Failed to insert log data into InfluxDB: {e}")

    def update_ue_association(self, ue, new_cell_id):
        """
        Updates the association of a UE with a new cell in the database.

        :param ue: The UE object to update.
        :param new_cell_id: The ID of the new cell to associate the UE with.
        """
        try:
            # Assuming 'ue' is an object with an attribute 'ue_id'
            # and 'new_cell_id' is the ID of the cell to associate the UE with.
            # You will need to replace 'ue_table' with the actual table name
            # and column names with the actual column names in your database.
            query = f"UPDATE ue_table SET cell_id = {new_cell_id} WHERE ue_id = {ue.ue_id}"
            self.cursor.execute(query)
            self.connection.commit()
            database_logger.info(f"UE {ue.ue_id} association updated to cell {new_cell_id}")
        except Exception as e:
            database_logger.error(f"Failed to update UE association in the database: {e}")
            raise