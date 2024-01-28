# init_cell.py
# Initialization of the cells in network directory
import os
import json
from .cell import Cell
from logs.logger_config import cell_logger
from utills.debug_utils import debug_print

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs, cells_config, db_manager,config):
    debug_print("Debug Start: initialize_cells function.")
    cell_logger.info("Initializing cells.")
    print("Debug: Initializing cells.")

    # List all cell IDs from the configuration
    all_cell_ids = [cell_data['cell_id'] for cell_data in cells_config['cells']]
    print(f"Debug: All available cell IDs from config: {all_cell_ids}")

    seen_cell_ids = set()
    created_cells_dict = {}  # Change to dictionary to track successfully created cells

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
        created_cells_dict[cell_id] = new_cell  # Track successfully created cell using cell_id as key
        print(f"Created cell {cell_id} with memory address {id(new_cell)}")

        # Attempt to add the cell to the corresponding gNodeB
        try:
            gNodeB_id = cell_data['gnodeb_id']  # Use the correct key from the JSON configuration
            if gNodeB_id in gNodeBs:
                gNodeBs[gNodeB_id].add_cell_to_gNodeB(new_cell)
                print(f"Debug: Cell {cell_id} added to gNodeB {gNodeB_id}")
            else:
                print(f"Error: gNodeB {gNodeB_id} not found for cell {cell_id}")
        except KeyError:
            print(f"Error: 'gnodeb_id' key not found for cell {cell_id}. Cannot add cell to gNodeB.")


        # Insert cell data into the database
        point = new_cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Cell {new_cell.ID} data inserted into InfluxDB.")

    # Verify the creation of all cells
    print(f"Debug: Expected cell IDs: {all_cell_ids}")
    created_cell_ids = list(created_cells_dict.keys())
    print(f"Debug: Created cell IDs: {created_cell_ids}")
    if len(created_cell_ids) == len(all_cell_ids):
        print("Success: The count and names of cells created match the list from the config.")
    else:
        print("Error: There is a mismatch in the count or names of cells created compared to the config.")

    print("Debug End: initialize_cells function.")
    return created_cells_dict  # Return the dictionary of created cells