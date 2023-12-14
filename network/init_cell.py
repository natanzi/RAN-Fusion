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

    for cell in cells:
        # Serialize and write to InfluxDB
        point = cell.serialize_for_influxdb()
        db_manager.insert_data(point)

        # Link cells to gNodeBs
        gnodeb = gNodeBs.get(cell.gNodeB_ID)
        if gnodeb:
            gnodeb.add_cell_to_gNodeB(cell)

    # Close the database connection
    db_manager.close_connection()

    return cells