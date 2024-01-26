# initialize_network.py
# Initialization of gNodeBs, Cells, and UEs // this file located in network directory
from .init_gNodeB import initialize_gNodeBs
from .init_cell import initialize_cells
from .init_sector import initialize_sectors  # Import the initialize_sectors function
from .init_ue import initialize_ues
from logs.logger_config import ue_logger
from .sector import Sector

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

    # Step 5: Associate UEs with Sectors and Cells
    associate_ue_with_sector_and_cell(ues, sectors, db_manager)

    return gNodeBs, cells, sectors, ues

def has_capacity(sector):
    return len(sector.connected_ues) < int(sector.capacity)

def associate_ue_with_sector_and_cell(ue, sectors_queue, db_manager):
    def has_capacity(sector):
        return len(sector.connected_ues) < sector.capacity
    
    def get_least_loaded_sector(cell_sectors):
        return min(cell_sectors, key=lambda sec: len(sec.connected_ues))
    
    def validate_and_update_db(ue, sector, cell):
        if len(cell.ConnectedUEs) < cell.maxConnectUes:
            ue.connected_sector = sector
            ue.connected_cell = cell
            sector.add_ue(ue)  # Use the add_ue method to ensure thread safety and proper logging
            cell.add_ue(ue)  # Use the add_ue method to ensure thread safety and proper logging
        
            # Pass the cell ID as the second argument to update_ue_association
            db_manager.update_ue_association(ue, cell.ID)
        
            return True
        return False
    
    for primary_candidate_sector in sectors_queue.values():  # Ensure sectors_queue is a dict of Sector objects
        if has_capacity(primary_candidate_sector):
            selected_sector = primary_candidate_sector
        else:
            cell_sectors = primary_candidate_sector.cell.sectors
            least_loaded_sector = get_least_loaded_sector(cell_sectors)
            selected_sector = least_loaded_sector if has_capacity(least_loaded_sector) else None
        
        if selected_sector and has_capacity(selected_sector):
            associated_cell = selected_sector.cell
            if validate_and_update_db(ue, selected_sector, associated_cell):
                ue_logger.info(f"UE {ue.ue_id} associated with Sector {selected_sector.id} and Cell {associated_cell.id}")
                return ue, selected_sector, associated_cell
            else:
                ue_logger.warning(f"Cell {associated_cell.id} capacity reached, unable to associate UE {ue.ue_id}")
    
    ue_logger.error(f"No sectors available with capacity to add UE {ue.ue_id}")
    return None, None, None