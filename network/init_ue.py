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
print(ue_config)

def initialize_ues(num_ues, sector_ids, cells, gnodebs, ue_config):
    sectors = []
    for cell_id, cell in cells.items():
        for sector_id in sector_ids:
            sector = cell.get_sector(sector_id)
            if sector is not None:
                sectors.append(sector)
            else:
                print(f"Sector with ID {sector_id} not found in cell {cell_id}")

    if not sectors:
        print("Error: No sectors found for allocation.")
        return []

    # Use the modified allocate_ues function from utils.py
    allocated_ues = allocate_ues(num_ues, sectors, ue_config)

    return allocated_ues