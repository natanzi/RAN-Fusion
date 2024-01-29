# init_ue.py
# Initialization of UEs
import random
from database.database_manager import DatabaseManager
from .ue import UE
from database.time_utils import get_current_time_ntp
from logs.logger_config import ue_logger
from network.utils import random_location_within_radius
from utills.debug_utils import debug_print

current_time = get_current_time_ntp()

def initialize_ues(num_ues_to_launch, gNodeBs, sectors, ue_config, db_manager):
    ues = []
    for _ in range(num_ues_to_launch):
        ue_data = random.choice(ue_config['ues']).copy()
        ue_id = ue_data.get('ue_id', '').strip()
        ue_data['ue_id'] = ue_id
        ue = UE(**ue_data)
        # Logic to select the appropriate sector based on UE's location
        # This is a placeholder for the logic to determine the sector
        #selected_sector_id = determine_sector_for_ue(ue, sectors)
        #if selected_sector_id in sectors:
            #sectors[selected_sector_id].add_ue(ue)
            #ues.append(ue)
        #else:
        # print(f"Error: No suitable sector found for UE {ue_id}.")
    #print(f"Initialized {len(ues)} UEs.")
    #return ues
        
        
        