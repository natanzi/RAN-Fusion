# init_cell.py
# Initialization of the cells in network directory
import os
import json
from .cell import Cell
from database.database_manager import DatabaseManager
from logs.logger_config import cell_logger

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs, network_state):
    print("Debug Start: initialize_cells function.")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))

    # Initialize the DatabaseManager with the required parameters
    db_manager = DatabaseManager(network_state)
    print("Debug: DatabaseManager initialized.")

    # Explicitly clear the network state before initializing
    network_state.clear_state()
    cell_logger.info("Cleared network state before initializing cells.")
    print("Debug: Network state cleared.")

    # Pre-validation to check for duplicate cell IDs in the configuration
    seen_cell_ids = set()
    new_cells = []  # List to keep track of newly added cells
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        print(f"--- Read cell {cell_id} from config ---")
        if cell_id in seen_cell_ids:
            cell_logger.error(f"Duplicate cell ID {cell_id} found in cell configuration. Skipping addition.")
            print(f"Error: Duplicate cell ID {cell_id} found. Skipping addition.")
            continue  # Skip this cell and continue with the next
        seen_cell_ids.add(cell_id)

        # Check if the cell already exists in the network state
        if network_state.has_cell(cell_id):
            cell_logger.error(f"Cell with ID {cell_id} already exists in the network state after clearing. Skipping addition.")
            print(f"Error: Cell with ID {cell_id} already exists after clearing state. Skipping addition.")
            continue  # Skip this cell and continue with the next

        # Log the cell ID before attempting to add
        cell_logger.info(f"Attempting to add cell with ID: {cell_id}")
        print(f"Debug: Attempting to add cell with ID: {cell_id}")

        # Create the Cell instance
        new_cell = Cell.from_json(cell_data)
        new_cells.append(new_cell)  # Add the new cell to the list of new cells
        print(f"Created cell {cell_id} with memory address {id(new_cell)}")

        # Add the new cell to the network state using add_cell method
        try:
            network_state.add_cell(new_cell)
            print(f"+++ Added {cell_id} to network state +++")
            # Log the successful addition
            cell_logger.info(f"Successfully added cell with ID: {cell_id}")
        except ValueError as e:
            # Log the error if a duplicate is found
            cell_logger.error(f"Failed to add cell with ID {cell_id}: {e}")
            print(f"Error: Failed to add cell with ID {cell_id}: {e}")
            continue  # Skip adding this cell and continue with the next

    # Serialize and write new cells to InfluxDB and link them to gNodeBs
    for new_cell in new_cells:  # Iterate over the list of newly added cells
        print(f"Linking cell {new_cell.ID} with memory address {id(new_cell)} to gNodeB")
        # Serialize and write to InfluxDB
        point = new_cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Cell {new_cell.ID} data inserted into InfluxDB.")

        # Link cells to gNodeBs
        gnodeb = gNodeBs.get(new_cell.gNodeB_ID)
        if gnodeb:
            print(f"Current cells in gNodeB {gnodeb.ID} before adding: {[cell.ID for cell in gnodeb.Cells]}")
            if not gnodeb.has_cell(new_cell.ID):
                print(f"+++ Calling add_cell_to_gNodeB() for {new_cell.ID} +++")
                gnodeb.add_cell_to_gNodeB(new_cell, network_state)  # Pass network_state as an argument
                print(f"Cells in gNodeB {gnodeb.ID} after adding: {[cell.ID for cell in gnodeb.Cells]}")
            else:
                print(f"Cell {new_cell.ID} already exists in gNodeB {gnodeb.ID}, skipping addition.")
        else:
            print(f"Error: gNodeB {new_cell.gNodeB_ID} not found for cell {new_cell.ID}.")

    # Close the database connection
    db_manager.close_connection()
    print("Debug: Database connection closed.")
    print("Debug End: initialize_cells function.")