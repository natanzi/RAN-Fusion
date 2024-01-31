# init_sector.py
# Initialization of the sectors in the network directory

import os
from .sector import Sector
from logs.logger_config import cell_logger

def initialize_sectors(sectors_config, cells, db_manager):
    initialized_sectors = {}
    processed_sectors = set()

    for sector_data in sectors_config['sectors']:
        sector_id = sector_data['sector_id']
        cell_id = sector_data['cell_id']

        sector_cell_combo = (cell_id, sector_id)

        if sector_cell_combo in processed_sectors:
            print(f"Sector {sector_id} already processed for Cell {cell_id}. Skipping.")
            continue

        processed_sectors.add(sector_cell_combo)

        if cell_id not in cells:
            print(f"Cell {cell_id} not found.")
            continue

        cell = cells[cell_id]

        # Construct Sector instance passing all required arguments
        new_sector = Sector(
            sector_id=sector_data['sector_id'],
            cell_id=sector_data['cell_id'],
            capacity=sector_data['capacity'],
            azimuth_angle=sector_data['azimuth_angle'],
            beamwidth=sector_data['beamwidth'],
            frequency=sector_data['frequency'],
            duplex_mode=sector_data['duplex_mode'],
            tx_power=sector_data['tx_power'],
            bandwidth=sector_data['bandwidth'],
            mimo_layers=sector_data['mimo_layers'],
            beamforming=sector_data['beamforming'],
            ho_margin=sector_data['ho_margin'],
            load_balancing=sector_data['load_balancing'],
            cell=cell
        )

        try:
            # Use the add_sector_to_cell method to add the sector
            cell.add_sector_to_cell(new_sector, cell_id)
        except ValueError as e:
            # Handle exceptions, such as when the cell is not found or the sector already exists
            cell_logger.warning(str(e))

        initialized_sectors[new_sector.sector_id] = new_sector

        point = new_sector.serialize_for_influxdb()
        db_manager.insert_data(point)

    print("Sectors initialization completed.")
    return initialized_sectors