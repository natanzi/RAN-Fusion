#network_metrics.py
import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.

    :param lat1: Latitude of the first point in degrees.
    :param lon1: Longitude of the first point in degrees.
    :param lat2: Latitude of the second point in degrees.
    :param lon2: Longitude of the second point in degrees.
    :return: Distance in kilometers.
    """
    R = 6371.0  # Radius of the Earth in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

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
    # Placeholder function to calculate signal strength
    distance_to_gNodeB = distance((ue.Latitude, ue.Longitude), (gNodeB.Latitude, gNodeB.Longitude))
    # Simple signal strength model (can be refined)
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

def simulate_latency(ue, gNodeBs, service_type):
    connected_gNodeB = next((gnb for gnb in gNodeBs if gnb.ID == ue.ConnectedCellID), None)
    if connected_gNodeB:
        signal_strength = calculate_signal_strength(ue, connected_gNodeB)
        network_load_impact = calculate_network_load_impact(connected_gNodeB)
        
        # Base latency based on distance
        base_latency = distance((ue.Latitude, ue.Longitude), (connected_gNodeB.Latitude, connected_gNodeB.Longitude)) * 0.1
        
        # Adjust latency based on service type, signal strength, and network load
        if service_type == 'voice':
            latency = base_latency + (network_load_impact * 10)  # Voice is sensitive to network load
        elif service_type == 'video':
            latency = base_latency + (1 - signal_strength) * 20  # Video is sensitive to signal strength
        elif service_type == 'gaming':
            latency = base_latency + 5  # Gaming requires low latency
        else:
            latency = base_latency + 15  # Default for other services
        return latency
    return 0

def calculate_throughput(data_size, interval, signal_strength, network_load_impact):
    base_throughput = (data_size / 1000) / interval
    throughput = base_throughput * signal_strength * (1 - network_load_impact)
    return throughput
