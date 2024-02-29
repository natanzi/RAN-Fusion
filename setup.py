import subprocess
import sys
from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv

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
    influxdb_log_bucket = "RAN_logs" 

    if not influxdb_token:
        print("No API Token provided. Exiting setup.")
        sys.exit(1)

    # Configure InfluxDB buckets
    configure_influxdb_bucket(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)
    configure_influxdb_bucket(influxdb_url, influxdb_token, influxdb_org, influxdb_log_bucket)  # For logs

    # Write configuration to .env file
    write_env_file(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, influxdb_log_bucket)

    # Load environment variables immediately after writing to .env to ensure they are available
    load_env_variables()

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
        client.close()

def write_env_file(url, token, org, bucket, log_bucket):
    """Writes the InfluxDB configuration to a .env file."""
    try:
        with open('.env', 'w') as env_file:
            env_file.write(f"INFLUXDB_URL={url}\n")
            env_file.write(f"INFLUXDB_TOKEN={token}\n")
            env_file.write(f"INFLUXDB_ORG={org}\n")
            env_file.write(f"INFLUXDB_BUCKET={bucket}\n")
            env_file.write(f"INFLUXDB_LOG_BUCKET={log_bucket}\n")  # Include the log bucket
        print("InfluxDB configuration written to .env file.")
    except IOError as e:
        print(f"Error writing to .env file: {e}")

def load_env_variables():
    """Load environment variables from the .env file."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    print("Environment variables loaded from .env file.")

def check_env_variables():
    """Check if necessary environment variables are set."""
    required_vars = ['INFLUXDB_URL', 'INFLUXDB_TOKEN', 'INFLUXDB_ORG', 'INFLUXDB_BUCKET', 'INFLUXDB_LOG_BUCKET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("The following required environment variables are missing:", ', '.join(missing_vars))
        sys.exit(1)
    else:
        print("All required environment variables are set.")

if __name__ == "__main__":
    print("Setting up the environment...")
    install_requirements()
    check_influxdb_installation()
    setup_influxdb_config()
    check_env_variables()  # Check if all required environment variables are set
    print("Setup completed successfully. Now you can run the main application.")
