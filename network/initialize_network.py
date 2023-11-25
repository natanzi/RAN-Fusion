# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
from .init_gNodeB import initialize_gNodeBs  # Import the new initialization function
from .init_cell import initialize_cells  # Import the new Cell initialization function
from .init_ue import initialize_ues  # Import the new UE initialization function

def initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config):
    # Initialize gNodeBs with the provided configuration
    gNodeBs = initialize_gNodeBs(gNodeBs_config)

    # Initialize Cells with the provided configuration and link them to gNodeBs
    cells = cells = initialize_cells(gNodeBs)


    # After initializing gNodeBs and cells, initialize UEs with the provided configuration
    ues = initialize_ues(num_ues_to_launch, gNodeBs, ue_config)

    return gNodeBs, cells, ues