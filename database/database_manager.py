# database_manager.py in database directory
from influxdb import InfluxDBClient

class DatabaseManager:
    def __init__(self, host='localhost', port=8086, username='root', password='root', dbname='RAN_metrics'):
        self.client = InfluxDBClient(host, port, username, password, dbname)
        self.dbname = dbname

    def connect(self):
        """Establishes a database connection."""
        self.client.create_database(self.dbname)

    def create_tables(self):
        # In InfluxDB, "tables" are structured as "measurements"
        # No need to create them explicitly as they are created on data insertion
        pass

    def insert_ue_static_data(self, data):
        """Inserts static UE data into the ue_static measurement."""
        json_body = [
            {
                "measurement": "ue_static",
                "tags": {
                    "ue_id": data['ue_id'],
                },
                "fields": {
                    "imei": data['imei'],
                    "service_type": data['service_type'],
                    # Add other static fields here
                }
            }
        ]
        self.client.write_points(json_body)

    def insert_ue_data(self, data):
        """Inserts a row of UE KPI data into the ue_metrics measurement."""
        json_body = [
            {
                "measurement": "ue_metrics",
                "tags": {
                    "ue_id": data['ue_id'],
                    "imsi": data['imsi']
                },
                "fields": {
                    "latency": data['latency'],
                    "throughput": data['throughput'],
                    "congestion_status": data['congestion_status']
                },
                "time": data['timestamp']
            }
        ]
        self.client.write_points(json_body)

    def insert_gnodeb_data(self, data):
        """Inserts a row of gNodeB KPI data into the gnodeb_metrics measurement."""
        json_body = [
            {
                "measurement": "gnodeb_metrics",
                "tags": {
                    "gnodeb_id": data['gnodeb_id'],
                    "imsi": data['imsi']
                },
                "fields": {
                    "latency": data['latency'],
                    "throughput": data['throughput'],
                    "congestion_status": data['congestion_status']
                },
                "time": data['timestamp']
            }
        ]
        self.client.write_points(json_body)

    def insert_cell_data(self, data):
        """Inserts a row of Cell KPI data into the cell_metrics measurement."""
        json_body = [
            {
                "measurement": "cell_metrics",
                "tags": {
                    "cell_id": data['cell_id'],
                    "imsi": data['imsi']
                },
                "fields": {
                    "latency": data['latency'],
                    "throughput": data['throughput'],
                    "congestion_status": data['congestion_status']
                },
                "time": data['timestamp']
            }
        ]
        self.client.write_points(json_body)

    def commit_changes(self):
        # InfluxDB writes data immediately, so no need for commit
        pass

    def close_connection(self):
        """Closes the database connection."""
        self.client.close()

# Example usage:
# db_manager = DatabaseManager()
# db_manager.connect()
# db_manager.insert_ue_static_data({
#     'ue_id': "ue_123",
#     'imei': "990000862471854",
#     'service_type': "4G"
# })
# db_manager.insert_ue_data({
#     'timestamp': "2023-04-01T00:00:00Z",
#     'ue_id': "ue_123",
#     'imsi': "123456789012345",
#     'latency': 10.5,
#     'throughput': 1000,
#     'congestion_status': False
# })