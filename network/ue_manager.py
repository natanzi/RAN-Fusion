#this is ue_manager.py inside the network folder to manage a ue
import os
from network.ue import UE
from network.utils import allocate_ues, create_ue
from Config_files.config import Config
from logs.logger_config import ue_logger

# Get base path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = Config(base_dir)
ue_config = config.ue_config

class UEManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UEManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, base_dir):
        if not hasattr(self, 'initialized'):  # This ensures __init__ is only called once
            self.config = Config(base_dir)
            self.ue_config = self.config.ue_config
            self.ues = {}  # Ensure this is a dictionary
            self.initialized = True

    @classmethod
    def get_instance(cls, base_dir):
        if not cls._instance:
            cls._instance = UEManager(base_dir)
        return cls._instance

    def initialize_ues(self, num_ues_to_launch, cells, gNodeBs, ue_config):
        """Initialize UEs and allocate them to sectors."""
        all_sectors = []
        for cell in cells.values():
            all_sectors.extend(cell.sectors)

        if not all_sectors:
            print("Error: No sectors found")
            return []

        ue_instances = allocate_ues(num_ues_to_launch, all_sectors, self.ue_config)
        # Convert list of UE instances to a dictionary with UE ID as keys
        self.ues = {ue.ID: ue for ue in ue_instances}
        return list(self.ues.values())  # Return a list of UE objects
##################################################################################
    def create_ue(self, config, **kwargs):
        # Logic to create a single UE instance
        new_ue = UE(config, **kwargs)
        self.ues[new_ue.ID] = new_ue
        return new_ue
##################################################################################
    def get_ue_by_id(self, ue_id):
        """
        Retrieve a UE instance by its ID.
        
        :param ue_id: The ID of the UE to retrieve.
        :return: The UE instance with the given ID, or None if not found.
        """
        return self.ues.get(ue_id)
##################################################################################
    def update_ue(self, ue_id, **kwargs):
        """
        Update the parameters of an existing UE.
        
        :param ue_id: The ID of the UE to update.
        :param kwargs: Parameters to update.
        :return: True if the update was successful, False otherwise.
        """
        ue = self.get_ue_by_id(ue_id)
        if ue:
            ue.update_parameters(**kwargs)
            ue_logger.info(f"UE {ue_id} updated successfully.")
            return True
        else:
            ue_logger.warning(f"UE {ue_id} not found. Update failed.")
            return False
##################################################################################
    def list_all_ues(self):
        # Now this will correctly return a list of UE IDs
        return list(self.ues.keys())
##################################################################################

# Example usage
if __name__ == "__main__":
    ue_manager = UEManager()
    config = {}  # Assuming a valid config dictionary is provided
    new_ue = ue_manager.create_ue(config, imei="123456789012345", location="Location1")
    if new_ue:
        print(f"New UE created with ID: {new_ue.ID}")
    updated = ue_manager.update_ue(new_ue.ID, location="NewLocation")
    if updated:
        print(f"UE {new_ue.ID} updated.")
    all_ues = ue_manager.list_all_ues()
    print(f"All UEs: {all_ues}")
    removed = ue_manager.remove_ue(new_ue.ID)
    if removed:
        print(f"UE {new_ue.ID} removed.")