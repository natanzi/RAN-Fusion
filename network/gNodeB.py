#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random

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
    def __init__(self, gnodeb_id, latitude, longitude, coverageRadius, power, frequency, bandwidth, maxUEs, cellCount, **kwargs):
        self.ID = gnodeb_id
        self.Latitude = latitude
        self.Longitude = longitude
        self.CoverageRadius = coverageRadius
        self.TransmissionPower = power
        self.Frequency = frequency
        self.Bandwidth = bandwidth
        self.MaxUEs = maxUEs
        self.CellCount = cellCount
        self.Cells = []  # This will hold Cell instances associated with this gNodeB

        # Optional attributes with default values
        self.Location = kwargs.get('location', [])
        self.Region = kwargs.get('region', [])
        self.HandoverMargin = kwargs.get('handoverMargin', 0)
        self.HandoverHysteresis = kwargs.get('handoverHysteresis', 0)
        self.TimeToTrigger = kwargs.get('timeToTrigger', 0)
        self.InterFreqHandover = kwargs.get('interFreqHandover', False)
        self.XnInterface = kwargs.get('xnInterface', False)
        self.SONCapabilities = kwargs.get('sonCapabilities', False)
        self.MeasurementBandwidth = kwargs.get('measurementBandwidth', 0)
        self.BlacklistedCells = kwargs.get('blacklistedCells', [])
        self.LoadBalancingOffset = kwargs.get('loadBalancingOffset', 0)
        self.CellIds = kwargs.get('cellIds', [])

    @staticmethod
    def from_json(json_data):
        gNodeBs = []
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs.append(gnodeb)
        return gNodeBs

    #def handover_decision(self, ue_array, cell_array):
        # Method to decide handovers for UEs based on signal-to-noise ratio (SNR)
        for ue in ue_array:
            current_cell_id = ue.ConnectedCellID
            current_cell_index = next((index for index, cell in enumerate(cell_array) if cell.ID == current_cell_id), None)

            if current_cell_index is None:
                continue  # Skip if the current cell is not found

            best_cell_index = current_cell_index
            best_snr = ue.SINR  # Current SNR

            # Loop through cells to find the best SNR
            for index, cell in enumerate(self.Cells):
                if index != current_cell_index:
                    potential_snr = random.random()  # Placeholder for actual SNR calculation
                    if potential_snr > best_snr:
                        best_snr = potential_snr
                        best_cell_index = index

            # Perform handover if a better cell is found
            if best_cell_index != current_cell_index:
                cell_array[current_cell_index].remove_ue(ue.ID)
                cell_array[best_cell_index].add_ue(ue.ID)
                ue.perform_handover(self.Cells[best_cell_index].ID)

