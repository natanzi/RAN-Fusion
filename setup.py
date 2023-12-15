import os
import subprocess
import sys
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

def install_requirements():
    """Install required packages from requirements.txt."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_influxdb_installation():
    """Check if InfluxDB Python client is installed."""
    try:
        import influxdb_client
    except ImportError:
        print("InfluxDB Python client is not installed. Please install it to continue.")
        sys.exit(1)

def setup_influxdb_config():
    """Prompt for the InfluxDB API token and set up configuration."""
    print("Please enter your InfluxDB API Token:")
    influxdb_token = input("API Token: ").strip()
    influxdb_url = "http://localhost:8086"
    influxdb_org = "ranfusion"
    influxdb_bucket = "RAN_metrics"

    if not influxdb_token:
        print("No API Token provided. Exiting setup.")
        sys.exit(1)

    # Configure InfluxDB bucket
    configure_influxdb_bucket(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)
    
    # Write configuration to .env file
    write_env_file(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)

def configure_influxdb_bucket(url, token, org, bucket_name):
    """Configures the InfluxDB bucket."""
    client = InfluxDBClient(url=url, token=token, org=org)
    
    try:
        bucket_api = client.buckets_api()
        buckets = bucket_api.find_buckets().buckets
        if not any(bucket.name == bucket_name for bucket in buckets):
            bucket = bucket_api.create_bucket(bucket_name=bucket_name, org=org)
            print(f"Bucket '{bucket_name}' created.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except Exception as e:
        print(f"An error occurred while setting up the bucket: {e}")
        sys.exit(1)
    finally:
        # Write configuration to .env file for the first bucket
        write_env_file(url, token, org, bucket_name)

def write_env_file(url, token, org, bucket):
    """Writes the InfluxDB configuration to a .env file."""
    try:
        with open('.env', 'w') as env_file:
            env_file.write(f"INFLUXDB_URL={url}\n")
            env_file.write(f"INFLUXDB_TOKEN={token}\n")
            env_file.write(f"INFLUXDB_ORG={org}\n")
            env_file.write(f"INFLUXDB_BUCKET={bucket}\n")
            # If you want to include the log bucket, you can add it here
            # env_file.write(f"INFLUXDB_LOG_BUCKET={influxdb_log_bucket}\n")
        print("InfluxDB configuration written to .env file.")
    except IOError as e:
        print(f"Error writing to .env file: {e}")

if __name__ == "__main__":
    print("Setting up the 5G Simulator...")
    install_requirements()
    check_influxdb_installation()
    setup_influxdb_config()
    print("Setup completed successfully, Now you can run the main.py")