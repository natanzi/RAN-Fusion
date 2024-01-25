# init_ue.py
# Initialization of UEs
import random
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from .ue import UE
from database.time_utils import get_current_time_ntp
from logs.logger_config import ue_logger

current_time = get_current_time_ntp()

def initialize_ues(num_ues_to_launch, sectors, ue_config, db_manager):
    ues = []
    db_manager = DatabaseManager()
    existing_ue_ids = set(db_manager.get_all_ue_ids())  # Get existing UE IDs to avoid duplicates

    for ue_data in ue_config['ues']:
        # Use the ue_id from the JSON file if it's provided and not empty
        ue_id = ue_data.get('ue_id', '').strip()
        if not ue_id:
            # Generate a unique UE ID if not provided
            ue_id_counter = max(existing_ue_ids, default=0) + 1
            ue_id = f"UE{ue_id_counter}"
            while ue_id in existing_ue_ids:  # Ensure the generated UE ID is unique
                ue_id_counter += 1
                ue_id = f"UE{ue_id_counter}"
        
        if ue_id in existing_ue_ids:
            # Skip if this ue_id is already used
            continue

        # Add the ue_id to the set of existing IDs and to the ue_data
        existing_ue_ids.add(ue_id)
        ue_data['ue_id'] = ue_id

        # Create the UE instance and add it to the list
        ue = UE(**ue_data)
        ues.append(ue)

        if len(ues) >= num_ues_to_launch:
            break  # Stop if the desired number of UEs has been reached

    db_manager.close_connection()

    # Log the result
    actual_ues = len(ues)
    if actual_ues != num_ues_to_launch:
        ue_logger.error(f"Expected {num_ues_to_launch} UEs, got {actual_ues}")
    else:
        ue_logger.info(f"Initialized {num_ues_to_launch} UEs successfully")

    return ues