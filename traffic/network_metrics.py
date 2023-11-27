#network_metrics.py
# network_metrics.py is in traffic directory
from math import radians, cos, sin, asin, sqrt
from utils.location_utils import calculate_distance_cached

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

def calculate_cell_load(cell_id, gnodebs):
    # Find the cell with the matching cell_id
    cell = find_cell_by_id(cell_id, gnodebs)
    
    if cell is None:
        raise ValueError(f"Cell with ID {cell_id} not found.")

    # Calculate the current load based on the number of connected UEs
    current_load = len(cell.ConnectedUEs)
    max_capacity = cell.MaxConnectedUEs
    
    # Calculate the load as a percentage
    load_percentage = (current_load / max_capacity) * 100 if max_capacity > 0 else 0
    
    return load_percentage

def find_cell_by_id(cell_id, gnodebs):
    # Iterate over all gNodeBs to find the cell with the given ID
    for gnodeb in gnodebs:
        for cell in gnodeb.cells:  # Assuming each gNodeB has a list of cells
            if cell.ID == cell_id:
                return cell
    return None

# Calculate the throughput for a UE
def calculate_throughput(data_size, interval, signal_strength, network_load_impact):
    base_throughput = (data_size / 1000) / interval
    throughput = base_throughput * signal_strength * (1 - network_load_impact)
    return throughput

# Calculate the total throughput for all UEs in a cell
def calculate_cell_throughput(cell, gnodebs):
    total_throughput = 0
    for ue in cell.assigned_UEs:
        signal_strength = calculate_signal_strength(ue, cell.gNodeB)
        network_load_impact = calculate_cell_load(cell.ID, gnodebs)
        ue_throughput = calculate_throughput(ue.data_size, ue.interval, signal_strength, network_load_impact)
        total_throughput += ue_throughput
    return total_throughput

# Calculate the total throughput for all cells in a gNodeB
def calculate_gnodeb_throughput(gNodeB, gnodebs):
    total_throughput = 0
    for cell in gNodeB.Cells:
        cell_throughput = calculate_cell_throughput(cell, gnodebs)
        total_throughput += cell_throughput
    return total_throughput

# Calculate latency for a UE as a function of signal strength, distance to gNodeB, and network load
def calculate_ue_latency(ue, gNodeB, gnodebs):
    signal_strength = calculate_signal_strength(ue, gNodeB)
    distance_to_gNodeB = calculate_distance_cached(ue.Latitude, ue.Longitude, gNodeB.Latitude, gNodeB.Longitude)
    network_load_impact = calculate_ue_load(ue.ID, gnodebs)
    # Latency calculation can be a complex function involving these parameters
    # For simplicity, we'll assume it's a linear combination
    latency = (1 / signal_strength) + distance_to_gNodeB + network_load_impact
    return latency

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