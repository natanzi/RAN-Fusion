# init_sector.py
# Initialization of the sectors in the network directory
import os
from .sector import Sector
from database.database_manager import DatabaseManager
from utills.debug_utils import debug_print

def initialize_sectors(sectors_config, cells, db_manager):
    initialized_sectors = {}  # Dictionary to keep track of initialized sectors
    
    for sector_data in sectors_config['sectors']:
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']
        
        # Check if the cell ID exists in the provided cells dictionary
        if cell_id not in cells:
            print(f"Error: Cell ID {cell_id} for sector {sector_id} not found.")
            continue
        
        # Retrieve the corresponding cell object
        cell = cells[cell_id]
        
        # Check if the sector already exists in the cell
        if sector_id in [sector.sector_id for sector in cell.sectors]:
            print(f"Warning: Sector with ID {sector_id} already exists in Cell {cell_id}. Skipping.")
            continue
        
        # Use the from_json class method to create a Sector instance
        # This method correctly handles the sector data and the cell object
        new_sector = Sector.from_json(sector_data, cell)
        
        # Add the new sector to the corresponding cell
        cell.add_sector(new_sector)
        
        # Keep track of the initialized sector
        initialized_sectors[sector_id] = new_sector
        
        # Serialize the sector data for database insertion
        point = new_sector.serialize_for_influxdb()
        db_manager.insert_data(point)
    
    print("Sectors initialization completed.")
    return initialized_sectors