# init_ue.py
# Initialization of UEs
import random
import math
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from Config_files.config_load import load_all_configs
from .ue import UE 

def random_location_within_radius(latitude, longitude, radius_km):
    random_radius = random.uniform(0, radius_km)
    random_angle = random.uniform(0, 2 * math.pi)
    delta_lat = random_radius * math.cos(random_angle)
    delta_lon = random_radius * math.sin(random_angle)
    return (latitude + delta_lat, longitude + delta_lon)

def initialize_ues(num_ues_to_launch, gNodeBs, ue_config):
    ues = []
    db_manager = DatabaseManager()
    
    # Define a default list of bandwidth parts if not provided in ue_config
    DEFAULT_BANDWIDTH_PARTS = [1, 2, 3, 4]  # Example default values

    # Instantiate UEs from the configuration
    for i, ue_data in enumerate(ue_config['ues'], start=1):
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
        ue_data['ue_id'] = f"UE{i}"
        # Instantiate UE with the adjusted data
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
        
        ue = UE(**ue_data)
        
        # Assign UE to a random cell of a random gNodeB, if available
        selected_gNodeB = random.choice(gNodeBs)
        if hasattr(selected_gNodeB, 'Cells'):  # Correct attribute name should be used here
            selected_cell = random.choice(selected_gNodeB.Cells)
            ue.ConnectedCellID = selected_cell.ID

        # Prepare static UE data for database insertion
        static_ue_data = {
            'ue_id': ue.ID,
            'imei': ue.IMEI,
            'service_type': ue.ServiceType,
            'model': ue.Model,
            'rat': ue.RAT,
            'max_bandwidth': ue.MaxBandwidth,
            'duplex_mode': ue.DuplexMode,
            'tx_power': ue.TxPower,
            'modulation': ue.Modulation,
            'coding': ue.Coding,
            'mimo': ue.MIMO,
            'processing': ue.Processing,
            'bandwidth_parts': ue.BandwidthParts,
            'channel_model': ue.ChannelModel,
            'velocity': ue.Velocity,
            'direction': ue.Direction,
            'traffic_model': ue.TrafficModel,
            'scheduling_requests': ue.SchedulingRequests,
            'rlc_mode': ue.RLCMode,
            'snr_thresholds': ','.join(map(str, ue.SNRThresholds)),  # Serialize list into a comma-separated string
            'ho_margin': ue.HOMargin,
            'n310': ue.N310,
            'n311': ue.N311,
            'screen_size': ue.ScreenSize,
            'battery_level': ue.BatteryLevel
        }
        # Write UE static data to the database
        db_manager.insert_ue_static_data(static_ue_data)
        ues.append(ue)
    
    # Calculate the number of additional UEs needed
    additional_ues_needed = max(0, num_ues_to_launch - len(ues))

    # Create additional UEs if needed
    for _ in range(additional_ues_needed):
        selected_gNodeB = random.choice(gNodeBs)
        available_cell = selected_gNodeB.find_available_cell()
        if available_cell is not None:
            random_location = random_location_within_radius(
                selected_gNodeB.Latitude, selected_gNodeB.Longitude, selected_gNodeB.CoverageRadius
            )
        if 'bandwidthParts' in ue_config['ues'][0]:
            bandwidth_parts = random.choice(ue_config['ues'][0]['bandwidthParts'])
        else:
            bandwidth_parts = random.choice(DEFAULT_BANDWIDTH_PARTS)
            
            new_ue = UE(
                ue_id=f"UE{random.randint(1000, 9999)}",
                location=random_location,
                connected_cell_id=available_cell.ID,
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
        if selected_gNodeB.Cells:
            selected_cell = random.choice(selected_gNodeB.Cells)
            new_ue.ConnectedCellID = selected_cell.ID

        # Prepare static UE data for database insertion
        static_ue_data = {
            'ue_id': new_ue.ID,
            'imei': new_ue.IMEI,
            'service_type': new_ue.ServiceType,
            'model': new_ue.Model,
            'rat': new_ue.RAT,
            'max_bandwidth': new_ue.MaxBandwidth,
            'duplex_mode': new_ue.DuplexMode,
            'tx_power': new_ue.TxPower,
            'modulation': new_ue.Modulation,
            'coding': new_ue.Coding,
            'mimo': new_ue.MIMO,
            'processing': new_ue.Processing,
            'bandwidth_parts': ue.BandwidthParts,
            'channel_model': new_ue.ChannelModel,
            'velocity': new_ue.Velocity,
            'direction': new_ue.Direction,
            'traffic_model': new_ue.TrafficModel,
            'scheduling_requests': new_ue.SchedulingRequests,
            'rlc_mode': new_ue.RLCMode,
            'snr_thresholds': ','.join(map(str, new_ue.SNRThresholds)),
            'ho_margin': new_ue.HOMargin,
            'n310': new_ue.N310,
            'n311': new_ue.N311,
            'screen_size': ue.ScreenSize,  
            'battery_level': ue.BatteryLevel
        }

        # Write UE static data to the database
        db_manager.insert_ue_static_data(static_ue_data)
        ues.append(new_ue)

        # Commit changes to the database and close the connection
        db_manager.commit_changes()
        db_manager.close_connection()

    return ues