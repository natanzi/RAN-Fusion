# utils.py in the network directory
import random
import math
from network.ue import UE
from network.sector import Sector
from network.gNodeB import gNodeB
from network.cell import Cell
from math import radians, cos, sin, sqrt, atan2

def random_location_within_radius(center_lat, center_lon, radius_km):

    x = random.uniform(-radius_km, radius_km)
    y = random.uniform(-radius_km, radius_km)

    lat = center_lat + x/110.574
    lon = center_lon + y/111.320*math.cos(center_lat)

    return lat, lon

def allocate_ues(num_ues, sectors, ue_config):
    ue_allocs = {s: [] for s in sectors}
    rr_pointer = 0
    allocated_ues = []

    for _ in range(num_ues):
        allocated = False
        attempted_sectors = 0

        while not allocated and attempted_sectors < len(sectors):
            sector = sectors[rr_pointer % len(sectors)]
            rr_pointer += 1
            attempted_sectors += 1

            if sector.remaining_capacity > 0:
                ue = create_ue(sector, ue_config)
                sector.add_ue(ue)
                ue_allocs[sector].append(ue)
                allocated_ues.append(ue)
                allocated = True
                break  # Break the while loop once UE is allocated

        if not allocated:
            print("Warning: Unable to allocate UE, all sectors at capacity.")
            break  # Break the for loop if no sectors have capacity

    return allocated_ues


def allocate_to_gnb(gnb, num_ues, sectors, ue_config): 
    gnb_sectors = get_sectors_for_gnb(gnb, sectors)
    
    ues = []
    
    for _ in range(num_ues):
        # Pick random sector from this gnb
        sector = random.choice(gnb_sectors) 
        
        if sector.remaining_capacity > 0:
            # Create & add UE with ue_config
            ue = create_ue(sector, ue_config)  # Pass ue_config to create_ue
            sector.add_ue(ue)
            ues.append(ue)

    return ues

def get_sectors_for_gnb(gnb, all_sectors):
    # Find all sectors for this gnb
    gnb_sectors = []
    for sector in all_sectors:  # Directly iterate over the list
        if sector.cell.gNodeB == gnb:
            gnb_sectors.append(sector)
    return gnb_sectors


def create_ue(sector, ue_config):
    gnb = sector.cell.gNodeB
    latitude, longitude = random_location_within_radius(gnb.Latitude, gnb.Longitude, gnb.CoverageRadius)

    # Create UE without specifying ue_id, letting the UE class handle it
    ue = UE(config=ue_config,
            connected_sector=sector.sector_id,
            connected_cell=sector.cell_id,
            gnodeb_id=gnb.ID,
            location=[latitude, longitude])

    return ue

def get_total_capacity(sectors):
    total_capacity = 0
    for sector in sectors:
        total_capacity += sector.remaining_capacity
    return total_capacity

def calculate_distance(lat1, lon1, lat2, lon2):
        # Radius of the Earth in kilometers
        R = 6371.0

        # Convert coordinates from degrees to radians
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        # Difference in coordinates
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        return distance
