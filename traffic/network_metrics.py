#network_metrics.py
import math
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers. Use 3956 for miles
    return c * r

def calculate_gnodeb_load(gnodeb_id, gnodebs):
    gNodeB = next((node for node in gnodebs if node.ID == gnodeb_id), None)
    if gNodeB is None:
        return None  # or raise an exception if gNodeB with the given ID does not exist
    connected_UEs = sum(len(cell.assigned_UEs) for cell in gNodeB.Cells)
    max_capacity = gNodeB.CellCount * gNodeB.MaxUEs
    return min(1, connected_UEs / max_capacity)

def calculate_cell_load(cell_id, gnodebs):
    for gNodeB in gnodebs:
        cell = next((cell for cell in gNodeB.Cells if cell.ID == cell_id), None)
        if cell:
            connected_UEs = len(cell.assigned_UEs)
            max_capacity = gNodeB.MaxUEs  # Assuming max UEs per cell is defined at gNodeB level
            return min(1, connected_UEs / max_capacity)
    return None  # or raise an exception if cell with the given ID does not exist

def calculate_network_load(gnodebs):
    total_connected_UEs = sum(sum(len(cell.assigned_UEs) for cell in gNodeB.Cells) for gNodeB in gnodebs)
    total_max_capacity = sum(gNodeB.CellCount * gNodeB.MaxUEs for gNodeB in gnodebs)
    return min(1, total_connected_UEs / total_max_capacity)

def calculate_ue_load(ue_id, gnodebs):
    for gNodeB in gnodebs:
        for cell in gNodeB.Cells:
            ue = next((ue for ue in cell.assigned_UEs if ue.ID == ue_id), None)
            if ue:
                # Assuming UE has attributes for current data rate demand and the cell has max data rate
                return min(1, ue.data_rate_demand / cell.max_data_rate)
    return None  # or raise an exception if UE with the given ID does not exist

def is_entity_congested(connected_UEs, max_capacity):
    """
    Determine if a cell or gNodeB is congested based on the number of connected UEs and the maximum capacity.
    :param connected_UEs: The number of UEs currently connected to the entity.
    :param max_capacity: The maximum number of UEs that the entity can support.
    :return: True if the entity is congested, False otherwise.
    """
    load_percentage = (connected_UEs / max_capacity) * 100
    return load_percentage > 85

# Example usage within the simulation loop or a relevant function
    for gnodeb in gNodeBs:
        gnodeb_congested = is_entity_congested(len(gnodeb.ConnectedUEs), gnodeb.MaxUEs)
        if gnodeb_congested:
            print(f"gNodeB {gnodeb.ID} is congested.")

        for cell in Cells:
            cell_congested = is_entity_congested(len(cell.ConnectedUEs), cell.MaxConnectedUEs)
            if cell_congested:
                print(f"Cell {cell.ID} is congested.")

def calculate_signal_strength(ue, gNodeB):
    # Assuming 'distance' is a function from 'location_utils.py' that calculates the distance
    # between two points (latitude, longitude)
    from location_utils import distance

    # Calculate the distance between the UE and the gNodeB
    distance_to_gNodeB = distance((ue.Latitude, ue.Longitude), (gNodeB.Latitude, gNodeB.Longitude))
    
    # Adjust the signal strength calculation to return a value between 0 and 100
    # The signal strength is 100 at the gNodeB and decreases linearly to 0 at the edge of the coverage radius
    signal_strength = max(0, 100 * (1 - (distance_to_gNodeB / gNodeB.CoverageRadius)))
    
    return signal_strength

# Now you can use the haversine function in your calculate_signal_strength function
def calculate_signal_strength(ue, gNodeB):
    distance_to_gNodeB = haversine(ue.Location[1], ue.Location[0], gNodeB.Longitude, gNodeB.Latitude)
    return max(0, 1 - (distance_to_gNodeB / gNodeB.CoverageRadius))

def distance(location1, location2):
    """
    Calculate the great-circle distance between two locations using their latitudes and longitudes.

    :param location1: Tuple representing the latitude and longitude of the first location.
    :param location2: Tuple representing the latitude and longitude of the second location.
    :return: Great-circle distance between the two locations in kilometers.
    """
    lat1, lon1 = location1
    lat2, lon2 = location2
    return haversine(lat1, lon1, lat2, lon2)

       
def calculate_throughput(data_size, interval, signal_strength, network_load_impact):
    base_throughput = (data_size / 1000) / interval
    throughput = base_throughput * signal_strength * (1 - network_load_impact)
    return throughput
