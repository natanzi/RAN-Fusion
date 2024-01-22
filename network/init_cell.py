# init_cell.py
# Initialization of the cells in network directory
import os
import json
from .cell import Cell
from database.database_manager import DatabaseManager
from .network_state import NetworkState
from logs.logger_config import cell_logger

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs, network_state):
    from network.gNodeB import gNodeB
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))

    # Clear the network state before initializing
    network_state.clear_state()
    
    # Pre-validation to check for duplicate cell IDs in the configuration
    seen_cell_ids = set()
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        if cell_id in seen_cell_ids:
            raise ValueError(f"Duplicate cell ID {cell_id} found in cell configuration.")
        seen_cell_ids.add(cell_id)

    # Initialize Cells and link them to gNodeBs
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        # Check if the cell already exists in the network state
        if cell_id in network_state.cells:
            cell_logger.warning(f"Cell with ID {cell_id} already exists. Skipping addition.")
            continue
        # Log the cell ID before attempting to add
        cell_logger.info(f"Attempting to add cell with ID: {cell_id}")
        # Create the Cell instance
        new_cell = Cell.from_json(cell_data)
        # Add the new cell to the network state using add_cell method
        try:
            network_state.add_cell(new_cell)
            # Log the successful addition
            cell_logger.info(f"Successfully added cell with ID: {cell_id}")
        except ValueError as e:
            # Log the error if a duplicate is found
            cell_logger.error(e)
            continue  # Skip adding this cell and continue with the next

    # Initialize the DatabaseManager with the required parameters
    db_manager = DatabaseManager(network_state)
    for cell_id, cell in network_state.cells.items():
        # Serialize and write to InfluxDB
        point = cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        # Link cells to gNodeBs
        gnodeb = gNodeBs.get(cell.gNodeB_ID)
        if gnodeb:
            # Check if the gNodeB instance has the 'add_cell_to_gNodeB' method
            if not hasattr(gnodeb, 'add_cell_to_gNodeB'):
                raise AttributeError(f"gNodeB object does not have 'add_cell_to_gNodeB' method.")
            # Only link if the cell is not already linked to the gNodeB
            if not gnodeb.has_cell(cell_id):
                gnodeb.add_cell_to_gNodeB(cell, network_state)

    # Close the database connection
    db_manager.close_connection()
    return list(network_state.cells.values())