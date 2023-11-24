# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
import os
import json
import random
import math
from .gNodeB import gNodeB  # Relative import
from .cell import Cell
from .ue import UE
from database.database_manager import DatabaseManager
from .init_gNodeB import initialize_gNodeBs  # Import the new initialization function
from .init_ue import initialize_ues  # Import the new UE initialization function
from .init_gNodeB import initialize_gNodeBs  # Import the new initialization function
from .init_cell import initialize_cells
db_manager = DatabaseManager()

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
    gNodeBs = initialize_gNodeBs()

    # Initialize Cells and link them to gNodeBs
    cells = initialize_cells(gNodeBs)

    # After initializing gNodeBs and cells
    ues = initialize_ues(num_ues_to_launch, gNodeBs, ue_config)
    

    return gNodeBs, cells, ues