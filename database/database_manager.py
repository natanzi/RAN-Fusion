# database_manager.py, this file located in database folder
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time
import sys

print(sys.path)

class DatabaseManager:
    def __init__(self, url='http://localhost:8086', bucket='RAN_metrics'):
        token = os.getenv('WnPp64q1nyPtp7kSRkTmKW8TNTaG--604-ZYdnt5ld1wwxi4Xu3wbb-jv_1bNCqDadLuvWIWwJNvTYTrdebjrw==')  # Ensure the INFLUXDB_TOKEN environment variable is set
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
        tags = {'ue_id': data.pop('ue_id')}  # Extract 'ue_id' as a tag
        # Ensure the additional fields are included in the 'data' dictionary
        fields = {
            "imei": data['imei'],
            "service_type": data['service_type'],
            "model": data['model'],
            "rat": data['rat'],
            "max_bandwidth": data['max_bandwidth'],
            "duplex_mode": data['duplex_mode'],
            "tx_power": data['tx_power'],
            "modulation": data['modulation'],
            "coding": data['coding'],
            "mimo": data['mimo'],
            "processing": data['processing'],
            "bandwidth_parts": data['bandwidth_parts'],
            "channel_model": data['channel_model'],
            "velocity": data['velocity'],
            "direction": data['direction'],
            "traffic_model": data['traffic_model'],
            "scheduling_requests": data['scheduling_requests'],
            "rlc_mode": data['rlc_mode'],
            "snr_thresholds": data['snr_thresholds'],
            "ho_margin": data['ho_margin'],
            "n310": data['n310'],
            "n311": data['n311'],
            # Additional static fields from UE class
            "screen_size": data['screen_size'],
            "battery_level": data['battery_level']
        }
        data.update(fields)
        self.insert_data('ue_static', tags, data, time.time_ns())

    def insert_ue_data(self, data):
        """Inserts a row of UE KPI data into the ue_metrics measurement."""
        tags = {key: data.pop(key) for key in ['ue_id', 'imsi']}
        self.insert_data('ue_metrics', tags, data, time.time_ns())

    def insert_cell_static_data(self, data):
        """Inserts static cell data into the cell_static measurement."""
        json_body = [
            {
                "measurement": "cell_static",
                "tags": {
                    "cell_id": data.pop('cell_id'),  # Extract 'cell_id' as a tag using pop
                },
                "fields": {
                    "pci": data['pci'],
                    "tac": data['tac'],
                    "frequency": data['frequency'],
                    "bandwidth": data['bandwidth'],
                    "power": data['power'],
                    "cell_range": data['cell_range'],
                    "mcc": data['mcc'],
                    "mnc": data['mnc'],
                    "technology": data['technology'],
                    # ... add other static cell parameters here
                },
                "time": time.time_ns()  # Add the current time in nanoseconds
            }
        ]
        self.client.write_points(json_body)

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

