from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time

class DatabaseManager:
    def __init__(self, url='http://localhost:8086', bucket='RAN_metrics'):
        token = os.getenv('INFLUXDB_TOKEN')  # Ensure the INFLUXDB_TOKEN environment variable is set
        org = "ranfusion"
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket

    def insert_data(self, measurement, tags, fields, timestamp):
        """Inserts data into InfluxDB."""
        point = Point(measurement)
        for tag_key, tag_value in tags.items():
            point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            point.field(field_key, field_value)
        point.time(timestamp, WritePrecision.NS)

        self.write_api.write(bucket=self.bucket, record=point)

    def insert_ue_static_data(self, data):
        """Inserts static UE data into the ue_static measurement."""
        tags = {'ue_id': data.pop('ue_id')}  # Changed to pop for consistency
        self.insert_data('ue_static', tags, data, time.time_ns())

    def insert_ue_data(self, data):
        """Inserts a row of UE KPI data into the ue_metrics measurement."""
        tags = {key: data.pop(key) for key in ['ue_id', 'imsi']}
        self.insert_data('ue_metrics', tags, data, time.time_ns())

    def insert_cell_static_data(self, data):
        """Inserts static cell data into the cell_static measurement."""
        tags = {'cell_id': data.pop('cell_id')}  # Using pop for consistency
        self.insert_data('cell_static', tags, data, time.time_ns())

    def insert_cell_data(self, data):
        """Inserts a row of Cell KPI data into the cell_metrics measurement."""
        tags = {key: data.pop(key) for key in ['cell_id', 'imsi']}
        self.insert_data('cell_metrics', tags, data, time.time_ns())

    def insert_gnodeb_static_data(self, data):
        """Inserts static gNodeB data into the gnodeb_static measurement."""
        tags = {'gnodeb_id': data.pop('gnodeb_id')}  # Using pop for consistency
        self.insert_data('gnodeb_static', tags, data, time.time_ns())

    def insert_gnodeb_data(self, data):
        """Inserts a row of gNodeB KPI data into the gnodeb_metrics measurement."""
        tags = {key: data.pop(key) for key in ['gnodeb_id', 'imsi']}
        self.insert_data('gnodeb_metrics', tags, data, time.time_ns())

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()
