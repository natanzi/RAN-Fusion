# init_ue.py
# Initialization of UEs
import random
import math
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from Config_files.config_load import load_all_configs
from .ue import UE
from network.network_state import NetworkState
from database.time_utils import get_current_time_ntp, server_pools
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger
current_time = get_current_time_ntp()

# Create an instance of NetworkState
network_state = NetworkState()

def initialize_ues(num_ues_to_launch, gNodeBs, ue_config, network_state):
    ues = []
    db_manager = DatabaseManager(network_state)
    DEFAULT_BANDWIDTH_PARTS = [1, 2, 3, 4]  # Example default values
    ue_id_counter = len(network_state.ues) + 1
    
    # Calculate the total capacity of all cells
    total_capacity = sum(cell.MaxConnectedUEs for gNodeB in gNodeBs.values() for cell in gNodeB.Cells if cell.IsActive)

    # Check if the total number of UEs to be launched exceeds the total capacity
    if num_ues_to_launch > total_capacity:
        ue_logger.error(f"Cannot launch {num_ues_to_launch} UEs, as it exceeds the total capacity of {total_capacity} UEs across all cells.")
        return []  # Return an empty list if the capacity is exceeded
    
    # Prepare a round-robin queue for gNodeBs
    round_robin_queue = [gNodeB for gNodeB in gNodeBs.values()]

    for _ in range(num_ues_to_launch):
        ue_data = random.choice(ue_config['ues']).copy()

        # Remove keys that are not used by the UE constructor
        ue_data.pop('IMEI', None)
        ue_data.pop('screensize', None)
        ue_data.pop('batterylevel', None)

        # Adjust the keys to match the UE constructor argument names
        ue_data['ue_id'] = f"UE{ue_id_counter}"

        # Check if 'bandwidthParts' exists in ue_data and handle it appropriately
        if 'bandwidthParts' in ue_data:
            # If 'bandwidthParts' exists and it's a list, choose a random element
            if isinstance(ue_data['bandwidthParts'], list) and ue_data['bandwidthParts']:
                ue_data['bandwidth_parts'] = random.choice(ue_data['bandwidthParts'])
            else:
                # If 'bandwidthParts' is not a list or is empty, use a default value
                ue_data['bandwidth_parts'] = random.choice(DEFAULT_BANDWIDTH_PARTS)
            # Remove the 'bandwidthParts' key as it's not expected by the UE constructor
            del ue_data['bandwidthParts']
        if isinstance(ue_data['modulation'], list):
            ue_data['modulation'] = random.choice(ue_data['modulation'])
        ue_data['connected_cell_id'] = ue_data.pop('connectedCellId', None)  
        ue_data['is_mobile'] = ue_data.pop('isMobile')
        ue_data['initial_signal_strength'] = ue_data.pop('initialSignalStrength')
        ue_data['rat'] = ue_data.pop('rat')
        ue_data['max_bandwidth'] = ue_data.pop('maxBandwidth')
        ue_data['duplex_mode'] = ue_data.pop('duplexMode')
        ue_data['tx_power'] = ue_data.pop('txPower')
        #ue_data['modulation'] = ue_data.pop('modulation')
        ue_data['coding'] = ue_data.pop('coding')
        ue_data['mimo'] = ue_data.pop('mimo')
        ue_data['processing'] = ue_data.pop('processing')
        ue_data['channel_model'] = ue_data.pop('channelModel')
        ue_data['velocity'] = ue_data.pop('velocity')
        ue_data['direction'] = ue_data.pop('direction')
        ue_data['traffic_model'] = ue_data.pop('trafficModel')
        ue_data['scheduling_requests'] = ue_data.pop('schedulingRequests')
        ue_data['rlc_mode'] = ue_data.pop('rlcMode')
        ue_data['snr_thresholds'] = ue_data.pop('snrThresholds')
        ue_data['ho_margin'] = ue_data.pop('hoMargin')
        ue_data['n310'] = ue_data.pop('n310')
        ue_data['n311'] = ue_data.pop('n311')
        ue_data['model'] = ue_data.pop('model')
        ue_data['service_type'] = ue_data.get('serviceType', None)  # Optional, with a default of None if not present

        # Generate a unique UE ID
        ue_id = f"UE{ue_id_counter}"
        existing_ue_ids = set(ue.ID for ue in network_state.ues)
        while ue_id in existing_ue_ids:
            ue_id_counter += 1
            ue_id = f"UE{ue_id_counter}"

        ue_data['ue_id'] = ue_id  # Set the unique UE ID

        # Use round-robin selection with fallback to least-loaded cell
        assigned = False
        for _ in range(len(round_robin_queue)):
            selected_gNodeB = round_robin_queue.pop(0)
            round_robin_queue.append(selected_gNodeB)

            # Generate a random location within the coverage radius of the selected gNodeB
            # Assuming selected_gNodeB.Location is a tuple (latitude, longitude)
            latitude, longitude = selected_gNodeB.Location
            ue_location = random_location_within_radius(latitude, longitude, selected_gNodeB.CoverageRadius)
            # Set the UE's location
            ue_data['location'] = ue_location
            
            available_cells = [cell for cell in selected_gNodeB.Cells if cell.current_ue_count < cell.MaxConnectedUEs and cell.IsActive]
            if available_cells:
                least_loaded_cell = sorted(available_cells, key=lambda cell: cell.current_ue_count)[0]
                # Adjust ue_data with the selected cell information
                ue_data['connected_cell_id'] = least_loaded_cell.ID
                # Instantiate UE with the adjusted data only if there's an available cell
                ue = UE(**ue_data)
                try:
                    least_loaded_cell.add_ue(ue, network_state)
                    ue.ConnectedCellID = least_loaded_cell.ID
                    ue_logger.info(f"UE '{ue.ID}' has been attached to Cell '{least_loaded_cell.ID}' at '{current_time}'.")
                    assigned = True
                    break
                except Exception as e:
                    ue_logger.error(f"Failed to add UE '{ue.ID}' to Cell '{least_loaded_cell.ID}' at '{current_time}': {e}")

        if not assigned:
            ue_logger.error(f"No available cell found for UE '{ue_id}' at '{current_time}'.")
            continue  # Skip the rest of the loop if no cell is available

        # Serialize and write to InfluxDB
        point = ue.serialize_for_influxdb()
        db_manager.insert_data(point)
        ues.append(ue)

        # Increment the UE ID counter for the next UE
        ue_id_counter += 1
    
    db_manager.close_connection()

    return ues