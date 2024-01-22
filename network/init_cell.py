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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))

    # Initialize the DatabaseManager with the required parameters
    db_manager = DatabaseManager(network_state)

    # Explicitly clear the network state before initializing
    network_state.clear_state()
    cell_logger.info("Cleared network state before initializing cells.")

    # Pre-validation to check for duplicate cell IDs in the configuration
    seen_cell_ids = set()
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        print(f"--- Read cell {cell_id} from config ---")
        if cell_id in seen_cell_ids:
            cell_logger.error(f"Duplicate cell ID {cell_id} found in cell configuration. Skipping addition.")
            continue  # Skip this cell and continue with the next
        seen_cell_ids.add(cell_id)

    # Initialize Cells and link them to gNodeBs
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        print(f"teesssst---Read cell {cell_id} from config")
        # Check if the cell already exists in the network state
        if network_state.has_cell(cell_id):
            cell_logger.error(f"Cell with ID {cell_id} already exists in the network state after clearing. Skipping addition.")
            continue  # Skip this cell and continue with the next

        # Log the cell ID before attempting to add
        cell_logger.info(f"Attempting to add cell with ID: {cell_id}")

        # Create the Cell instance
        new_cell = Cell.from_json(cell_data)
        print(f"tesst-Created cell {cell_id}")
        # Add the new cell to the network state using add_cell method
        try:
            network_state.add_cell(new_cell)
            print(f"+++ Added {cell_id} to network state +++")
            # Log the successful addition
            cell_logger.info(f"Successfully added cell with ID: {cell_id}")
        except ValueError as e:
            # Log the error if a duplicate is found
            cell_logger.error(f"Failed to add cell with ID {cell_id}: {e}")
            continue  # Skip adding this cell and continue with the next

    # Serialize and write new cells to InfluxDB and link them to gNodeBs
    for new_cell in network_state.cells.values():
        print(f"tesss-Linking cell {new_cell} to gNodeB")
        # Serialize and write to InfluxDB
        point = new_cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        # Link cells to gNodeBs
        gnodeb = gNodeBs.get(new_cell.gNodeB_ID)
        if gnodeb and not gnodeb.has_cell(new_cell.ID):
            print(f"+++ Calling add_cell() for {cell_id} +++")
            gnodeb.add_cell_to_gNodeB(new_cell, network_state)

    # Close the database connection
    db_manager.close_connection()