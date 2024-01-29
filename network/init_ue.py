# init_ue.py
# Initialization of UEs
import random
from database.database_manager import DatabaseManager
from .ue import UE
from database.time_utils import get_current_time_ntp
from logs.logger_config import ue_logger
from network.utils import random_location_within_radius
from utills.debug_utils import debug_print

def initialize_ues(num_ues, sectors, cells, gnodebs):

    ues = []
    
    for _ in range(num_ues):
            
        # Select random sector
        sector = random.choice(list(sectors.values()))
            
        # Get associated cell and gNodeB
        cell = sector.cell 
        gnodeb = cell.gNodeB

        # Generate location within gNodeB coverage radius 
        latitude, longitude = random_location_within_radius(
            gnodeb.Latitude, gnodeb.Longitude, gnodeb.CoverageRadius  
        )
            
        # Create UE 
        ue = UE(
            ue_id=f"UE{len(ues)+1}", 
            connected_sector=sector.sector_id,
            connected_cell_id=cell.ID,
            gnodeb_id=gnodeb.ID,  
            location=[latitude, longitude] 
        )
            
        # Set random service type
        ue.ServiceType = random.choice(["video", "game", "voice", "data", "IoT"])
            
        ues.append(ue)

    return ues
        
        
        