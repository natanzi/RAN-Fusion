#bucket_operations.py inside the database folder
from influxdb_client import InfluxDBClient, BucketsApi

# Define your InfluxDB credentials and details
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "Z2HLqLWYr45rTCdTA3QgjMSMA6Nw8YZuDxgDEfYZyRjqmJ8ZOKjdURP9ke__3JZjv8g8DIjV05PyqItC6cIF1Q==" 
INFLUXDB_ORG = "ranfusion"

def create_bucket(bucket_name):
    """Create a bucket in InfluxDB."""
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    buckets_api = BucketsApi(client)
    
    # Check if the bucket already exists
    bucket_exists = any(bucket.name == bucket_name for bucket in buckets_api.find_buckets().buckets)
    
    if not bucket_exists:
        # Create the bucket if it does not exist
        bucket = buckets_api.create_bucket(bucket_name=bucket_name, org=INFLUXDB_ORG)
        print(f"Bucket '{bucket_name}' created successfully.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")
    
    # Close the client connection
    client.close()