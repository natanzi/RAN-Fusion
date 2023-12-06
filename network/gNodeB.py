#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random
import time
import logging
from utils.location_utils import get_nearest_gNodeB, get_ue_location_info
from traffic.network_metrics import calculate_cell_throughput
from network.cell import Cell
from network.init_cell import initialize_cells
from .init_cell import load_json_config
from network.network_state import NetworkState
from traffic.network_metrics import calculate_cell_load
from time import sleep
from handover import handover_decision, perform_handover, handle_load_balancing, handle_qos_based_handover
from handover import handover_decision  # Import the handover function from handover.py
from .handover import handover_decision, perform_handover

# Set up logging
logging.basicConfig(filename='cell_load.log', level=logging.INFO)

def load_gNodeB_config():
    # Correct the path to point to the 'Config_files' directory
    # This assumes that 'Config_files' is a direct subdirectory of the base directory where 'main.py' is located
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'Config_files', 'gNodeB_config.json')

    with open(file_path, 'r') as file:
        return json.load(file)

# Using the function to load the configuration
gNodeBs_config = load_gNodeB_config()

class gNodeB:
    def __init__(self, gnodeb_id, latitude, longitude, coverageRadius, power, frequency, bandwidth, location, region, maxUEs, cellCount, handoverMargin, handoverHysteresis, timeToTrigger, interFreqHandover, xnInterface, sonCapabilities, loadBalancingOffset, cellIds, MeasurementBandwidth=None, BlacklistedCells=None, **kwargs):
        self.ID = gnodeb_id
        self.Latitude = latitude
        self.Longitude = longitude
        self.CoverageRadius = coverageRadius
        self.TransmissionPower = power
        self.Frequency = frequency
        self.Bandwidth = bandwidth
        self.Location = location
        self.Region = region
        self.MaxUEs = maxUEs
        self.CellCount = cellCount
        self.Cells = []  # This will hold Cell instances associated with this gNodeB
        self.HandoverMargin = handoverMargin
        self.HandoverHysteresis = handoverHysteresis
        self.TimeToTrigger = timeToTrigger
        self.InterFreqHandover = interFreqHandover
        self.XnInterface = xnInterface
        self.SONCapabilities = sonCapabilities
        self.MeasurementBandwidth = MeasurementBandwidth
        self.BlacklistedCells = BlacklistedCells
        self.LoadBalancingOffset = loadBalancingOffset
        self.CellIds = cellIds
        self.handover_success_count = 0
        self.handover_failure_count = 0

        # Handle any additional keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        print(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")
        
        # Logging statement should be here, after all attributes are set
        logging.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")
        time.sleep(1)  # Delay for 1 second
    @staticmethod
    def from_json(json_data):
        gNodeBs = []
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs.append(gnodeb)
        return gNodeBs
##################################################Cell and UE Management##########################
    def find_ue_by_id(self, ue_id):
        # Assuming self.all_ues is a method that returns a list of all UE objects
        for ue in self.all_ues():
            if ue.ID == ue_id:
                return ue
        return None    

    def delete_cell(self, cell_id):
        # Find the cell to be deleted
        cell_to_delete = next((cell for cell in self.Cells if cell.ID == cell_id), None)
        
        if cell_to_delete is None:
            print(f"No cell with ID {cell_id} found in gNodeB with ID {self.ID}")
            return
        
        # Attempt to handover UEs to other cells using the handover function from handover.py
        for ue_id in cell_to_delete.ConnectedUEs:
            ue = self.find_ue_by_id(ue_id)
            if ue:
                # Use the handover function from handover.py to make a handover decision
                new_cell = handover_decision(ue, self.Cells)  # Assuming handover_decision takes a UE and a list of Cells
                if new_cell:
                    # Perform handover to the new cell using the perform_handover method from ue.py
                    ue.perform_handover(new_cell)
                else:
                    print(f"No available cell for UE with ID {ue.ID} to handover.")
        
        # Remove the cell from the Cells list
        self.Cells.remove(cell_to_delete)
        print(f"Cell with ID {cell_id} has been deleted from gNodeB with ID {self.ID}")

    def all_ues(self):
        """
        Returns a list of all UE objects managed by this gNodeB.
        """
        all_ue_objects = []
        for cell in self.Cells:
            # Assuming each cell has a list of UE IDs in a property called ConnectedUEs
            for ue_id in cell.ConnectedUEs:
                # Assuming there is a method to find a UE by its ID
                ue = self.find_ue_by_id(ue_id)
                if ue:
                    all_ue_objects.append(ue)
        return all_ue_objects

    def find_cell_by_id(self, cell_id):
        """
        Finds a cell by its ID within the gNodeB's list of cells.

        :param cell_id: The ID of the cell to find.
        :return: The cell with the matching ID or None if not found.
        """
        return next((cell for cell in self.Cells if cell.ID == cell_id), None)
        
    def update_cell_capacity(self, new_capacity):
        # Check if the new capacity is valid
        if new_capacity < 0:
            raise ValueError("Cell capacity cannot be negative.")
        
        # Update the CellCount attribute
        self.CellCount = new_capacity
        
        # Log the change
        logging.info(f"gNodeB '{self.ID}' cell capacity updated to {self.CellCount}.")

    def add_cell_to_gNodeB(self, cell):
    # Assuming 'cell' is an instance of Cell
        if len(self.Cells) < self.CellCount:  # Use CellCount to check the capacity for cells
            self.Cells.append(cell)
            print(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")
            logging.info(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")
            time.sleep(1)  # Delay for 1 second
        else:
            print(f"gNodeB '{self.ID}' has reached its maximum cell capacity.")
##################################################################################################
#####################################Load Calculation#############################################
    def calculate_cell_load(self, cell):
        # Calculate the load based on the number of connected UEs
        ue_based_load = len(cell.ConnectedUEs) / cell.MaxConnectedUEs if cell.MaxConnectedUEs > 0 else 0
        
        # Calculate the load based on the throughput
        throughput_based_load = calculate_cell_throughput(cell, [self])  # Assuming 'self' is the only gNodeB for simplicity
        
        # Combine the UE-based load and throughput-based load for a more accurate load calculation
        # The weights (0.5 in this case) can be adjusted based on which factor is deemed more important
        combined_load = (0.5 * ue_based_load) + (0.5 * throughput_based_load)
        
        return combined_load

    def find_underloaded_cell(self):
        # Find a cell with load below a certain threshold, e.g., 50%
        for cell in self.Cells:
            if self.calculate_cell_load(cell) < 0.5:
                return cell
        return None

    def select_ues_for_load_balancing(self, overloaded_cell):
        # Select UEs to handover based on criteria like service type, data usage, etc.
        # Placeholder logic: Select a subset of UEs from the overloaded cell
        return overloaded_cell.ConnectedUEs[:len(overloaded_cell.ConnectedUEs) // 2]
    
    def find_available_cell(self, target_ue):
        """
        Finds the best available cell for a UE to handover to based on the cell load and other criteria.

        :param target_ue: The UE object that needs to be handed over.
        :return: The best target cell for handover or None if no suitable cell is found.
        """
        best_cell = None
        lowest_load = float('inf')

        # Iterate over all cells to find the one with the lowest load that is underloaded
        for cell in self.Cells:
            cell_load = self.calculate_cell_load(cell)

            # Check if the cell is underloaded and has a lower load than the current best cell
            if cell_load < 0.5 and cell_load < lowest_load:
                # Here you can add additional criteria for handover, such as signal quality, etc.
                # For now, we only check if the cell is underloaded and has the lowest load
                best_cell = cell
                lowest_load = cell_load

        return best_cell

######################################################################################################
#######################################Periodic Updates###############################################
    def update(self):
        # Call this method regularly to update handover decisions
        handle_load_balancing(self, self.calculate_cell_load, self.find_underloaded_cell, self.select_ues_for_load_balancing)
        #handle_qos_based_handover(self, self.all_ues, self.find_cell_by_id)
######################################################################################################

    # Update the database if necessary
    # db_manager = DatabaseManager()
    # db_manager.insert_cell_static_data(cell.to_dict())
    # db_manager.close_connection()

    # Update the list of available cells if there's such a function
    # update_available_cells_list(cell)

    

    
        
        # Update the database with the new capacity
        # Assuming the DatabaseManager has a method named 'update_gNodeB_cell_capacity'
        #db_manager = DatabaseManager()
        #db_manager.update_gNodeB_cell_capacity(self.ID, self.CellCount)
        #db_manager.close_connection()
        
        # Update related components if necessary
        # For example, if there is a list of available cells that needs to be updated
        # update_available_cells_list(self)