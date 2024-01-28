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
    
    # Make sure sectors is a collection of Sector objects
    assert all(isinstance(sec, Sector) for sec in sectors.values()), "Sectors must be a collection of Sector objects"
    
    # Step 4: Instantiate UEs
    ues = initialize_ues(num_ues_to_launch, ue_config, db_manager)
    # Debugging print statements
    print(f"initialize_ues returned: {type(ues)}, Contents: {ues}")
    
    # Add the debugging print statement here to check the type of 'ues' before calling associate_ue_with_sector_and_cell
    print(f"Type of 'ues' before calling associate_ue_with_sector_and_cell: {type(ues)}")
    
    # Step 5: Associate UEs with Sectors and Cells
    associate_ue_with_sector_and_cell(ues, sectors, db_manager)
    
    return gNodeBs, cells, sectors, ues

def has_capacity(sector):
    return len(sector.connected_ues) < int(sector.capacity)

def associate_ue_with_sector_and_cell(ues, sectors_queue, db_manager):
    # Ensure 'ues' is always a list
    if not isinstance(ues, list):
        ues = [ues]
    for ue in ues:  # Now 'ues' is guaranteed to be a list of UE objects
        associated = False
        for primary_candidate_sector in sectors_queue.values():  # Ensure sectors_queue is a dict of Sector objects
            if has_capacity(primary_candidate_sector):
                selected_sector = primary_candidate_sector
                associated_cell = selected_sector.cell
                if len(associated_cell.ConnectedUEs) >= associated_cell.maxConnectUes:  # Assuming 'connected_ues' is the correct attribute and 'maxConnectUes' is defined
                    ue_logger.warning(f"Cell {associated_cell.ID} at max capacity. Cannot add UE {ue.ID}")
                    continue  # Skip to the next sector/cell if this cell is at max capacity
                ue.connected_sector = selected_sector
                ue.connected_cell = associated_cell
                selected_sector.add_ue(ue)  # Use the add_ue method to ensure thread safety and proper logging
                associated_cell.add_ue(ue)  # Use the add_ue method to ensure thread safety and proper logging
                # Pass the cell ID as the second argument to update_ue_association
                db_manager.update_ue_association(ue, associated_cell.ID)
                ue_logger.info(f"UE {ue.ID} associated with Sector {selected_sector.sector_id} and Cell {associated_cell.ID}")
                associated = True
                break  # Break the loop once the UE is successfully associated
        if not associated:
            # This else block executes if no break occurs, indicating no sector had capacity for the UE
            ue_logger.error(f"No sectors available with capacity to add UE {ue.ID}")
            return ue, None, None  # Return the UE with None for both sector and cell if no association was made
    # If the function reaches this point without returning, it means all UEs were processed successfully
    return ues, sectors_queue, db_manager  # This return statement might need adjustment based on your actual logic