# init_sector.py
# Initialization of the sectors in the network directory
import os
from .sector import Sector
from database.database_manager import DatabaseManager
from utills.debug_utils import debug_print

def initialize_sectors(sectors_config, cells, db_manager):
    # Print to validate sector config
    debug_print(f"Sector config keys: {sectors_config.keys()}")

    
    # Validate sectors key exists
    if 'sectors' not in sectors_config:
        raise KeyError("The key 'sectors' is missing from the sectors configuration.")
    
    # Get sectors list from config
    sectors_list = sectors_config['sectors']
    
    # Dictionary to hold initialized sectors
    initialized_sectors = {}
    
    # Iterate over each sector
    for sector_data in sectors_list:
        # Get sector ID and cell ID from data
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']
        print(f"Debug: Processing sector {sector_id} for cell {cell_id}.")
        
        # Check if cell ID exists in cells dict
        if cell_id not in cells:
            raise ValueError(f"Cell ID {cell_id} for sector {sector_id} not found in cells dictionary.")
        
        # Check for duplicate sector IDs
        if any(sector.sector_id == sector_id for sector in cells[cell_id].sectors):
            raise ValueError(f"Duplicate sector ID {sector_id} found during initialization.")
        
        # Retrieve the cell object using cell_id
        cell = cells[cell_id]
        
        # Create Sector instance from data, passing the cell object as an argument
        new_sector = Sector.from_json(sector_data, cell)
        
        # Add new sector to Cell
        cells[cell_id].add_sector(new_sector)
        
        # Add new sector to the initialized_sectors dictionary
        initialized_sectors[sector_id] = new_sector
        
        # Insert sector data into InfluxDB
        point = new_sector.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Sector {sector_id} added to database")
    
    print("Debug: Finished initialize_sectors function.")
    return initialized_sectors