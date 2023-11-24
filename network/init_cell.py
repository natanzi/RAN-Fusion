# init_cell.py
# Initialization of the cells

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
    cells = []
    for cell_data in cells_config['cells']:
        cell = Cell(
            cell_id=cell_data['cell_id'],
            gnodeb_id=cell_data['gnodeb_id'],
            frequencyBand=cell_data['frequencyBand'],
            duplexMode=cell_data['duplexMode'],
            tx_power=cell_data['tx_power'], 
            bandwidth=cell_data['bandwidth'],
            ssb_periodicity=cell_data['ssbPeriodicity'], 
            ssb_offset=cell_data['ssbOffset'],
            max_connect_ues=cell_data['maxConnectUes'],
            channel_model=cell_data['channelModel'],
            trackingArea=cell_data.get('trackingArea', None)
        )
        cells.append(cell)

        # Insert static cell data into the database
        db_manager.insert_cell_static_data({
            'cell_id': cell_data['cell_id'],
            'gnodeb_id': cell_data['gnodeb_id'],
            'frequencyBand': cell_data['frequencyBand'],
            'duplexMode': cell_data['duplexMode'],
            'tx_power': cell_data['tx_power'], 
            'bandwidth': cell_data['bandwidth'],
            'ssb_periodicity': cell_data['ssbPeriodicity'], 
            'ssb_offset': cell_data['ssbOffset'],
            'max_connect_ues': cell_data['maxConnectUes'],
            'channel_model': cell_data['channelModel'],
            'trackingArea': cell_data.get('trackingArea', None)
        })

    # Link cells to their respective gNodeBs
    for cell in cells:
        for gnodeb in gNodeBs:
            if cell.gnodeb_id == gnodeb.ID:
                gnodeb.add_cell(cell)  # Use the add_cell method of gNodeB

    # Close the database connection
    db_manager.close_connection()

    return cells

# The function initialize_cells should be called from initialize_network.py or similar