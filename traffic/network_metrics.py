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
def calculate_cell_load(cell_id, gnodebs):
    # Find the cell with the matching cell_id
    # the calculate_cell_load function is calculating the cell load by counting the number of connected UEs to a cell and comparing it to the maximum capacity of the cell.
    cell = find_cell_by_id(cell_id, gnodebs)
    
    if cell is None:
        raise ValueError(f"Cell with ID {cell_id} not found.")

    # Calculate the current load based on the number of connected UEs
    current_load = len(cell.ConnectedUEs)
    max_capacity = cell.MaxConnectedUEs
    
    # Calculate the load as a percentage
    load_percentage = (current_load / max_capacity) * 100 if max_capacity > 0 else 0
    return load_percentage

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
# To use this function, you would call it at regular intervals.
# For example, you could use a loop or a scheduling library to call this function every second:
#while True:
    #calculate_and_write_ue_throughput(ue, network_load_impact)
    #time.sleep(interval)
################################################################################################
# Calculate the total throughput for all UEs in a cell based on traffic generation
def calculate_cell_throughput(cell, gnodebs):
    total_throughput = 0
    network_load_impact = calculate_cell_load(cell.ID, gnodebs) / 100  # Convert percentage to a value between 0 and 1

    for ue in cell.assigned_UEs:
        # Calculate throughput for each UE based on traffic generation and quality metrics
        ue_throughput = calculate_ue_throughput(ue, network_load_impact)
        # Adjust the throughput based on the quality metrics
        ue_throughput *= (1 - cell.jitter - cell.packet_loss - cell.delay)
        total_throughput += ue_throughput

    return total_throughput
######################################################################################################
# Calculate the total throughput for all cells in a gNodeB
def calculate_gnodeb_throughput(gNodeB, gnodebs):
    total_throughput = 0
    for cell in gNodeB.Cells:
        cell_throughput = calculate_cell_throughput(cell, gnodebs)
        total_throughput += cell_throughput
    return total_throughput
#######################################################################################################
# Calculate latency for a UE as a function of signal strength, distance to gNodeB, and network load
def calculate_ue_latency(ue, gNodeB, gnodebs):
    signal_strength = calculate_signal_strength(ue, gNodeB)
    distance_to_gNodeB = calculate_distance_cached(ue.Latitude, ue.Longitude, gNodeB.Latitude, gNodeB.Longitude)
    network_load_impact = calculate_cell_load(ue.CellID, gnodebs)
    # Latency calculation can be a complex function involving these parameters
    # For simplicity, we'll assume it's a linear combination
    latency = (1 / signal_strength) + distance_to_gNodeB + network_load_impact
    return latency
######################################################################################################
# Calculate the overall network latency as an average of the latencies across all UEs
def calculate_overall_network_latency(gnodebs):
    total_latency = 0
    total_ues = 0
    for gNodeB in gnodebs:
        for cell in gNodeB.Cells:
            for ue in cell.assigned_UEs:
                ue_latency = calculate_ue_latency(ue, gNodeB, gnodebs)
                total_latency += ue_latency
                total_ues += 1
    return total_latency / total_ues if total_ues > 0 else 0
#####################################################################################################
def calculate_network_level_kpis(gnodebs):
    """
    Calculate network-level KPIs such as overall network latency, total throughput, and cell load.
    
    :param gnodebs: List of all gNodeB instances in the network
    :return: Dictionary containing the calculated network KPIs
    """
    # Calculate overall network latency
    overall_network_latency = calculate_overall_network_latency(gnodebs)
    
    # Calculate total throughput for all gNodeBs
    total_throughput = sum(calculate_gnodeb_throughput(gnodeb, gnodebs) for gnodeb in gnodebs)
    
    cell_loads = [calculate_cell_load(cell.ID, gnodebs) for gnodeb in gnodebs for cell in gnodeb.Cells]
    average_cell_load = sum(cell_loads) / len(cell_loads) if cell_loads else 0
    
    # Compile the KPIs into a dictionary
    network_kpis = {
        'overall_network_latency': overall_network_latency,
        'total_network_throughput': total_throughput,
        'average_cell_load': average_cell_load
    }
    
    return network_kpis