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

def calculate_network_load_impact(gNodeB):
    # Placeholder function to calculate network load impact
    connected_UEs = sum(len(cell.assigned_UEs) for cell in gNodeB.Cells)
    max_capacity = len(gNodeB.Cells) * max_UEs_per_cell  # Assuming each cell has same max capacity
    return min(1, connected_UEs / max_capacity)  # Ratio of load to capacity

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
