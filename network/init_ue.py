# init_ue.py
# Initialization of UEs

import random
import math
from .ue import UE
from database.database_manager import DatabaseManager

def random_location_within_radius(latitude, longitude, radius_km):
    random_radius = random.uniform(0, radius_km)
    random_angle = random.uniform(0, 2 * math.pi)
    delta_lat = random_radius * math.cos(random_angle)
    delta_lon = random_radius * math.sin(random_angle)
    return (latitude + delta_lat, longitude + delta_lon)

def initialize_ues(num_ues_to_launch, gNodeBs, ue_config):
    ues = []
    db_manager = DatabaseManager(db_path='path_to_your_database')

    for ue_data in ue_config['ues']:
        # Adjust the keys to match the UE constructor argument names
        ue_data['ue_id'] = ue_data.pop('ue_id')
        ue_data['location'] = (ue_data['location']['latitude'], ue_data['location']['longitude'])
        ue_data['connected_cell_id'] = ue_data.pop('connectedCellId')
        ue_data['is_mobile'] = ue_data.pop('isMobile')
        ue_data['initial_signal_strength'] = ue_data.pop('initialSignalStrength')
        # ... (rest of the UE data adjustments)

        ue = UE(**ue_data)
        # Assign UE to a random cell of a random gNodeB, if available
        selected_gNodeB = random.choice(gNodeBs)
        if selected_gNodeB.cells:
            selected_cell = random.choice(selected_gNodeB.cells)
            ue.connected_cell_id = selected_cell.cell_id
        
        # Write UE static data to the database
        db_manager.insert_ue_static_data(ue)
        ues.append(ue)

    additional_ues_needed = max(0, num_ues_to_launch - len(ues))
    for _ in range(additional_ues_needed):
        selected_gNodeB = random.choice(gNodeBs)
        random_location = random_location_within_radius(
            selected_gNodeB.latitude, selected_gNodeB.longitude, selected_gNodeB.coverage_radius
        )
        new_ue = UE(
            ue_id=f"UE{random.randint(1000, 9999)}",
            location=random_location,
            connected_cell_id=None,  # Placeholder for no initial cell connection
            is_mobile=True,
            initial_signal_strength=-70,  # Example placeholder value
            rat='LTE',  # Example placeholder value
            max_bandwidth=20,  # Example placeholder value in MHz
            duplex_mode='FDD',  # Example placeholder value
            tx_power=23,  # Example placeholder value in dBm
            modulation='QAM',  # Example placeholder value
            coding='Turbo',  # Example placeholder value
            mimo=True,  # Example placeholder value
            processing='normal',  # Example placeholder value
            bandwidth_parts=1,  # Example placeholder value
            channel_model='urban',  # Example placeholder value
            velocity=3.0,  # Example placeholder value in m/s
            direction=45,  # Example placeholder value in degrees
            traffic_model='fullbuffer',  # Example placeholder value
            scheduling_requests=5,  # Example placeholder value
            rlc_mode='AM',  # Example placeholder value
            snr_thresholds=[-15, -10, -6, 0, 5, 10],  # Example placeholder value in dB
            ho_margin=3,  # Example placeholder value in dB
            n310=1,  # Example placeholder value
            n311=1,  # Example placeholder value
            model='generic',  # Example placeholder value
            service_type='data'  # Example placeholder value
        )
        if selected_gNodeB.cells:
            selected_cell = random.choice(selected_gNodeB.cells)
            new_ue.connected_cell_id = selected_cell.cell_id
        
        # Write UE static data to the database
        db_manager.insert_ue_static_data(new_ue)
        ues.append(new_ue)

    db_manager.commit_changes()
    db_manager.close_connection()

    return ues