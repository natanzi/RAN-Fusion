# init_cell.py
# Initialization of the cells in network directory
import os
import json
from .cell import Cell
from logs.logger_config import cell_logger

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs, cells_config, db_manager):
    print("Debug Start: initialize_cells function.")
    cell_logger.info("Initializing cells.")
    print("Debug: Initializing cells.")

    # List all cell IDs from the configuration
    all_cell_ids = [cell_data['cell_id'] for cell_data in cells_config['cells']]
    print(f"Debug: All available cell IDs from config: {all_cell_ids}")

    seen_cell_ids = set()
    created_cells = []  # Keep track of successfully created cells

    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        if cell_id in seen_cell_ids:
            cell_logger.error(f"Duplicate cell ID {cell_id} found in cell configuration. Skipping addition.")
            print(f"Error: Duplicate cell ID {cell_id} found. Skipping addition.")
            continue

        seen_cell_ids.add(cell_id)
        cell_logger.info(f"Attempting to add cell with ID: {cell_id}")
        print(f"Debug: Attempting to add cell with ID: {cell_id}")

        # Create the cell instance
        new_cell = Cell(**cell_data)
        created_cells.append(new_cell.ID)  # Track successfully created cell
        print(f"Created cell {cell_id} with memory address {id(new_cell)}")

        # Insert cell data into the database
        point = new_cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Cell {new_cell.ID} data inserted into InfluxDB.")

        # Link the cell to its gNodeB
        gnodeb = gNodeBs.get(new_cell.gNodeB_ID)
        if gnodeb:
            print(f"Debug: Current cells in gNodeB {gnodeb.ID} before adding: {[cell.ID for cell in gnodeb.Cells]}")
            if not gnodeb.find_cell_by_id(new_cell.ID):
                gnodeb.add_cell_to_gNodeB(new_cell)
                print(f"Debug: Cell {new_cell.ID} linked to gNodeB {gnodeb.ID}")
            else:
                print(f"Warning: Cell {new_cell.ID} already exists in gNodeB {gnodeb.ID}, skipping addition.")
        else:
            print(f"Error: gNodeB {new_cell.gNodeB_ID} not found for cell {new_cell.ID}.")

    # Verify the creation of all cells
    print(f"Debug: Expected cell IDs: {all_cell_ids}")
    print(f"Debug: Created cell IDs: {created_cells}")
    if len(created_cells) == len(all_cell_ids):
        print("Success: The count and names of cells created match the list from the config.")
    else:
        print("Error: There is a mismatch in the count or names of cells created compared to the config.")

    print("Debug End: initialize_cells function.")