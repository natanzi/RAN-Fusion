# init_cell.py
# Initialization of the cells
import os
import json
from .cell import Cell
from database.database_manager import DatabaseManager

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_cells(gNodeBs):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')
    cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))

    # Initialize the DatabaseManager with the required parameters and connect to the database
    db_manager = DatabaseManager()
    db_manager.connect()

    # Initialize Cells and link them to gNodeBs
    cells = [Cell.from_json(cell_data) for cell_data in cells_config['cells']]

    # Insert static cell data into the database and link cells to gNodeBs
    for cell in cells:
        db_manager.insert_cell_static_data(cell.__dict__)
        for gnodeb in gNodeBs:
            if cell.gNodeB_ID == gnodeb.ID:
                gnodeb.add_cell(cell)  # Use the add_cell method of gNodeB

    # Close the database connection
    db_manager.close_connection()

    return cells