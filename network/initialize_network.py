# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
from .init_gNodeB import initialize_gNodeBs  # Import the new initialization function
from .init_cell import initialize_cells  # Import the new Cell initialization function
from .init_ue import initialize_ues  # Import the new UE initialization function
from .network_state import NetworkState  # Import the NetworkState class
from .network_state import print_network_state  # Import the print_network_state function

def initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config):
    # Initialize gNodeBs with the provided configuration
    gNodeBs = initialize_gNodeBs(gNodeBs_config)

    # Initialize Cells with the provided configuration and link them to gNodeBs
    cells = cells = initialize_cells(gNodeBs)


    # After initializing gNodeBs and cells, initialize UEs with the provided configuration
    ues = initialize_ues(num_ues_to_launch, gNodeBs, ue_config)
    # Create an instance of NetworkState
    network_state = NetworkState()

    # Update the network state with the initialized elements
    network_state.update_state(gNodeBs, cells, ues)
    return gNodeBs, cells, ues
    
    # Print the network state
    network_state.print_state()