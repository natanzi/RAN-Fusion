# init_ue.py
# Initialization of UEs
import random
import math
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from Config_files.config_load import load_all_configs
from .ue import UE 
import logging
from network.network_state import NetworkState

# Create an instance of NetworkState
network_state = NetworkState()

def random_location_within_radius(latitude, longitude, radius_km):
    random_radius = random.uniform(0, radius_km)
    random_angle = random.uniform(0, 2 * math.pi)
    delta_lat = random_radius * math.cos(random_angle)
    delta_lon = random_radius * math.sin(random_angle)
    return (latitude + delta_lat, longitude + delta_lon)

def initialize_ues(num_ues_to_launch, gNodeBs, ue_config):
    ues = []
    db_manager = DatabaseManager(network_state)
    DEFAULT_BANDWIDTH_PARTS = [1, 2, 3, 4]  # Example default values
    ue_id_counter = 1  # Initialize the UE ID counter

    # Instantiate UEs from the configuration
    for ue_data in ue_config['ues']:
        # Adjust the keys to match the UE constructor argument names
        ue_data['location'] = (ue_data['location']['latitude'], ue_data['location']['longitude'])
        ue_data['connected_cell_id'] = ue_data.pop('connectedCellId')
        ue_data['is_mobile'] = ue_data.pop('isMobile')
        ue_data['initial_signal_strength'] = ue_data.pop('initialSignalStrength')
        ue_data['rat'] = ue_data.pop('rat')
        ue_data['max_bandwidth'] = ue_data.pop('maxBandwidth')
        ue_data['duplex_mode'] = ue_data.pop('duplexMode')
        ue_data['tx_power'] = ue_data.pop('txPower')
        ue_data['modulation'] = ue_data.pop('modulation')
        ue_data['coding'] = ue_data.pop('coding')
        ue_data['mimo'] = str(ue_data.pop('mimo'))
        ue_data['processing'] = ue_data.pop('processing')
        ue_data['bandwidth_parts'] = ue_data.pop('bandwidthParts')
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
        ue_data['service_type'] = ue_data.get('serviceType', None)
        ue_data.pop('IMEI', None)  # Ensure 'IMEI' is not passed to the constructor
        ue_data.pop('screensize', None)  # Add this line to remove 'screensize' key
        ue_data.pop('batterylevel', None)  # This line removes 'batterylevel' key
        # Assign sequential UE ID
        ue_data['ue_id'] = f"UE{ue_id_counter}" 
        
        # Ensure modulation is a single scalar value, not a list
        
        if isinstance(ue_data['modulation'], list):
            ue_data['modulation'] = random.choice(ue_data['modulation'])
        
        # Check if 'bandwidthParts' exists in ue_data and handle it appropriately
        if 'bandwidthParts' not in ue_data:
            # If 'bandwidthParts' does not exist, provide a default value or handle the absence
            ue_data['bandwidth_parts'] = random.choice(DEFAULT_BANDWIDTH_PARTS)
        else:
            # If 'bandwidthParts' exists and it's a list, choose a random element
            if isinstance(ue_data['bandwidthParts'], list):
                ue_data['bandwidth_parts'] = random.choice(ue_data['bandwidthParts'])
            else:
                # If 'bandwidthParts' is not a list (i.e., it's a single value), use it as is
                ue_data['bandwidth_parts'] = ue_data['bandwidthParts']
        
        # Instantiate UE with the adjusted data
        ue = UE(**ue_data)
        # Assign UE to a random cell of a random gNodeB, if available
        selected_gNodeB = random.choice(list(gNodeBs.values()))
        if hasattr(selected_gNodeB, 'Cells'):  # Correct attribute name should be used here
            selected_cell = random.choice(selected_gNodeB.Cells)
            try:
                # Add the UE to the cell's ConnectedUEs list
                selected_cell.add_ue(ue, network_state)  # Pass the network_state object to the add_ue method
            # The network_state should be updated here if necessary
            # network_state.update_state(...)
                ue.ConnectedCellID = selected_cell.ID
                logging.info(f"UE '{ue.ID}' has been attached to Cell '{ue.ConnectedCellID}'.")
            except Exception as e:
        # Handle the case where the cell is at maximum capacity
                logging.error(f"Failed to add UE '{ue.ID}' to Cell '{selected_cell.ID}': {e}")
        
        # Serialize and write to InfluxDB
        point = ue.serialize_for_influxdb()
        db_manager.insert_data(point)    

    # Prepare static UE data for database insertion
        #static_ue_data = {
            #'ue_id': ue.ID,
            ##'imei': ue.IMEI,
            #'service_type': ue.ServiceType,
            #'model': ue.Model,
            #'rat': ue.RAT,
            #'max_bandwidth': ue.MaxBandwidth,
            #'duplex_mode': ue.DuplexMode,
            #'tx_power': ue.TxPower,
            #'modulation': ue.Modulation,
            #'coding': ue.Coding,
            #'mimo': ue.MIMO,
            #'processing': ue.Processing,
            #'bandwidth_parts': ue.BandwidthParts,
            #'channel_model': ue.ChannelModel,
            ##'direction': ue.Direction,
            #'traffic_model': ue.TrafficModel,
           # 'scheduling_requests': bool(ue.SchedulingRequests),  # Convert to boolean
            #'rlc_mode': ue.RLCMode,
            #'snr_thresholds': ','.join(map(str, ue.SNRThresholds)),  # Serialize list into a comma-separated string
            #'ho_margin': ue.HOMargin,
            #'n310': ue.N310,
            #'n311': ue.N311,
            #'screen_size': ue.ScreenSize,
            #'battery_level': ue.BatteryLevel
        #}
        # Write UE data to the database
        ues.append(ue)
    
    # Calculate the number of additional UEs needed
    additional_ues_needed = max(0, num_ues_to_launch - len(ues))

    # Create additional UEs if needed
    for _ in range(additional_ues_needed):
        selected_gNodeB = random.choice(list(gNodeBs.values()))
        available_cell = selected_gNodeB.find_underloaded_cell()
        random_location = random_location_within_radius(
            selected_gNodeB.Latitude, selected_gNodeB.Longitude, selected_gNodeB.CoverageRadius
        )
        if 'bandwidthParts' in ue_config['ues'][0]:
            bandwidth_parts = random.choice(ue_config['ues'][0]['bandwidthParts'])
        else:
            bandwidth_parts = random.choice(DEFAULT_BANDWIDTH_PARTS)
        
        new_ue = UE(
            ue_id=f"UE{ue_id_counter}",
            location=random_location,
            connected_cell_id=available_cell.ID if available_cell else None,
            is_mobile=True,
            initial_signal_strength=random.uniform(-120, -30),
            rat='NR',
            max_bandwidth=random.choice([5, 10, 15, 20]),
            duplex_mode='TDD',
            tx_power=random.randint(0, 23),
            modulation=random.choice(['QPSK', '16QAM', '64QAM']),
            coding=random.choice(['LDPC', 'Turbo']),
            mimo='2*2',
            processing=random.choice(['low', 'normal', 'high']),
            bandwidth_parts=bandwidth_parts,
            channel_model=random.choice(['urban', 'rural', 'suburban']),
            velocity=random.uniform(0, 50),
            direction=random.randint(0, 360),
            traffic_model=random.choice(['fullbuffer', 'bursty', 'periodic']),
            scheduling_requests=random.randint(1, 10),
            rlc_mode=random.choice(['AM', 'UM']),
            snr_thresholds=[random.randint(-20, 0) for _ in range(6)],
            ho_margin=random.randint(1, 10),
            n310=random.randint(1, 10),
            n311=random.randint(1, 10),
            model='generic',
            service_type=random.choice(['video', 'game', 'voice', 'data', 'IoT'])
        )
        ue_id_counter += 1  # Increment the counter outside of any conditions

        if selected_gNodeB.Cells:
            selected_cell = random.choice(selected_gNodeB.Cells)
            try:
            # Add the UE to the cell's ConnectedUEs list
                selected_cell.add_ue(ue, network_state)
            # Update the network state with the current state of gNodeBs, cells, and UEs
                network_state.update_state(network_state.gNodeBs, list(network_state.cells.values()), list(network_state.ues.values()))
                ue.ConnectedCellID = selected_cell.ID
                logging.info(f"UE '{ue.ID}' has been attached to Cell '{ue.ConnectedCellID}'.")
            except Exception as e:
            # Handle the case where the cell is at maximum capacity
                logging.error(f"Failed to add UE '{ue.ID}' to Cell '{selected_cell.ID}': {e}")

        # You may want to implement additional logic to handle this case
        ue.ConnectedCellID = selected_cell.ID


        # Write UE static data to the database
        db_manager.insert_ue_data(ue)
        ues.append(new_ue)
        db_manager.close_connection()

    return ues