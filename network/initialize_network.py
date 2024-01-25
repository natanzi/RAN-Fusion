# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_sector import initialize_sectors  # Import the initialize_sectors function
from .init_ue import initialize_ues

# This is a pseudo-code outline of the final initialize_network.py
from network.init_gNodeB import initialize_gNodeBs
from network.init_cell import initialize_cells
from network.init_sector import initialize_sectors
from network.init_ue import initialize_ues

def initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, sectors_config, ue_config, db_manager):
    # Initialize gNodeBs
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)
    
    # Initialize Cells
    cells = initialize_cells(gNodeBs, cells_config, db_manager)
    
    # Initialize Sectors
    sectors = initialize_sectors(cells, sectors_config, db_manager)
    
    # Initialize UEs
    ues = initialize_ues(num_ues_to_launch, sectors, ue_config, db_manager)
    
    return gNodeBs, cells, sectors, ues