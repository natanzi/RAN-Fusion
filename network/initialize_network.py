# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs
# This file is located in the network directory

from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_sector import initialize_sectors
from .init_ue import initialize_ues
from logs.logger_config import ue_logger
from .sector import Sector
from network.ue import UE
from utills.debug_utils import debug_print
from Config_files.config import Config  # Import the Config class
from database.database_manager import DatabaseManager  # Import DatabaseManager

def initialize_network(base_dir, num_ues_to_launch=None):
    # Create an instance of Config
    config = Config(base_dir)

    # Access the network map data
    network_map = config.network_map_data
    
    # Create an instance of DatabaseManager
    db_manager = DatabaseManager()

    # Initialize gNodeBs
    gNodeBs = initialize_gNodeBs(config.gNodeBs_config, db_manager)
    print("Initialized gNodeBs:")
    for gnb_id, gnb in gNodeBs.items():
        print(f"gNodeB ID: {gnb_id}, Details: {gnb}")

    # Initialize Cells
    cells = initialize_cells(gNodeBs, config.cells_config, db_manager)
    if cells is not None:
        print("Initialized Cells:")
        for cell_id, cell in cells.items():
            print(f"Cell ID: {cell_id}, Details: {cell}")
    else:
        print("No cells were initialized.")

    # Initialize Sectors
    sectors = initialize_sectors(cells, config.sectors_config, db_manager)
    print("Initialized Sectors:")
    for sector_id, sector in sectors.items():
        print(f"Sector ID: {sector_id}, Details: {sector}")

    # Initialize UEs if num_ues_to_launch is provided
    if num_ues_to_launch:
        ues = initialize_ues(num_ues_to_launch, sectors, cells, gNodeBs, config.ue_config)
        print("Initialized UEs:")
        for ue in ues:
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Sector ID: {ue.ConnectedSector}, Cell ID: {ue.ConnectedCellID}, gNodeB ID: {ue.gNodeB_ID}")
        return gNodeBs, cells, sectors, ues

    return gNodeBs, cells, sectors