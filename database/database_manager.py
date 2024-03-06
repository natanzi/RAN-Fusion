#########################################################################################################
# This is database manager class "database_manager.py" located in datbase folderThe DatabaseManager     #
# class is responsible for managing all interactions with the InfluxDB database. It provides methods    #
# for inserting, querying, and deleting data related to the network simulation, including metrics for   #
# sectors, cells, UEs (User Equipments), and network performance. This class implements the Singleton   #
# design pattern to ensure that only one instance of the database connection is created and used        #
# throughout the application.                                                                           #
#########################################################################################################
import os
from influxdb_client import InfluxDBClient, WritePrecision, Point, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from logs.logger_config import database_logger  # Import the configured logger
from datetime import datetime
from influxdb_client import Point
import json

# Read from environment variables or use default values
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is not set.")
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

class DatabaseManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            # Initialize the instance here if needed, similar to what's done in __new__
            cls._instance.client_init()
        return cls._instance
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            # Initialize the instance (the part of __init__)
            cls._instance.client_init()
        return cls._instance

    def client_init(self):
        # This method replaces the original __init__ content
        print(f"InfluxDB token: {INFLUXDB_TOKEN}")  # Print the InfluxDB token for test
        print(f"Connecting to InfluxDB with URL: {INFLUXDB_URL}, Token: {INFLUXDB_TOKEN}, Org: {INFLUXDB_ORG}")
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = INFLUXDB_BUCKET
    
##################################################################################################################################
    def get_sector_by_id(self, sector_id):
        query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "sector_metrics" and r.sector_id == "{sector_id}")'
        result = self.query_api.query(query=query)
        for table in result:
            for record in table.records:
                if record.values.get('sector_id') == sector_id:
                    return record.values  # Adjust based on what you need
        return None
################################################################################################################################
    def insert_sector_state(self, sector):
        """Inserts the state of a sector into InfluxDB."""
        point = sector.serialize_for_influxdb()  # Assuming serialize_for_influxdb() prepares the data correctly
        self.insert_data(point)
##################################################################################################################################
    def get_sectors(self):
        try:
            query = f'from(bucket:"{self.bucket}") |> range(start: -30d) |> filter(fn:(r) => r._measurement == "sectors")'
            result = self.query_api.query(query=query)
            sectors = []
            for table in result:
                for record in table.records:
                    sector_data = json.loads(record.get_value())
                    sectors.append(sector_data)
            return sectors
        except Exception as e:
            print(f"Failed to retrieve sectors: {e}")
            return []
##################################################################################################################################
    def remove_ue_state(self, ue_id, sector_id):
        """
        Removes the state of a UE from InfluxDB within the last 24 hours.
        
        :param ue_id: The ID of the UE to remove.
        :param sector_id: The ID of the sector associated with the UE.
        """
        # Define the time range for deletion. Here, we use 24 hours as an example.
        start_time = "now() - 24h"
        stop_time = "now()"
        
        # Construct the delete predicate function
        predicate = f'_measurement="ue_metrics" AND ue_id="{ue_id}" AND sector_id="{sector_id}"'
        
        try:
            # Perform the deletion
            self.client.delete_api().delete(start_time, stop_time, predicate, bucket=self.bucket, org=INFLUXDB_ORG)
            database_logger.info(f"Successfully removed state for UE {ue_id} in sector {sector_id}.")
        except Exception as e:
            database_logger.error(f"Failed to remove state for UE {ue_id} in sector {sector_id}: {e}")
##################################################################################################################################
    def test_connection(self):
        """Test if the connection to the database is successful."""
        try:
            self.client.ping()
            database_logger.info("Database connection successful.")
            return True
        except Exception as e:
            database_logger.error(f"Database connection test failed: {e}")
            return False
##################################################################################################################################
    def insert_data_batch(self, points):
        """Inserts a batch of Point objects into InfluxDB."""
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            #database_logger.info("Batch data inserted into InfluxDB")
        except Exception as e:
            database_logger.error(f"Failed to insert batch data into InfluxDB: {e}")
##################################################################################################################################
    # def insert_data(self, measurement_or_point, tags=None, fields=None, timestamp=None):
    #     print('------------------inside insert -------------------')
    #     print('measurement_or_point:', measurement_or_point)
    #     """Inserts data into InfluxDB. Can handle both Point objects and separate parameters."""
    #     try:
    #         if isinstance(measurement_or_point, Point):
    #             print('-----we are in first try if insert_data-----------')
    #             # If a Point object is provided
    #             point = measurement_or_point
    #             if timestamp:
    #                 point.time(timestamp)
    #         else:
    #             # If separate parameters are provided
    #             print('-----we are in first try else insert_data-----------')
    #             measurement = measurement_or_point
    #             point = Point(measurement)
    #             for tag_key, tag_value in (tags or {}).items():
    #                 point.tag(tag_key, tag_value)
    #             for field_key, field_value in (fields or {}).items():
    #                 point.field(field_key, field_value)
    #             # Convert the timestamp to the correct format for InfluxDB
    #             point.time(timestamp, WritePrecision.S)

    #         self.write_api.write(bucket=self.bucket, record=point)
    #         print('write is done')
    #         # Log the measurement and the tags for context
    #         tags_description = ", ".join([f"{k}={v}" for k, v in point._tags.items()])
    #         #database_logger.info(f"Data inserted for measurement {point._name} with tags {tags_description}")

    #     except Exception as e:
    #         database_logger.error(f"Failed to insert data into InfluxDB: {e}")
    def insert_data(self, measurement_or_point, tags=None, fields=None, timestamp=None):
        #print('------------------inside insert -------------------')
        """Inserts or updates data into InfluxDB. Can handle both Point objects and separate parameters."""
        try:
            if isinstance(measurement_or_point, Point):
                point = measurement_or_point
                # For debugging: print throughput if it's a field in the Point object
                if 'throughput' in point._fields:
                    throughput_value = point._fields['throughput']
                    #print(f"Throughput (Point object): {throughput_value}, Type: {type(throughput_value)}")
            else:
                # If separate parameters are provided, create a new Point
                measurement = measurement_or_point
                point = Point(measurement)
                # For debugging: specifically check and print throughput and its type
                if fields and 'throughput' in fields:
                    throughput_value = fields['throughput']
                    #print(f"Throughput (field): {throughput_value}, Type: {type(throughput_value)}")
                # Add tags and fields to the Point
                for tag_key, tag_value in (tags or {}).items():
                    point.tag(tag_key, tag_value)
                for field_key, field_value in (fields or {}).items():
                    point.field(field_key, field_value)
                # Use the provided timestamp or the current time
                if timestamp is None:
                    timestamp = datetime.utcnow()
                point.time(timestamp, WritePrecision.S)
            
            # Write the point to the database
            self.write_api.write(bucket=self.bucket, record=point)
            #print('Data write is done')

        except Exception as e:
            print(f"Failed to insert data into InfluxDB: {e}")

##################################################################################################################################
    def close_connection(self):
        """Closes the database connection."""
        self.client.close()
##################################################################################################################################
    def get_all_ue_ids(self):
        """Retrieves all UE IDs from InfluxDB."""
        try:
            query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "ue_metrics")'
            result = self.query_api.query(query=query, org=INFLUXDB_ORG)
            ue_ids = []
            for table in result:
                for record in table.records:
                    if 'ue_id' in record.values:
                        ue_ids.append(record.values['ue_id'])
        except Exception as e:
            database_logger.error(f"Failed to retrieve UE IDs from InfluxDB: {e}")
            return []  # Return an empty list in case of any exception
        return ue_ids
##################################################################################################################################
    def insert_log(self, log_point):
        """Inserts log data into the logs bucket in InfluxDB."""
        log_bucket = 'RAN_logs'
        try:
            self.write_api.write(bucket=log_bucket, record=log_point)
            database_logger.info(f"Log data inserted into bucket {log_bucket}")
        except Exception as e:
            database_logger.error(f"Failed to insert log data into InfluxDB: {e}")
##################################################################################################################################
    def update_ue_association(self, ue_id, new_cell_id):
        """
        Updates the association of a UE with a new cell in the database by writing a new point.
        :param ue_id: The ID of the UE to update.
        :param new_cell_id: The ID of the new cell to associate the UE with.
        """
        try:
            # Create a new Point with the measurement name you're using for UEs
            point = Point("ue_metrics")\
                .tag("ue_id", str(ue_id))\
                .tag("connected_cell_id", str(new_cell_id)) \
                .field("update_type", "cell_association_change")\
                .time(datetime.utcnow())
            # Write the point to InfluxDB
            self.write_api.write(bucket=self.bucket, record=point)
            database_logger.info(f"UE {ue_id} association updated to cell {new_cell_id}")
        except Exception as e:
            database_logger.error(f"Failed to update UE association in the database: {e}")
            raise
##################################################################################################################################
    def write_sector_load(self, sector_id, load):
        point = Point("sector_metrics") \
            .tag("sector_id", sector_id) \
            .field("sector_load", load) \
            .time(datetime.utcnow(), WritePrecision.S)
        self.write_api.write(bucket=self.bucket, record=point)

    def write_cell_load(self, cell_id, load):
        point = Point("cell_metrics") \
            .tag("cell_id", cell_id) \
            .field("cell_load", load) \
            .time(datetime.utcnow(), WritePrecision.S)
        self.write_api.write(bucket=self.bucket, record=point)

###################################################################################################################################
    def write_network_measurement(self, network_load, network_delay, total_handover_success_count, total_handover_failure_count):
        point = Point("network_metrics") \
            .field("load", float(network_load)) \
            .field("delay", float(network_delay)) \
            .field("total_handover_success_count", int(total_handover_success_count)) \
            .field("total_handover_failure_count", int(total_handover_failure_count)) \
            .time(datetime.utcnow(), WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=point)
##################################################################################################################################
    # def get_ue_metrics(self, ue_id):
    #     print('----DB Manager----ue_id:', ue_id)
    #     print('----DB Manager----self.bucket:', self.bucket)
    #     query = f'''
    #         from(bucket: "{self.bucket}")
    #             |> range(start: -1d)
    #             |> filter(fn: (r) => r._measurement == "ue_metrics" and r.ue_id == "ue_id")
    #             |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    #             |> last()
    #     '''
    #     result = self.query_api.query(query=query)
    #     print('result:', result)
    #     metrics = []
    #     for table in result:
    #         print('--------inside for loop DB Manager----table:', table)
    #         for record in table.records:
    #             print('----DB Manager-------record:', record)
    #             print('-------DB Manager-------throughput:', record.get_value())
    #             metrics.append({
    #                 'timestamp': record.get_time(),
    #                 'throughput': record.get_value(),
    #                 'jitter': record.values['jitter'],
    #                 'packet_loss': record.values['packet_loss'],
    #                 'delay': record.values['delay']
    #             })
    #     return metrics
    def get_ue_metrics(self, ue_id):
        #print('----DB Manager----ue_id:', ue_id)
        #print('----DB Manager----self.bucket:', self.bucket)
        #3query = f'''
            #from(bucket: "{self.bucket}")
            # |> range(start: -1d)
            # |> filter(fn: (r) => r._measurement == "ue_metrics" and r.ue_id == "{ue_id}")
            # |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            # |> last()
        query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -1d)
                |> filter(fn: (r) => r._measurement == "ue_metrics" and r.ue_id == "{ue_id}")
                // Check the output here to ensure fields are present
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                // Then check the output here to ensure the pivot is as expected
                '''
        result = self.query_api.query(query=query)
        #print('result:', result)
        metrics = []
        if result:
            for table in result:
                #print('--------inside for loop DB Manager----table:', table)
                for record in table.records:
                    #print('----DB Manager-------record:', record)
                    #print('--------------throughput:', record.values.get('throughput', None))
                    #print('-------------------time:', record.get_time())
                    # Ensure you are safely accessing fields, assuming 'throughput', 'jitter', 'packet_loss', 'delay' might not always be present
                    metrics.append({
                        'timestamp': record.get_time(),
                        'throughput': record.values.get('throughput', None),
                        'ue_jitter': record.values.get('jitter', None),
                        'ue_packet_loss_rate': record.values.get('packet_loss', None),
                        'ue_delay': record.values.get('delay', None)
                    })
        else:
            print("No results found for the query.")
        return metrics


##################################################################################################################################
    def get_sector_load(self, sector_id):
        # Flux query syntax for InfluxDB 2.x
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "sector" and r["sector_id"] == "{sector_id}")
            |> filter(fn: (r) => r["_field"] == "load")  # Assuming 'load' is a field in your data
        '''
        result = self.query_api.query(query=query)
        load_metrics = []
        for table in result:
            for record in table.records:
                # Adjust according to the structure of your data
                load_metrics.append({
                    'load': record.get_value(),
                    'time': record.get_time()
                })
        return load_metrics
##################################################################################################################################
    def flush_all_data(self):
        try:
            # No need to call connect_to_database() since self.client is already initialized
            bucket_to_clear = self.bucket  # Use the bucket name from the class attribute

            # Use delete_api to delete all data within the specified bucket
            delete_api = self.client.delete_api()
            start = "1970-01-01T00:00:00Z"  # Broadly covers the earliest possible data
            stop = "2099-01-01T00:00:00Z"   # Broadly covers up to far future data

            # Perform the deletion for the entire bucket content
            delete_api.delete(start=start, stop=stop, bucket=bucket_to_clear, org=self.org)

            print(f"All data in the bucket {bucket_to_clear} has been deleted.")
            return True  # Indicate success
        except Exception as e:
            print(f"Failed to delete data from bucket {bucket_to_clear}: {e}")
            return False  # Indicate failure