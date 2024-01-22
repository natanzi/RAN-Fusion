# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_ue import initialize_ues
from .network_state import NetworkState
from threading import Lock

def initialize_network(num_ues_to_launch, gNodeBs_config, ue_config, db_manager):

    
    # Create a lock for the NetworkState
    network_state_lock = Lock()

    # Create an instance of NetworkState
    network_state = NetworkState(network_state_lock)

    # Initialize gNodeBs with the provided configuration
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)

    # Initialize Cells with the provided configuration and link them to gNodeBs
    # This function now updates network_state directly, so no need to assign its return value to a variable
    initialize_cells(gNodeBs, network_state)

    # Calculate the total capacity of all cells
    total_capacity = sum(cell.MaxConnectedUEs for cell in network_state.cells.values())

    # Check if the total capacity is less than the number of UEs to launch
    if num_ues_to_launch > total_capacity:
        print(f"Cannot launch {num_ues_to_launch} UEs, as it exceeds the total capacity of {total_capacity} UEs across all cells.")
        return  # Exit the function if the capacity is exceeded

    # After initializing gNodeBs and cells, initialize UEs with the provided configuration
    ues = initialize_ues(num_ues_to_launch, gNodeBs, ue_config, network_state)

    # Update the network state with the initialized elements
    # Since cells are already updated in network_state, we pass network_state.cells instead of cells
    network_state.update_state(gNodeBs, network_state.cells, ues)

    # Print the network state
    network_state.print_state()

    # Return the list of initialized UEs for further processing or verification
    return gNodeBs, network_state.cells, ues
