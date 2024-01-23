# init_sector.py
# Initialization of the sectors in the network directory
import os
import json
from .sector import Sector  # Assuming you have a sector.py that defines the Sector class
from database.database_manager import DatabaseManager

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_sectors(cells_dict, network_state):
    print("Debug: Starting initialize_sectors function.")  # Start message

    # Determine the base directory of the current file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Construct the path to the configuration directory
    config_dir = os.path.join(base_dir, 'Config_files')
    
    print("Debug: Loading sector configuration(started..).")  # Before loading config
    # Load the sector configuration from the JSON file
    sectors_config = load_json_config(os.path.join(config_dir, 'sector_config.json'))
    print("Debug: Sector configuration loaded(finishied...).")  # After loading config

    # Initialize the DatabaseManager with the network state
    db_manager = DatabaseManager(network_state)
    
    # Iterate over each sector in the configuration
    for sector_data in sectors_config['sectors']:
        # Extract the sector ID and cell ID from the configuration data
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']
        
        print(f"Debug: Processing sector {sector_id} for cell {cell_id}.")  # Before processing each sector

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
        
        print(f"Debug: Adding sector {sector_id} to the database.")  # Before inserting data into the database
        # Serialize the new sector for InfluxDB and insert the data into the database
        point = new_sector.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Sector {sector_id} added to the database.")  # After inserting data into the database

    # Close the database connection
    db_manager.close_connection()
    print("Debug: Finished initialize_sectors function.")  # End message