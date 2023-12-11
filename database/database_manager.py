# database_manager.py, this file located in database folder
import os
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, WritePrecision, Point  
from influxdb_client.client.write_api import SYNCHRONOUS
from traffic.network_metrics import calculate_gnodeb_throughput
from network.network_state import NetworkState

# Read from environment variables or use default values
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your-default-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

class DatabaseManager:
    
    def check_database_connection(self):
        """Checks if the database is connected."""
        try:
            is_alive = self.client.ping()
            if is_alive:
                print("Database connection is alive.")
                return True
            else:
                print("Database connection is not alive.")
                return False
        except Exception as e:
            print(f"An error occurred while checking the database connection: {e}")
            return False
        
    def __init__(self):
        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = INFLUXDB_BUCKET
        # Create an instance of NetworkState or pass it as a parameter to the DatabaseManager
        self.network_state = NetworkState()

    def insert_data(self, measurement, tags, fields, timestamp):
        """Inserts data into InfluxDB."""
        point = Point(measurement)
        for tag_key, tag_value in tags.items():
            point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            point.field(field_key, field_value)
        point.time(timestamp, WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=point)
    
    def insert_data_batch(self, points):
        """Inserts a batch of data points into InfluxDB."""
        self.write_api.write(bucket=self.bucket, record=points)
        
    def insert_ue_static_data(self, data):
        """Inserts static UE data into the ue_static measurement."""
        tags = {'ue_id': data.pop('ue_id')}  # Extract 'ue_id' as a tag
        # Ensure the additional fields are included in the 'data' dictionary
        # Convert 'mimo' to string if it's not already one
        mimo_value = str(data['mimo']) if 'mimo' in data else 'unknown'
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
        tags = {key: data.pop(key, None) for key in ['ue_id', 'imsi']}  # Provide a default value of None if 'imsi' is not present
        tags = {k: v for k, v in tags.items() if v is not None}  # Remove any tags that have a value of None
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

    def insert_cell_data(self, cell):
        """Inserts a row of Cell KPI data into the cell_metrics measurement."""
        # Assuming 'cell' is an instance of the Cell class and has the necessary methods
        current_ue_count = cell.update_ue_count()  # This method should return the current UE count
        total_throughput = cell.calculate_total_throughput()  # You need to implement this method in the Cell class
        cell_load = self.network_state.get_cell_load(cell)

        # Retrieve the cell load using the get_cell_load method from network_state.py
        # Assuming you have an instance of NetworkState available here as `network_state`
        cell_load = network_state.get_cell_load(cell)

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

        # Assuming insert_data is a method in this class that handles the database insertion
        self.insert_data('cell_metrics', tags, fields, timestamp)

    def insert_cell_static_data(self, data):

        """Inserts static gNodeB data into the gnodeb_static measurement."""
        point = Point("cell_static") \
        .tag("cell_id", data.pop('ID')) \
        .time(time.time_ns(), WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=point)


    def insert_gnodeb_data(self, gnodeb, gnodebs):
        """Inserts a row of gNodeB KPI data into the gnodeb_metrics measurement."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gnodeb_id = gnodeb.ID
        region = gnodeb.Region
        maxUEs = gnodeb.MaxUEs
        cell_count = gnodeb.CellCount
        current_ue_count = len(gnodeb.all_ues())
        gnodeb_throughput = calculate_gnodeb_throughput(gnodeb, gnodebs)

        tags = {
            'gnodeb_id': gnodeb_id,
            'region': region
        }
        fields = {
            'timestamp': timestamp,
            'maxUEs': maxUEs,
            'cell_count': cell_count,
            'current_ue_count': current_ue_count,
            'gnodeb_throughput': gnodeb_throughput
        }

        self.insert_data('gnodeb_metrics', tags, fields, time.time_ns())
    
    def insert_network_level_measurement(self, timestamp, region, count_gnodebs, count_ues, network_latency):
        """Inserts network level KPIs into the network_metrics measurement."""
        tags = {
            'region': region
        }
        fields = {
            'count_gnodebs': count_gnodebs,
            'count_ues': count_ues,
            'network_latency': network_latency
        }
        self.insert_data('network_metrics', tags, fields, timestamp)
        
    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

