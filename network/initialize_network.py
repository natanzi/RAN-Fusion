# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs
# This file is located in the network directory

from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_sector import initialize_sectors  # Import the initialize_sectors function
from .init_ue import initialize_ues
from logs.logger_config import ue_logger
from .sector import Sector
from network.ue import UE
from utills.debug_utils import debug_print

def initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, sectors_config, ue_config, db_manager):
    # Step 1: Instantiate gNodeBs
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)
    
    # Step 2: Instantiate Cells and associate with gNodeBs
    cells = initialize_cells(gNodeBs, cells_config, db_manager)
    
    # Step 3: Instantiate Sectors and associate with Cells
    sectors = initialize_sectors(cells, sectors_config, db_manager)

    # Step 4: Initialize UEs
    ues = initialize_ues(num_ues_to_launch, sectors, cells, gNodeBs)
    
    return gNodeBs, cells, sectors, ues
