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
    def handle_handover(self, ue, other_gNodeBs, real_time_db):
        """
        Handles all handover scenarios for a UE.

        :param ue: The User Equipment instance.
        :param other_gNodeBs: List of other gNodeBs in the network.
        :param real_time_db: Connection to the real-time database (e.g., InfluxDB).
        """
        # Update UE location from the real-time database
        ue_location = real_time_db.get_latest_ue_location(ue.ID)

        # Intra-frequency and Inter-frequency Handovers
        self.handle_intra_and_inter_frequency_handover(ue, ue_location)

        # Xn-Based Handover
        self.handle_xn_based_handover(ue, other_gNodeBs, ue_location)

        # Inter-RAT and S1-Based Handovers
        self.handle_inter_rat_and_s1_based_handover(ue, ue_location)

        # N3 and N2 Based Handovers
        self.handle_n3_and_n2_based_handover(ue, other_gNodeBs, ue_location)

        # Seamless, Conditional, and Load Balancing Handovers
        self.handle_seamless_conditional_and_load_balancing_handover(ue, ue_location)

        # Vertical Handover
        self.handle_vertical_handover(ue, ue_location)

        # Emergency Handover
        self.handle_emergency_handover(ue, ue_location)

    # Define individual methods for each handover type within the gNodeB class
    # ...

# Example of a method for intra-frequency and inter-frequency handovers
def handle_intra_and_inter_frequency_handover(self, ue, ue_location):
    # Logic to handle intra-frequency and inter-frequency handovers
    pass

# ... other methods for different handover types ...

# In your main simulation loop or appropriate control structure
# Instantiate gNodeB objects and pass them to the handover function along with the UE and real-time DB connection
