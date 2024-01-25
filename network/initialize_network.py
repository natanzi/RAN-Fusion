# initialize_network.py
# Initialization of gNodeBs, Cells, Sectors, and UEs
# This file is located in the network directory

from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_sector import initialize_sectors
from .init_ue import initialize_ues

def initialize_network(gNodeBs_config, cells_config, sectors_config, ues_config, db_manager):
    print("Debug: initialize_network started.")

    # Initialize gNodeBs with the provided configuration
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)
    print(f"Debug: Initialized {len(gNodeBs)} gNodeBs.")

    # Initialize Cells with the provided configuration and link them to gNodeBs
    cells = initialize_cells(gNodeBs, cells_config, db_manager)
    print("Debug: Cells initialized and linked to gNodeBs.")

    # Call initialize_cells_with_sectors for each gNodeB
    for gnb in gNodeBs.values():
        gnb.initialize_cells_with_sectors(cells_config)

    # Initialize Sectors with the provided configuration and link them to Cells
    sectors = initialize_sectors(cells, sectors_config, db_manager)
    print("Debug: Sectors initialized and linked to Cells.")

    # Initialize UEs with the provided configuration
    ues = initialize_ues(ues_config, sectors, db_manager)
    print(f"Debug: Initialized {len(ues)} UEs.")

    # Link UEs to Sectors
    for ue in ues:
        # Assuming assign_to_sector is a method of UE class that assigns the UE to a sector
        # This method should also handle the logic to find the appropriate sector for the UE
        ue.assign_to_sector()

    print("Debug: Network initialization process completed.")
    return gNodeBs, cells, sectors, ues