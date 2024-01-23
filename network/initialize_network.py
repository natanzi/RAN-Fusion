# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_sector import initialize_sectors  # Import the initialize_sectors function
from .init_ue import initialize_ues
from threading import Lock

def initialize_network(num_ues_to_launch, gNodeBs_config, ue_config, db_manager):
    print("Debug: initialize_network started.")

    # Initialize gNodeBs with the provided configuration
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)
    print(f"Debug: Initialized {len(gNodeBs)} gNodeBs.")

    # Initialize Cells with the provided configuration and link them to gNodeBs
    cells = initialize_cells(gNodeBs)  # Ensure that initialize_cells returns the cells
    print("Debug: Cells initialized and linked to gNodeBs.")

    # After cells are initialized, initialize sectors
    initialize_sectors(cells)  # Pass the cells to the initialize_sectors function
    print("Debug: Sectors initialized and linked to cells.")

    # Calculate the total capacity of all cells
    total_capacity = sum(cell.MaxConnectedUEs for cell in cells.values())
    print(f"Debug: Total capacity of all cells is {total_capacity} UEs.")

    # Check if the total capacity is less than the number of UEs to launch
    if num_ues_to_launch > total_capacity:
        print(f"Cannot launch {num_ues_to_launch} UEs, as it exceeds the total capacity of {total_capacity} UEs across all cells.")
        return  # Exit the function if the capacity is exceeded

    # After initializing gNodeBs and cells, initialize UEs with the provided configuration
    ues = initialize_ues(num_ues_to_launch, gNodeBs, ue_config, db_manager)  # Pass db_manager to the function
    print(f"Debug: Initialized {len(ues)} UEs out of requested {num_ues_to_launch}.")

    # Update the network state with the initialized elements
    # (This part of the code may need to be updated based on how the network state is managed in the new architecture)

    # Print the network state
    print("Debug: Network initialization process completed.")

    # Return the list of initialized UEs for further processing or verification
    return gNodeBs, cells, ues