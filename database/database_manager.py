# database_manager.py, this file located in database folder
import os
import time

from influxdb_client import InfluxDBClient, WritePrecision, Point  
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "aZPFioFZQE_kNcXy5E7JLhaX0x4RaK0RG14xEgWIieGtuX8_xB2f783mRjn3Vj04y7iuMME-VRfB-HlbRt_iVw==" 
INFLUXDB_ORG = "ranfusion"
INFLUXDB_BUCKET = "RAN_metrics"

class DatabaseManager:

    def __init__(self):
        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        
        self.write_api = self.client.write_api(
            write_options=SYNCHRONOUS
        )  

        self.bucket = INFLUXDB_BUCKET

    def write_point(self, point):
        self.write_api.write(
            bucket=self.bucket, 
            org=INFLUXDB_ORG,
            record=point
        )

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
                    "cell_id": data.pop('ID'),  # Keep only cell_id in tags
                },
                "fields": {
                # No fields are included
                },
                "time": time.time_ns()  # Add the current time in nanoseconds
            }
        ]
        self.client.write_points(json_body)

    def insert_cell_data(self, data):
        """Inserts a row of Cell KPI data into the cell_metrics measurement."""
        tags = {key: data.pop(key) for key in ['cell_id', 'imsi']}
        self.insert_data('cell_metrics', tags, data, time.time_ns())

    def insert_cell_static_data(self, data):

        """Inserts static gNodeB data into the gnodeb_static measurement."""
        point = Point("cell_static") \
        .tag("cell_id", data.pop('ID')) \
        .time(time.time_ns(), WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=point)


    def insert_gnodeb_data(self, data):
        """Inserts a row of gNodeB KPI data into the gnodeb_metrics measurement."""
        tags = {key: data.pop(key) for key in ['gnodeb_id', 'imsi']}
        self.insert_data('gnodeb_metrics', tags, data, time.time_ns())

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

