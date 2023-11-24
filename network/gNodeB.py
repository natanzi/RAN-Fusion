#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random
from utils.location_utils import get_nearest_gNodeB, get_ue_location_info

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

    @staticmethod
    def from_json(json_data):
        gNodeBs = []
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs.append(gnodeb)
        return gNodeBs

    def add_cell(self, cell):
        """
        Adds a Cell instance to the gNodeB's list of cells.

        :param cell: The Cell instance to be added.
        """
        # Check if the cell is already in the list to avoid duplicates
        if cell not in self.Cells:
            self.Cells.append(cell)
        else:
            print(f"Cell with ID {cell.ID} is already added to gNodeB with ID {self.ID}")

        # Optionally, you can also check if the cell's gNodeB_ID matches this gNodeB's ID
        if cell.gNodeB_ID != self.ID:
            print(f"Cell with ID {cell.ID} does not match gNodeB ID {self.ID}. Not adding to Cells list.")

    def check_cell_capacity(self, cell):
        # Placeholder for checking if a cell can accept more UEs
        return len(cell.ConnectedUEs) < cell.MaxConnectedUEs

    def find_available_cell(self):
        # Find a cell with available capacity
        for cell in self.Cells:
            if self.check_cell_capacity(cell):
                return cell
        return None

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
