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
    cells_dict = {}  # Initialize an empty dictionary for cells
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        if cell_id in network_state.cells:
            raise ValueError(f"Duplicate cell ID {cell_id} found during initialization.")
        new_cell = Cell.from_json(cell_data)
        cells_dict[cell_id] = new_cell  # Add the new cell to the dictionary with cell_id as key
        network_state.cells[cell_id] = new_cell

    # Update the network state with the new cells
    network_state.update_state(gNodeBs, cells_dict, network_state.ues)  # Assuming ues is already a part of network_state

    for cell_id, cell in cells_dict.items():
        # Serialize and write to InfluxDB
        point = cell.serialize_for_influxdb()
        db_manager.insert_data(point)
        # Link cells to gNodeBs
        gnodeb = gNodeBs.get(cell.gNodeB_ID)
        if gnodeb:
            gnodeb.add_cell_to_gNodeB(cell)

    # Close the database connection
    db_manager.close_connection()

    return cells_dict  # Return the dictionary instead of list
