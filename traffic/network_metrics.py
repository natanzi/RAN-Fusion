#network_metrics.py
# network_metrics.py is in traffic directory
from math import radians, cos, sin, asin, sqrt
from utils.location_utils import calculate_distance_cached
import time
from database.database_manager import DatabaseManager
from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions

# Haversine formula to calculate the great-circle distance between two points
def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

# Calculate the signal strength between a UE and a gNodeB
def calculate_signal_strength(ue, gNodeB):
    # Calculate the distance between the UE and the gNodeB using the cached function
    distance_to_gNodeB = calculate_distance_cached(ue.Latitude, ue.Longitude, gNodeB.Latitude, gNodeB.Longitude)
    
    # Adjust the signal strength calculation to return a value between 0 and 100
    # The signal strength is 100 at the gNodeB and decreases linearly to 0 at the edge of the coverage radius
    signal_strength = max(0, 100 * (1 - (distance_to_gNodeB / gNodeB.CoverageRadius)))
    
    return signal_strength
#################################################################################################
################################################################################################
def find_cell_by_id(cell_id, gnodebs):
    # Iterate over all gNodeBs to find the cell with the given ID
    for gnodeb in gnodebs:
        for cell in gnodeb.Cells:
            if cell.ID == cell_id:
                return cell
    return None
################################################################################################
# Calculate the throughput for a UE based on traffic generation and network quality metrics
def calculate_and_write_ue_throughput(ue, network_load_impact, jitter, packet_loss, delay, interval=1):
    # Create an instance of DatabaseManager
    database_manager = DatabaseManager()

    # Calculate the base throughput in bytes per second
    base_throughput = ue.data_size / ue.interval

    # Adjust the throughput based on network load impact, jitter, packet loss, and delay
    # Assuming these are values between 0 and 1, where 1 represents the worst case
    quality_impact = (1 - jitter) * (1 - packet_loss) * (1 - delay)
    adjusted_throughput = base_throughput * (1 - network_load_impact) * quality_impact

    # Prepare the data to be written to InfluxDB
    data = {
        "measurement": "ue_throughput",
        "tags": {
            "ue_id": ue.id
        },
        "fields": {
            "throughput": adjusted_throughput,
            "jitter": jitter,
            "packet_loss": packet_loss,
            "delay": delay
        },
        "time": datetime.utcnow().isoformat()
    }

    # Write the data to InfluxDB
    database_manager.insert_data(data)

    # Close the database connection
    database_manager.close_connection()

    return adjusted_throughput
