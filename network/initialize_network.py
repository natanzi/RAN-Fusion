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
from Config_files.config import Config  # Import the Config class
from database.database_manager import DatabaseManager  # Import DatabaseManager

def reconcile_network_with_map(network_map, cells):
    for gNodeB in network_map['gNodeBs']:
        for cell_config in gNodeB['cells']:
            cell_id = cell_config['cellId']
            if cell_id in cells:
                cell = cells[cell_id]
                sector_ids = [sector['sectorId'] for sector in cell_config['sectors']]
                cell_sector_ids = [sector.sector_id for sector in cell.sectors]
                if set(sector_ids) != set(cell_sector_ids):
                    print(f"Mismatch in sectors for cell {cell_id}. Expected: {sector_ids}, Found: {cell_sector_ids}")
            else:
                print(f"Cell {cell_id} not found in initialized network.")

def initialize_network(base_dir, num_ues_to_launch=None):
    # Create an instance of Config
    config = Config(base_dir)

    # Access the network map data
    network_map = config.network_map_data
    
    # Create an instance of DatabaseManager
    db_manager = DatabaseManager()

    # Initialize gNodeBs
    gNodeBs = initialize_gNodeBs(config.gNodeBs_config, db_manager)
    for gnb_id, gnb in gNodeBs.items():
        print(f"gNodeB ID: {gnb_id}")
        

    #Initialize Cells
    cells = initialize_cells(gNodeBs, config.cells_config, db_manager)
    if cells is not None:
        for cell_id, cell in cells.items():
            print(f"Cell ID: {cell_id}")
            
    else:
        print("No cells were initialized.")
        
    # Initialize Sectors
    sectors = initialize_sectors(config.sectors_config, cells, db_manager)
    for sector_id, sector in sectors.items():
        print(f"Sector ID: {sector_id}")
        
        
    #Reconcile the initialized network with the network map
    reconcile_network_with_map(network_map, cells)

    #Initialize UEs if num_ues_to_launch is provided
    if num_ues_to_launch:
        ues = initialize_ues(num_ues_to_launch, cells, gNodeBs, config.ue_config)
        print("Initialized UEs:")
        for ue in ues:
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Sector ID: {ue.ConnectedSector}, Cell ID: {ue.ConnectedCellID}, gNodeB ID: {ue.gNodeB_ID}")

    return gNodeBs, cells, sectors, ues