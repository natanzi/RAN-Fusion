#sector_manager.py inside the network folder SectorManager class can centralize the management of sectors, including their initialization, updates, and the handling of User Equipment (UE) associations. This approach can streamline interactions with the database and ensure consistent state management across the application.
# sector_manager.py
from network.sector import Sector, all_sectors
from database.database_manager import DatabaseManager
from influxdb_client import Point, WritePrecision
from logs.logger_config import cell_logger, gnb_logger, ue_logger, sector_logger

import threading

class SectorManager:
    def __init__(self, db_manager):
        self.sectors = all_sectors  # Use the global all_sectors dictionary to track sectors
        self.db_manager = db_manager  # Instance of DatabaseManager for DB operations
        self.lock = threading.Lock()  # Lock for thread-safe operations on sectors

    def initialize_sectors(self, sectors_config, cells):
        initialized_sectors = {}
        processed_sectors = set()

        # Validate cells before allocation
        required_cell_ids = {sector_data['cell_id'] for sector_data in sectors_config['sectors']}
        for cell_id in required_cell_ids:
            if cell_id not in cells:
                print(f"Cell {cell_id} not initialized, cannot allocate sectors.")
                return  # Skip sector allocation for this cell

        for sector_data in sectors_config['sectors']:
            sector_id = sector_data['sector_id']
            cell_id = sector_data['cell_id']
            sector_cell_combo = (cell_id, sector_id)
            if sector_cell_combo in processed_sectors:
                print(f"Sector {sector_id} already processed for Cell {cell_id}. Skipping.")
                continue

            processed_sectors.add(sector_cell_combo)
            cell = cells[cell_id]

            with self.lock:
                if sector_id not in self.sectors:
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
                        cell.add_sector_to_cell(new_sector)
                        self.sectors[new_sector.sector_id] = new_sector
                        initialized_sectors[new_sector.sector_id] = new_sector
                        point = new_sector.serialize_for_influxdb()
                        self.db_manager.insert_data(point)
                        print(f"Sector {new_sector.sector_id} initialized and added.")
                    except ValueError as e:
                        cell_logger.warning(str(e))
                else:
                    print(f"Sector {sector_id} already exists in the manager.")

        print("Sectors initialization completed.")
        return initialized_sectors



    def add_ue_to_sector(self, sector_id, ue):
        with self.lock:  # Use the SectorManager's lock for thread safety
            sector = self.sectors.get(sector_id)
            if sector:
                if len(sector.connected_ues) >= sector.capacity:
                    sector_logger.warning(f"Sector {sector_id} at max capacity! Cannot add UE {ue.ID}")
                elif ue.ID not in sector.connected_ues:
                    sector.connected_ues.append(ue.ID)  # Store only the ID, not the UE object
                    sector.current_load += 1  # Increment the current load
                    global_ue_ids.add(ue.ID)  # Add the UE ID to the global list
                    sector.remaining_capacity = sector.capacity - len(sector.connected_ues)  # Update remaining_capacity
                    ue.ConnectedCellID = sector.cell_id
                    ue.gNodeB_ID = sector.cell.gNodeB_ID
                    sector.ues[ue.ID] = ue
                    global_ue_ids.add(ue.ID)
                    point = sector.serialize_for_influxdb()
                    self.db_manager.insert_data(point)  # Use SectorManager's db_manager to insert data
                    sector_logger.info(f"UE with ID {ue.ID} has been added to the sector {sector_id}. Current load: {sector.current_load}")
                else:
                    sector_logger.warning(f"UE with ID {ue.ID} is already connected to the sector {sector_id}.")
            else:
                print(f"Sector {sector_id} not found.")

    def remove_ue_from_sector(self, sector_id, ue_id):
        with self.lock:  # Use the SectorManager's lock for thread safety
            sector = self.sectors.get(sector_id)
            if sector and ue_id in sector.connected_ues:
                sector.connected_ues.remove(ue_id)  # Correctly remove the ID string
                sector.current_load -= 1  # Decrement the current load
                global_ue_ids.discard(ue_id)  # Correctly discard the ID string
                sector.remaining_capacity = sector.capacity - len(sector.connected_ues)  # Update remaining_capacity
                del sector.ues[ue_id]  # Correctly delete the UE from the dictionary
                point = sector.serialize_for_influxdb()
                self.db_manager.insert_data(point)  # Use SectorManager's db_manager to insert data
                sector_logger.info(f"UE with ID {ue_id} has been removed from the sector {sector_id}. Current load: {sector.current_load}")
            else:
                sector_logger.warning(f"UE with ID {ue_id} is not connected to the sector {sector_id}.")

    def update_sector(self, sector_id, updates):
        """
        Updates properties of a specified sector.
        :param sector_id: ID of the sector to update.
        :param updates: Dictionary containing updates (property: new_value).
        """
        with self.lock:
            sector = self.sectors.get(sector_id)
            if sector:
                for key, value in updates.items():
                    if hasattr(sector, key):
                        setattr(sector, key, value)
                        print(f"Sector {sector_id} property {key} updated to {value}.")
                    else:
                        print(f"Sector {sector_id} has no property {key}.")
                # Optionally, serialize and update the sector in the database
                self.db_manager.insert_data(sector.serialize_for_influxdb())
            else:
                print(f"Sector {sector_id} not found.")

    def get_sector_state(self, sector_id):
        """
        Queries the database for the current state of a sector.
        :param sector_id: ID of the sector to query.
        :return: Sector state or None if not found.
        """
        # Implementation depends on the structure of your database and data model
        # This is a placeholder for the database query logic
        sector_state = self.db_manager.query_sector_state(sector_id)
        return sector_state

# Example usage
#if __name__ == "__main__":
# sector_manager = SectorManager()
    # Example sector_data and cell object need to be provided based on your application's structure
    # sector_manager.initialize_sector(sector_data, cell)
    # sector_manager.add_ue_to_sector("sector_id", ue)
    # sector_manager.remove_ue_from_sector("sector_id", "ue_id")
    # sector_manager.update_sector("sector_id", {"property": "new_value"})