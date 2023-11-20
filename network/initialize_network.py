    # initialize_network.py
    # Initialization of gNodeBs, Cells, and UEs // this file located in network directory
import os
import json
import random
import math
from .gNodeB import gNodeB  # Relative import
from .cell import Cell
from .ue import UE

print("gNodeB import successful:", gNodeB)

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def random_location_within_radius(latitude, longitude, radius_km):
    random_radius = random.uniform(0, radius_km)
    random_angle = random.uniform(0, 2 * math.pi)
    delta_lat = random_radius * math.cos(random_angle)
    delta_lon = random_radius * math.sin(random_angle)
    return (latitude + delta_lat, longitude + delta_lon)

def initialize_network(num_ues_to_launch):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')

    gNodeBs_config = load_json_config(os.path.join(config_dir, 'gNodeB_config.json'))
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))
    ue_config = load_json_config(os.path.join(config_dir, 'ue_config.json'))

    # Initialize gNodeBs
    gNodeBs = gNodeB.from_json(gNodeBs_config)

    # Initialize Cells and link them to gNodeBs
    cells = []
    for cell_data in cells_config['cells']:
    # Map the JSON keys to the constructor parameter names
        cell_data_mapped = {
        'cell_id': cell_data['cell_id'],
        'gnodeb_id': cell_data['gnodeb_id'],
        'frequencyBand': cell_data['frequencyBand'],  # Corrected from 'frequency_band' to 'frequencyBand'
        'duplexMode': cell_data['duplexMode'],  # Ensure this matches the constructor argument name
        'tx_power': cell_data['txPower'],  # Ensure this matches the constructor argument name
        'bandwidth': cell_data['bandwidth'],
        'ssb_periodicity': cell_data['ssbPeriodicity'],
        'ssb_offset': cell_data['ssbOffset'],
        'max_connect_ues': cell_data['maxConnectUes'],
        'channel_model': cell_data['channelModel']
    }
    cell = Cell(**cell_data_mapped)
    cells.append(cell)

    # Initialize UEs and assign them to Cells
    ues = []
    for ue_data in ue_config['ues']:  # Assuming the key in the config is 'ues'
        ue = UE(**ue_data)  # Assuming UE class has an appropriate constructor
        # Assign UE to a random cell of a random gNodeB, if available
        selected_gNodeB = random.choice(gNodeBs)
        if selected_gNodeB.Cells:
            selected_cell = random.choice(selected_gNodeB.Cells)
            ue.ConnectedCellID = selected_cell.ID
        ues.append(ue)

    # Create additional UEs if needed
    additional_ues_needed = max(0, num_ues_to_launch - len(ues))
    for _ in range(additional_ues_needed):
        selected_gNodeB = random.choice(gNodeBs)
        random_location = random_location_within_radius(
            selected_gNodeB.Latitude, selected_gNodeB.Longitude, selected_gNodeB.CoverageRadius
        )
        new_ue = UE(
            ue_id=f"UE{random.randint(1000, 9999)}",
            location=random_location,
            connected_cell_id=None,  # Placeholder for no initial cell connection
            is_mobile=True,  # Assuming the UE is mobile
            service_type=random.choice(["video", "game", "voice", "data", "IoT"]),
            initial_signal_strength=random.uniform(0, 1),  # Random initial signal strength
            rat="5G",  # Assuming a 5G UE
            max_bandwidth=100,  # Example bandwidth value
            duplex_mode="FDD",  # Assuming Frequency Division Duplexing
            tx_power=23,  # Transmission power in dBm
            modulation="QAM",  # Example modulation
            coding="LDPC",  # Example coding scheme
            mimo="4x4",  # Example MIMO configuration
            processing="high",  # Processing capability
            bandwidth_parts=[10, 20, 30],  # Bandwidth parts
            channel_model="urban",  # Channel model
            velocity=random.uniform(0, 100),  # Random velocity
            direction=random.randint(0, 360),  # Random direction
            traffic_model="random",  # Traffic model
            scheduling_requests=True,  # Scheduling requests
            rlc_mode="UM",  # RLC mode
            snr_thresholds=[10, 20, 30],  # SNR thresholds
            ho_margin=3,  # Handover margin
            n310=5,  # N310 counter value
            n311=10,  # N311 counter value
            model="ModelX",  # Device model
            screenSize=f"{random.uniform(5.0, 7.0):.1f} inches",  # Random screen size
            batteryLevel=random.randint(10, 100)  # Random battery level
        
        )
        if selected_gNodeB.Cells:
            selected_cell = random.choice(selected_gNodeB.Cells)
            new_ue.ConnectedCellID = selected_cell.ID
        ues.append(new_ue)

    return gNodeBs, cells, ues
