# init_ue.py
# Initialization of UEs
import random
import math
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius

def random_location_within_radius(latitude, longitude, radius_km):
    random_radius = random.uniform(0, radius_km)
    random_angle = random.uniform(0, 2 * math.pi)
    delta_lat = random_radius * math.cos(random_angle)
    delta_lon = random_radius * math.sin(random_angle)
    return (latitude + delta_lat, longitude + delta_lon)

def initialize_ues(num_ues_to_launch, gNodeBs, ue_config):
    ues = []
    db_manager = DatabaseManager()

    for i, ue_data in enumerate(ue_config['ues'], start=1):
        # Adjust the keys to match the UE constructor argument names
        ue_data['ue_id'] = ue_data.pop('ue_id')
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
        ue_data['mimo'] = ue_data.pop('mimo')
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
        ue_data['service_type'] = ue_data.get('serviceType')  # Use get in case 'serviceType' is not provided

        # Assign sequential UE ID
        ue_data['ue_id'] = f"UE{i}"

        # Instantiate UE with the adjusted data
        ue = UE(**ue_data)
        # Assign UE to a random cell of a random gNodeB, if available
        selected_gNodeB = random.choice(gNodeBs)
        if selected_gNodeB.cells:
            selected_cell = random.choice(selected_gNodeB.cells)
            ue.connected_cell_id = selected_cell.cell_id
        
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
            'snr_thresholds': ue.SNRThresholds,
            'ho_margin': ue.HOMargin,
            'n310': ue.N310,
            'n311': ue.N311,
            'screen_size': ue.ScreenSize,
            'battery_level': ue.BatteryLevel
        }


        # Write UE static data to the database
        db_manager.insert_ue_static_data(static_ue_data)
        ues.append(ue)

    # Create additional UEs if needed
    additional_ues_needed = max(0, num_ues_to_launch - len(ues))
    for i in range(len(ues) + 1, num_ues_to_launch + 1):
        selected_gNodeB = random.choice(gNodeBs)
        random_location = random_location_within_radius(
            selected_gNodeB.latitude, selected_gNodeB.longitude, selected_gNodeB.coverage_radius
        )
        new_ue = UE(
            ue_id=f"UE{i}",  # Sequential UE ID from UE1 to UE50
            location=random_location,
            connected_cell_id=None,  # Placeholder for no initial cell connection
            is_mobile=True,
            initial_signal_strength=random.uniform(-120, -30),  # Randomized signal strength
            rat='NR',  # Assuming New Radio (5G) as the RAT
            max_bandwidth=random.choice([5, 10, 15, 20]),  # Randomized bandwidth
            duplex_mode='TDD',  # Assuming Time Division Duplexing
            tx_power=random.randint(0, 23),  # Randomized transmission power
            modulation=random.choice(['QPSK', '16QAM', '64QAM']),  # Randomized modulation
            coding=random.choice(['LDPC', 'Turbo']),  # Randomized coding scheme
            mimo=random.choice([True, False]),  # Randomized MIMO capability
            processing=random.choice(['low', 'normal', 'high']),  # Randomized processing capability
            bandwidth_parts=random.randint(1, 5),  # Randomized bandwidth parts
            channel_model=random.choice(['urban', 'rural', 'suburban']),  # Randomized channel model
            velocity=random.uniform(0, 50),  # Randomized velocity
            direction=random.randint(0, 360),  # Randomized direction
            traffic_model=random.choice(['fullbuffer', 'bursty', 'periodic']),  # Randomized traffic model
            scheduling_requests=random.randint(1, 10),  # Randomized scheduling requests
            rlc_mode=random.choice(['AM', 'UM']),  # Randomized RLC mode
            snr_thresholds=[random.randint(-20, 0) for _ in range(6)],  # Randomized SNR thresholds
            ho_margin=random.randint(1, 10),  # Randomized handover margin
            n310=random.randint(1, 10),  # Randomized N310
            n311=random.randint(1, 10),  # Randomized N311
            model='generic',  # Placeholder for model
            service_type=random.choice(['video', 'game', 'voice', 'data', 'IoT'])  # Randomized service type
        )
        if selected_gNodeB.cells:
            selected_cell = random.choice(selected_gNodeB.cells)
            new_ue.connected_cell_id = selected_cell.cell_id
        
        # Write UE static data to the database
        db_manager.insert_ue_static_data(new_ue)
        ues.append(new_ue)

    # Commit changes to the database and close the connection
    db_manager.commit_changes()
    db_manager.close_connection()

    return ues