#sector_manager.py inside the network folder SectorManager class can centralize the management of sectors, including their initialization, updates, and the handling of User Equipment (UE) associations. This approach can streamline interactions with the database and ensure consistent state management across the application.
# sector_manager.py
from network.sector import Sector, all_sectors
from database.database_manager import DatabaseManager
import threading

class SectorManager:
    def __init__(self):
        self.sectors = all_sectors  # Use the global all_sectors dictionary to track sectors
        self.db_manager = DatabaseManager()  # Instance of DatabaseManager for DB operations
        self.lock = threading.Lock()  # Lock for thread-safe operations on sectors

    def initialize_sector(self, sector_data, cell):
        """
        Initializes a new sector from provided data and adds it to the sectors dictionary.
        :param sector_data: Dictionary containing data to initialize a sector.
        :param cell: Cell object to which the sector belongs.
        """
        with self.lock:
            if sector_data['sector_id'] not in self.sectors:
                new_sector = Sector.from_json(sector_data, cell)
                self.sectors[new_sector.sector_id] = new_sector
                # Optionally, serialize and insert the new sector into the database
                self.db_manager.insert_data(new_sector.serialize_for_influxdb())
                print(f"Sector {new_sector.sector_id} initialized and added.")
            else:
                print(f"Sector {sector_data['sector_id']} already exists.")

    def add_ue_to_sector(self, sector_id, ue):
        """
        Adds a UE to a specified sector.
        :param sector_id: ID of the sector to which the UE will be added.
        :param ue: UE object to add to the sector.
        """
        with self.lock:
            sector = self.sectors.get(sector_id)
            if sector:
                sector.add_ue(ue)
                print(f"UE {ue.ID} added to sector {sector_id}.")
            else:
                print(f"Sector {sector_id} not found.")

    def remove_ue_from_sector(self, sector_id, ue_id):
        """
        Removes a UE from a specified sector.
        :param sector_id: ID of the sector from which the UE will be removed.
        :param ue_id: ID of the UE to remove from the sector.
        """
        with self.lock:
            sector = self.sectors.get(sector_id)
            if sector and ue_id in sector.ues:
                sector.remove_ue(ue_id)
                print(f"UE {ue_id} removed from sector {sector_id}.")
            else:
                print(f"Sector {sector_id} or UE {ue_id} not found.")

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