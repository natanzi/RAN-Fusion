import os
import logging
from Config_files.config_load import load_all_configs
from logo import create_logo
from network.init_gNodeB import initialize_gNodeBs
from network.init_cell import initialize_cells
from network.init_sector import initialize_sectors
from network.init_ue import initialize_ues
from database.database_manager import DatabaseManager

def main():
    logo_text = create_logo()
    print(logo_text)
    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config, sectors_config = load_all_configs(base_dir)
    
    # Create an instance of DatabaseManager here
    db_manager = DatabaseManager()
    
    num_ues_to_launch = 10
    
    # Initialize gNodeBs
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)
    print("Initialized gNodeBs:")
    for gnb_id, gnb in gNodeBs.items():
        print(f"gNodeB ID: {gnb_id}, Details: {gnb}")
    
    # Initialize Cells
    # Ensure cells_config has the 'cells' key
    if 'cells' not in cells_config:
        raise KeyError("cells_config is missing 'cells' key")
    cells = initialize_cells(gNodeBs, cells_config, db_manager)
    
    # Check if cells is not None before iterating
    if cells is not None:
        print("Initialized Cells:")
        for cell_id, cell in cells.items():
            print(f"Cell ID: {cell_id}, Details: {cell}")
    else:
        print("No cells were initialized.")
        cells = {}  # Initialize cells as an empty dictionary if None was returned
    
    # Initialize Sectors
    try:
        sectors = initialize_sectors(sectors_config['sectors'], cells, db_manager)
    except KeyError as e:
        logging.error(f"Failed to initialize sectors: {e}")
        sectors = {}  # Initialize sectors as an empty dictionary if an exception occurred

    print("Initialized Sectors:")
    for sector_id, sector in sectors.items():
        print(f"Sector ID: {sector_id}, Details: {sector}")

    # Initialize UEs
    # The db_manager argument is removed from the call to match the function signature
    ues = initialize_ues(num_ues_to_launch, sectors, ue_config)

    print("Initialized UEs:")
    for ue in ues:
        print(f"UE ID: {ue.ID}, Sector ID: {ue.ConnectedSectorID}, Service Type: {ue.ServiceType}")

if __name__ == "__main__":
    main()