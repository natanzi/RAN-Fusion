#this is ue_manager.py inside the network folder to manage a ue
import os
from network.ue import UE
from network.utils import allocate_ues, create_ue
from Config_files.config import Config
from logs.logger_config import ue_logger
from network.sector_manager import SectorManager
from traffic.traffic_generator import TrafficController

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
        # Assuming ue_id is an integer and UEs are stored with their ID as the key
        ue = self.ues.get(ue_id)
        if ue is None:
            print(f"UE with ID {ue_id} not found.")  # Example print message for debugging
        return ue
##################################################################################
    def update_ue(self, ue_id, **kwargs):
        """
        Update the parameters of an existing UE.
        
        :param ue_id: The ID of the UE to update.
        :param kwargs: Parameters to update.
        :return: True if the update was successful, False otherwise.
        """
        ue = self.get_ue_by_id(ue_id)
        print(f"UE instance found for ID {ue_id}: {ue}")
        if ue:
            ue.update_parameters(**kwargs)
            ue_logger.info(f"UE {ue_id} updated successfully.")
            return True
        else:
            print(f"UE {ue_id} not found")
            ue_logger.warning(f"UE {ue_id} not found. Update failed.")
            return False
##################################################################################
    def list_all_ues(self):
        # Now this will correctly return a list of UE IDs
        return list(self.ues.keys())
#################################################################################
    def delete_ue(self, ue_id):
        # Retrieve the UE instance
        ue = self.get_ue_by_id(ue_id)
        if ue is None:
            print(f"UE with ID {ue_id} not found.")
            return False

        # Assuming you have a way to access the SectorManager instance
        # This might involve importing SectorManager and getting its instance
        sector_manager = SectorManager.get_instance()

        # Remove the UE from its connected sector
        sector_id = ue.ConnectedSectorID  # Assuming UE has attribute ConnectedSectorID
        if sector_manager.remove_ue_from_sector(sector_id, ue_id):
            print(f"UE {ue_id} successfully removed from sector {sector_id}.")
            # Now, delete the UE instance from UEManager's ues dictionary
            del self.ues[ue_id]
            # Perform any additional cleanup here (if necessary)
            return True
        else:
            print(f"Failed to remove UE {ue_id} from sector {sector_id}.")
            return False
#################################################################################
    def stop_ue_traffic(self, ue_id):
        """Stop traffic generation for the given UE"""
        ue = self.get_ue_by_id(ue_id)
        
        if not ue:
            print(f"UE {ue_id} not found")
            return
        # Get reference to traffic generator 
        traffic_controller = TrafficController.get_instance()
        if ue.generating_traffic:
            traffic_controller.stop_ue_traffic(ue)
            ue.generating_traffic = False
            ue.throughput = 0
            print(f"Traffic stopped for UE {ue_id}")
        else:
            print(f"UE {ue_id} does not have active traffic generation")