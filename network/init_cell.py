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

def initialize_cells(gNodeBs, cells_config, db_manager):
    cell_logger.info("Initializing cells.")
    cells = {}  # Initialize an empty dictionary to hold cell instances
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        gNodeB_id = cell_data['gnodeb_id']
        if gNodeB_id not in gNodeBs:
            print(f"Error: gNodeB {gNodeB_id} not found for cell {cell_id}")
            continue
        
        new_cell = Cell(**cell_data)
        
        # Assuming add_cell_to_gNodeB method correctly adds the cell to the gNodeB and updates any necessary state
        gNodeBs[gNodeB_id].add_cell_to_gNodeB(new_cell)
        
        # Add the new cell to the cells dictionary
        cells[cell_id] = new_cell
        
        # Assuming serialize_for_influxdb prepares data for database insertion
        point = new_cell.serialize_for_influxdb()
        db_manager.insert_data(point)
    
    print("Cells initialization completed.")
    return cells  # Return the dictionary of cells