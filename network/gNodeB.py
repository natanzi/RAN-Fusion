#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random
import logging
from utils.location_utils import get_nearest_gNodeB, get_ue_location_info
from traffic.network_metrics import calculate_cell_throughput
from network.cell import Cell
from network.gNodeB import load_gNodeB_config, gNodeB
from network.init_cell import initialize_cells
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

        # Handle any additional keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        print(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")
        
        # Logging statement should be here, after all attributes are set
        logging.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")

    @staticmethod
    def from_json(json_data):
        gNodeBs = []
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs.append(gnodeb)
        return gNodeBs

    def add_cell_to_gNodeB(cell_name, gnodeb_target_id):
        # Load the existing gNodeBs configuration
        gNodeBs_config = load_gNodeB_config()
    
        # Initialize gNodeBs from the configuration
        gNodeBs = gNodeB.from_json(gNodeBs_config)

        # Find the target gNodeB by ID
        target_gNodeB = next((gnodeb for gnodeb in gNodeBs if gnodeb.ID == gnodeb_target_id), None)
    
        if target_gNodeB is None:
            print(f"gNodeB with ID '{gnodeb_target_id}' not found.")
            return

        # Load the cell configurations
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(base_dir, 'Config_files')
        cells_config = load_json_config(os.path.join(config_dir, 'cell_config.json'))

        # Find the cell configuration by name
        cell_config = next((config for config in cells_config['cells'] if config['cell_id'] == cell_name), None)
        if cell_config is None:
            print(f"No configuration found for cell '{cell_name}'.")
            return

        # Create a new Cell instance from the configuration
        new_cell = Cell.from_json(cell_config)

        # Add the cell to the target gNodeB
        target_gNodeB.add_cell(new_cell)
        print(f"Cell '{cell_name}' has been added to gNodeB '{gnodeb_target_id}'.")

        # Update the database if necessary
        # db_manager = DatabaseManager()
        # db_manager.insert_cell_static_data(new_cell.to_dict())
        # db_manager.close_connection()

        # Update the list of available cells if there's such a function
        # update_available_cells_list(new_cell)

        return new_cell

    def handover_decision(self, ue):
        # Placeholder logic for deciding if a handover is needed
        current_cell = next((cell for cell in self.Cells if cell.ID == ue.ConnectedCellID), None)
        if current_cell and not self.check_cell_capacity(current_cell):
            new_cell = self.find_available_cell()
            if new_cell:
                return new_cell
        return None

    def perform_handover(self, ue):
        new_cell = self.handover_decision(ue)
        if new_cell:
            # Update the UE's connected cell
            ue.perform_handover(new_cell.ID)
            # Update the cell's connected UEs
            current_cell = next((cell for cell in self.Cells if cell.ID == ue.ConnectedCellID), None)
            if current_cell:
                current_cell.ConnectedUEs.remove(ue.ID)
            new_cell.ConnectedUEs.append(ue.ID)
            
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

    def perform_handover(self, ue, target_cell):
        # Implement the handover logic
        ue.perform_handover(target_cell.ID)
        current_cell = next((cell for cell in self.Cells if cell.ID == ue.ConnectedCellID), None)
        if current_cell:
            current_cell.ConnectedUEs.remove(ue.ID)
        target_cell.ConnectedUEs.append(ue.ID)

    def handle_load_balancing(self):
        for cell in self.Cells:
            if self.calculate_cell_load(cell) > 0.8:  # If cell load is over 80%
                underloaded_cell = self.find_underloaded_cell()
                if underloaded_cell:
                    selected_ues = self.select_ues_for_load_balancing(cell)
                    for ue in selected_ues:
                        self.perform_handover(ue, underloaded_cell)

    def handle_qos_based_handover(self):
        for ue in self.all_ues():  # Assuming all_ues method returns all UEs in the gNodeB
            current_cell = self.find_cell_by_id(ue.ConnectedCellID)
            if current_cell and not current_cell.can_provide_gbr(ue):
                for cell in self.Cells:
                    if cell != current_cell and cell.can_provide_gbr(ue):
                        self.perform_handover(ue, cell)
                        break

    def update(self):
        # Call this method regularly to update handover decisions
        self.handle_load_balancing()
        self.handle_qos_based_handover()

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
        
        # Attempt to handover UEs to other cells
        for ue_id in cell_to_delete.ConnectedUEs:
            # Find a UE object by its ID (assuming a method exists to find a UE by ID)
            ue = self.find_ue_by_id(ue_id)
            if ue:
                new_cell = self.handover_decision(ue)
                if new_cell:
                    self.perform_handover(ue, new_cell)
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