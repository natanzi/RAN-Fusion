# utils.py in the network directory
import random
import math
from network import UE

def random_location_within_radius(center_lat, center_lon, radius_km):

    x = random.uniform(-radius_km, radius_km)
    y = random.uniform(-radius_km, radius_km)

    lat = center_lat + x/110.574
    lon = center_lon + y/111.320*math.cos(center_lat)

    return lat, lon

def allocate_ues(num_ues, sectors, ue_config):
    
    # Track per-sector allocation
    ue_allocs = {s: [] for s in sectors}  
    rr_pointer = 0
    
    for _ in range(num_ues):
    
        # Round-robin sector selection 
        sector = sectors[rr_pointer % len(sectors)]
        
        if sector.remaining_capacity > 0:
        # Allocate UE if capacity available
            ue = create_ue(sector, ue_config)  
            sector.add_ue(ue)
            ue_allocs[sector].append(ue)

        else:
            # Apply fallback logic  
            for fallback_sector in sectors:
                if fallback_sector.remaining_capacity > 0:
                    ue = create_ue(fallback_sector) 
                    fallback_sector.add_ue(ue)  
                    ue_allocs[fallback_sector].append(ue)
                    break 
                    
        rr_pointer += 1
        
    # Flatten final UE allocation lists
    allocated_ues = [ue for ue_list in ue_allocs.values() for ue in ue_list]   
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
    for sector in all_sectors.values():
        if sector.cell.gnodeb == gnb:
            gnb_sectors.append(sector)

    return gnb_sectors


def create_ue(sector, ue_config):
    gnb = sector.cell.gnodeb
    latitude, longitude = random_location_within_radius(gnb.latitude, gnb.longitude, gnb.coverageRadius)

    # Create UE without specifying ue_id, letting the UE class handle it
    ue = UE(config=ue_config,
            connected_sector=sector.id,
            connected_cell=sector.cell.id,
            gnodeb_id=gnb.id,
            location=[latitude, longitude])

    return ue