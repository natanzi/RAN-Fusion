# initialize_network.py
# Initialization of gNodeBs, Cells, sectors, and UEs
# This file is located in the network directory
from network.gNodeB_manager import gNodeBManager  
from network.cell_manager import CellManager  
from network.sector_manager import SectorManager  
from network.ue_manager import UEManager  
from logs.logger_config import ue_logger
from Config_files.config import Config  
from database.database_manager import DatabaseManager  

def reconcile_network_with_map(network_map, cell_manager):
    # Adjusted to use cell_manager for cell retrieval
    for gNodeB in network_map['gNodeBs']:
        for cell_config in gNodeB['cells']:
            cell_id = cell_config['cellId']
            cell = cell_manager.get_cell(cell_id)
            if cell:
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

    # Initialize gNodeBs using gNodeBManager
    gnodeb_manager = gNodeBManager(db_manager)
    gNodeBs = gnodeb_manager.initialize_gNodeBs()

    # Initialize Cells using CellManager
    cell_manager = CellManager(gNodeBs, db_manager)
    cells = cell_manager.initialize_cells(config.cells_config)

    # Initialize Sectors using SectorManager
    sector_manager = SectorManager(db_manager)
    sectors = sector_manager.initialize_sectors(config.sectors_config, cells)

    reconcile_network_with_map(network_map, cell_manager)

    # Initialize UEs if num_ues_to_launch is provided, using UEManager
    if num_ues_to_launch:
        ue_manager = UEManager(db_manager)
        ues = ue_manager.initialize_ues(num_ues_to_launch, cells, gNodeBs, config.ue_config)
        print("Initialized UEs:")
        for ue in ues:
                print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Sector ID: {ue.ConnectedSector}, Cell ID: {ue.ConnectedCellID}, gNodeB ID: {ue.gNodeB_ID}")

    return gNodeBs#, cells, sectors, ues