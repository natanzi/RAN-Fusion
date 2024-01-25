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
            existing_ue_ids.add(ue_id)  # This line should be inside the while loop


        # Remove the 'IMEI' key from ue_data since it's generated within the UE class
        ue_data.pop('IMEI', None)
        # Set default values or generate necessary parameters for UE constructor
        ue_data['connected_cell_id'] = None  # or some logic to determine the cell ID
        ue_data['connected_sector'] = None  # or some logic to determine the sector
        ue_data['is_mobile'] = True  # or some logic to determine mobility
        ue_data['initial_signal_strength'] = -95  # or some logic to determine signal strength
        ue_data['max_bandwidth'] = 100  # or some logic to determine bandwidth
        ue_data['duplex_mode'] = 'FDD'  # or some logic to determine duplex mode
        ue_data['tx_power'] = 23  # or some logic to determine transmission power
        ue_data['bandwidth_parts'] = 1  # or some logic to determine bandwidth parts
        ue_data['channel_model'] = 'Rayleigh'  # or some logic to determine channel model
        ue_data['traffic_model'] = 'FullBuffer'  # or some logic to determine traffic model
        ue_data['scheduling_requests'] = 1  # or some logic to determine scheduling requests
        ue_data['rlc_mode'] = 'AM'  # or some logic to determine RLC mode
        ue_data['snr_thresholds'] = [0, 5, 10, 15, 20]  # or some logic to determine SNR thresholds
        ue_data['ho_margin'] = 3  # or some logic to determine handover margin
        ue_data['n310'] = 1  # or some logic to determine N310
        ue_data['n311'] = 1  # or some logic to determine N311
        ue_data['model'] = 'Generic'  # or some logic to determine model
        
        # Ensure the key matches the UE class constructor argument name
        if 'connectedCellID' in ue_data:
            ue_data['connected_cell_id'] = ue_data.pop('connectedCellID')
        if 'isMobile' in ue_data:
            ue_data['is_mobile'] = ue_data.pop('isMobile')    
        if 'initialSignalStrength' in ue_data:
            ue_data['initial_signal_strength'] = ue_data.pop('initialSignalStrength')
        if 'maxBandwidth' in ue_data:
            ue_data['max_bandwidth'] = ue_data.pop('maxBandwidth')
            
        # Create the UE instance and add it to the list
        ue = UE(**ue_data)
        ues.append(ue)

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