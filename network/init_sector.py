# init_sector.py
# Initialization of the sectors in the network directory
import os
from .sector import Sector  # Assuming you have a sector.py that defines the Sector class
from database.database_manager import DatabaseManager
from threading import Lock

sector_lock = Lock()

def initialize_sectors(cells_dict, sectors_config, db_manager):
    print("Debug: Starting initialize_sectors function.")  # Start message

    # Iterate over each sector in the configuration
    for sector_data in sectors_config['sectors']:
        # Extract the sector ID and cell ID from the configuration data
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']
        print(f"Debug: Processing sector {sector_id} for cell {cell_id}.")  # Before processing each sector

        with sector_lock:  # Acquire the lock for thread-safe operations
            # Check if the cell ID exists in the provided cells dictionary
            if cell_id not in cells_dict:
                raise ValueError(f"Cell ID {cell_id} for sector {sector_id} not found in cells dictionary.")

            # Check for duplicate sector ID within the same cell
            if any(sector.sector_id == sector_id for sector in cells_dict[cell_id].sectors):
                raise ValueError(f"Duplicate sector ID {sector_id} found during initialization.")

            # Create a new Sector instance from the JSON data
            new_sector = Sector.from_json(sector_data)

            # Add the new sector to the corresponding cell in the cells dictionary
            cells_dict[cell_id].add_sector(new_sector)

        # Serialize the new sector for InfluxDB and insert the data into the database
        # This is done outside of the lock to not hold the lock during I/O operations
        print(f"Debug: Adding sector {sector_id} to the database.")  # Before inserting data into the database
        point = new_sector.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Sector {sector_id} added to the database.")  # After inserting data into the database

    print("Debug: Finished initialize_sectors function.")  # End message