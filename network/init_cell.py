# init_cell.py
# Initialization of the cells in network directory
import os
import json
from .cell import Cell
from database.database_manager import DatabaseManager

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs, network_state):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))

    # Initialize the DatabaseManager with the required parameters
    db_manager = DatabaseManager(network_state)

    # Initialize Cells and link them to gNodeBs
    cells = [Cell.from_json(cell_data) for cell_data in cells_config['cells']]

    # Prepare a list for batch insertion
    cell_data_points = []

    # Collect static cell data into the list for batch insertion
    for cell in cells:
        cell_data = cell.to_dict()
        gnodeb_id = cell_data.pop('gNodeB_ID', None)
        
        # Add a 'measurement' key to cell_data
        cell_data['measurement'] = 'cell_measurement'  # Replace 'cell_measurement' with your actual measurement name
        
        # Add a 'fields' key to cell_data with the necessary fields
        cell_data['fields'] = {
            # Add your cell data fields here. For example:
            'max_capacity': cell_data['max_capacity']
        }
        
        # Remove the 'max_capacity' from the main dictionary as it's now in 'fields'
        cell_data.pop('max_capacity', None)
        
        # Instead of inserting here, we add the data to the list
        cell_data_points.append(cell_data)
        
        # Link cells to gNodeBs
        for gnodeb_key, gnodeb in gNodeBs.items():
            if gnodeb_id == gnodeb_key:
                gnodeb.add_cell_to_gNodeB(cell)

    # Use the new batch insert method
    db_manager.insert_data_batch(cell_data_points)

    # Close the database connection
    db_manager.close_connection()

    return cells