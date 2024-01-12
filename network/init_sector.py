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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    sectors_config = load_json_config(os.path.join(config_dir, 'sector_config.json'))

    # Initialize the DatabaseManager with the required parameters
    db_manager = DatabaseManager(network_state)

    # Initialize Sectors and link them to Cells
    for sector_data in sectors_config['sectors']:
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']
        
        # Check if the cell_id exists in the cells_dict
        if cell_id not in cells_dict:
            raise ValueError(f"Cell ID {cell_id} for sector {sector_id} not found in cells dictionary.")
        
        # Check for duplicate sector_id in the cell
        if any(sector.sector_id == sector_id for sector in cells_dict[cell_id].sectors):
            raise ValueError(f"Duplicate sector ID {sector_id} found during initialization.")
        
        # Create a new sector instance from the JSON data
        new_sector = Sector.from_json(sector_data)
        
        # Add the new sector to the corresponding cell
        cells_dict[cell_id].add_sector(new_sector)
        
        # Serialize and write to InfluxDB
        point = new_sector.serialize_for_influxdb()
        db_manager.insert_data(point)

    # Close the database connection
        db_manager.close_connection()