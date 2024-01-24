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
    
    seen_cell_ids = set()
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        print(f"--- Read cell {cell_id} from config ---")
        if cell_id in seen_cell_ids:
            cell_logger.error(f"Duplicate cell ID {cell_id} found in cell configuration. Skipping addition.")
            print(f"Error: Duplicate cell ID {cell_id} found. Skipping addition.")
            continue
        
        seen_cell_ids.add(cell_id)
        cell_logger.info(f"Attempting to add cell with ID: {cell_id}")
        print(f"Debug: Attempting to add cell with ID: {cell_id}")
        
        new_cell = Cell(**cell_data)
        print(f"Created cell {cell_id} with memory address {id(new_cell)}")
        
        point = new_cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        print(f"Debug: Cell {new_cell.ID} data inserted into InfluxDB.")
        
        gnodeb = gNodeBs.get(new_cell.gNodeB_ID)
        if gnodeb:
            print(f"Current cells in gNodeB {gnodeb.ID} before adding: {[cell.ID for cell in gnodeb.Cells]}")
            if not gnodeb.find_cell_by_id(new_cell.ID):
                print(f"+++ Linking cell {new_cell.ID} to gNodeB {gnodeb.ID} +++")
                gnodeb.add_cell_to_gNodeB(new_cell)
                print(f"Cells in gNodeB {gnodeb.ID} after adding: {[cell.ID for cell in gnodeb.Cells]}")
            else:
                print(f"Cell {new_cell.ID} already exists in gNodeB {gnodeb.ID}, skipping addition.")
        else:
            print(f"Error: gNodeB {new_cell.gNodeB_ID} not found for cell {new_cell.ID}.")
    
    print("Debug End: initialize_cells function.")
