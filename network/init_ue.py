# init_ue.py
# Initialization of UEs
import os
from .ue import UE
from network.utils import allocate_ues
from Config_files.config import Config

# Get base path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = Config(base_dir)
ue_config = config.ue_config

def initialize_ues(num_ues, cells, gnodebs, ue_config):

    # Get list of all sectors from cells
    all_sectors = []
    for cell in cells.values():
        all_sectors.extend(cell.sectors)
    
    if not all_sectors:
        print("Error: No sectors found")
        return

    # Use the modified allocate_ues function from utils.py
    allocated_ues = allocate_ues(num_ues, all_sectors, ue_config)

    return allocated_ues