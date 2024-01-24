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
    gNodeBs_config, cells_config, ue_config, sector_config = load_all_configs(base_dir)
    
    # Create an instance of DatabaseManager here
    db_manager = DatabaseManager()

    num_ues_to_launch = 10

    # Initialize gNodeBs
    gNodeBs = initialize_gNodeBs(gNodeBs_config, db_manager)

    print("Initialized gNodeBs:")
    for gnb_id, gnb in gNodeBs.items():
        print(f"gNodeB ID: {gnb_id}, Details: {gnb}")

    # Initialize Cells
    cells = initialize_cells(gNodeBs)
    print("Initialized Cells:")
    for cell_id, cell in cells.items():
        print(f"Cell ID: {cell_id}, Details: {cell}")

    # Initialize Sectors
    sectors = initialize_sectors(cells)
    print("Initialized Sectors:")
    for sector_id, sector in sectors.items():
        print(f"Sector ID: {sector_id}, Details: {sector}")

    # Initialize UEs
    ues = initialize_ues(num_ues_to_launch, sectors, ue_config)
    print("Initialized UEs:")
    for ue in ues:
        print(f"UE ID: {ue.ID}, Sector ID: {ue.sector.ID}, Service Type: {ue.ServiceType}")

if __name__ == "__main__":
    main()