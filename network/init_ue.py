# init_ue.py
# Initialization of UEs
import random
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from .ue import UE
from database.time_utils import get_current_time_ntp
from logs.logger_config import ue_logger
from threading import Lock
current_time = get_current_time_ntp()

# Initialize a lock for thread-safe operations on sectors
sector_lock = Lock()

def initialize_ues(num_ues_to_launch, gNodeBs, ue_config):
    """
    Initialize UEs and assign them to sectors.

    Args:
        num_ues_to_launch (int): The number of UEs to launch.
        gNodeBs (dict): A dictionary of gNodeB instances.
        ue_config (dict): A dictionary containing UE configuration.

    Returns:
        list: A list of initialized UE instances.
    """
    ues = []
    db_manager = DatabaseManager()
    DEFAULT_BANDWIDTH_PARTS = [1, 2, 3, 4]  # Example default values

    # Initialize ue_id_counter based on the highest existing UE ID to avoid duplicates
    existing_ue_ids = set(db_manager.get_all_ue_ids())  # Convert to set if it's not already
    ue_id_counter = max(existing_ue_ids) + 1 if existing_ue_ids else 1

    # Flatten the list of sectors and sort by current load
    all_sectors = [sector for gNodeB in gNodeBs.values() for cell in gNodeB.Cells for sector in cell.sectors]
    all_sectors.sort(key=lambda sector: sector.current_ue_count / sector.MaxConnectedUEs)

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
        while ue_id in existing_ue_ids:  # Validate no duplicate UE IDs
            ue_id_counter += 1
            ue_id = f"UE{ue_id_counter}"
        ue_data['ue_id'] = ue_id
        existing_ue_ids.add(ue_id)  # Keep track of the generated UE ID
        ue_id_counter += 1

        # Assign UE to the least-loaded sector
        assigned = False
        assigned = False
        for sector in all_sectors:
            with sector_lock:  # Acquire lock before modifying the sector's UE list
                if sector.current_ue_count < sector.MaxConnectedUEs:
                # Generate a random location within the coverage radius of the sector's gNodeB
                    latitude, longitude = sector.gNodeB.Location
                    ue_location = random_location_within_radius(latitude, longitude, sector.gNodeB.CoverageRadius)
                    ue_data['location'] = ue_location
                    ue_data['connected_sector_id'] = sector.ID
                    ue = UE(**ue_data)
                    try:
                        sector.add_ue(ue)  # Assuming Sector class has an add_ue method
                        ue_logger.info(f"UE '{ue.ID}' has been attached to Sector '{sector.ID}' at '{current_time}'.")
                        ue.ConnectedSectorID = sector.ID  # Store the sector ID in the UE
                        assigned = True
                        break  # Exit the loop as the UE has been successfully assigned
                    except Exception as e:
                        ue_logger.error(f"Failed to add UE '{ue.ID}' to Sector '{sector.ID}' at '{current_time}': {e}")

        if not assigned:
            ue_logger.error(f"No available sector found for UE '{ue.ID}' at '{current_time}'.")
            continue  # Skip the rest of the loop if no sector is available

        # Serialize and write to InfluxDB
        try:
            point = ue.serialize_for_influxdb()
            db_manager.insert_data(point)
            ues.append(ue)
        except Exception as e:
            ue_logger.error(f"Failed to serialize or write UE '{ue.ID}' to InfluxDB at '{current_time}': {e}")

    db_manager.close_connection()
    expected_ues = num_ues_to_launch
    actual_ues = len(ues)

    if actual_ues != expected_ues:
        ue_logger.error(f"Expected {expected_ues} UEs, got {actual_ues}")
    else:
        ue_logger.info(f"Initialized {expected_ues} UEs successfully")

    return ues