# init_cell.py
# Initialization of the cells in the network directory
import os
import json
from .cell import Cell
from datetime import datetime
from database.database_manager import DatabaseManager
from logs.logger_config import sector_logger

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs, network_state):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))
    sectors_config = load_json_config(os.path.join(config_dir, 'sector_config.json'))

    # Initialize the DatabaseManager with the required parameters
    db_manager = DatabaseManager(network_state)

    # Initialize Cells and link them to gNodeBs
    # `cells_dict` is a dictionary that stores the cells in the network. Each cell is added to the
    # dictionary with its cell ID as the key and the cell object as the value. This dictionary is used
    # to keep track of the cells in the network and is returned at the end of the `initialize_cells`
    # function.
    cells_dict = {}  # Initialize an empty dictionary for cells
    for cell_data in cells_config['cells']:
        cell_id = cell_data['cell_id']
        print(f"Attempting to add cell ID {cell_id} to network state.")
        if cell_id in cells_dict:
            print(f"Warning: Duplicate cell ID {cell_id} found in configuration. Skipping this cell.")
            continue
    
    # Find sectors for this cell
        cell_sectors = [sector['sector_id'] for sector in sectors_config['sectors'] if sector['cell_id'] == cell_id]
        if len(cell_sectors) != 3:
            raise ValueError(f"Cell ID {cell_id} does not have exactly 3 sectors. Found {len(cell_sectors)} sectors.")
    
        new_cell = Cell.from_json({**cell_data, "sectors": cell_sectors})
        cells_dict[cell_id] = new_cell  # Add the new cell to the dictionary with cell_id as key
        network_state.cells[cell_id] = new_cell

    # Initialize Sectors and print their creation details
    for sector_data in sectors_config['sectors']:
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']
        # Assuming each sector has a max capacity of 3
        max_capacity = 3
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"A sector '{sector_id}' has been created at '{creation_time}' in '{cell_id}' with max capacity {max_capacity}.")
        sector_logger.info(f"A sector '{sector_id}' has been created at '{creation_time}' in '{cell_id}' with max capacity {max_capacity}.")

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