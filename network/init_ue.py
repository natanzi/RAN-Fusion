# init_ue.py
# Initialization of UEs
import random
from database.database_manager import DatabaseManager
from .ue import UE
from database.time_utils import get_current_time_ntp
from logs.logger_config import ue_logger


current_time = get_current_time_ntp()

def initialize_ues(num_ues_to_launch, sectors, ue_config, db_manager):
    from network.initialize_network import associate_ue_with_sector_and_cell
    ues = []
    existing_ue_ids = set(db_manager.get_all_ue_ids())  # Use passed db_manager instance

    for _ in range(num_ues_to_launch):
        ue_data = random.choice(ue_config['ues']).copy()  # Choose a random UE config to copy
        
        # Generate a unique UE ID if not provided
        ue_id = ue_data.get('ue_id', '').strip()
        if not ue_id:
            ue_id_counter = max((int(ue_id[2:]) for ue_id in existing_ue_ids if ue_id.startswith('UE')), default=0) + 1
            ue_id = f"UE{ue_id_counter}"
            while ue_id in existing_ue_ids:  # Ensure the generated UE ID is unique
                ue_id_counter += 1
                ue_id = f"UE{ue_id_counter}"
            existing_ue_ids.add(ue_id)
        
        ue_data['ue_id'] = ue_id  # Set the generated ue_id to ue_data
        # Remove the 'IMEI' key from ue_data since it's generated within the UE class
        ue_data.pop('IMEI', None)
        
        # Create the UE instance
        ue = UE(**ue_data)
        
        # Attempt to associate the UE with a sector and cell
        associated_ue, associated_sector, associated_cell = associate_ue_with_sector_and_cell(ue, sectors, db_manager)
        
        # Check if the association was successful
        if associated_ue and associated_sector and associated_cell:
            # If successful, append the associated UE to the list
            ues.append(associated_ue)
        else:
            # If the association failed, log an error or warning
            ue_logger.error(f"Failed to associate UE {ue_id} with a sector and cell.")
            continue  # Skip adding the UE to the list and continue with the next UE
        
        # Stop if the desired number of UEs has been reached
        if len(ues) >= num_ues_to_launch:
            break

    # Log the result
    actual_ues = len(ues)
    if actual_ues != num_ues_to_launch:
        ue_logger.error(f"Expected {num_ues_to_launch} UEs, got {actual_ues}")
    else:
        ue_logger.info(f"Initialized {num_ues_to_launch} UEs successfully")

    return ues