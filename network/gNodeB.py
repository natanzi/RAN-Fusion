#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random
import time
from database.time_utils import get_current_time_ntp
import logging
from utils.location_utils import get_nearest_gNodeB, get_ue_location_info
from network.init_cell import initialize_cells
from .init_cell import load_json_config
from time import sleep
from logs.logger_config import cell_logger, gnodeb_logger
from datetime import datetime
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
from database.time_utils import get_current_time_ntp, server_pools
from multiprocessing import Manager
import threading

current_time = get_current_time_ntp()

def load_gNodeB_config():
    # Correct the path to point to the 'Config_files' directory
    # This assumes that 'Config_files' is a direct subdirectory of the base directory where 'main.py' is located
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'Config_files', 'gNodeB_config.json')

    with open(file_path, 'r') as file:
        return json.load(file)

##Using the function to load the configuration
gNodeBs_config = load_gNodeB_config()

class gNodeB:
    def __init__(self, gnodeb_id, latitude, longitude, coverageRadius, power, frequency, bandwidth, location, region, maxUEs, cellCount, handoverMargin, handoverHysteresis, timeToTrigger, interFreqHandover, xnInterface, sonCapabilities, loadBalancingOffset, cellIds, MeasurementBandwidth=None, BlacklistedCells=None, **kwargs):
        from network.cell import Cell
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
        gnodeb_logger.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells at '{current_time}'.")

        # Handle any additional keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        print(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")
        
        # Logging statement should be here, after all attributes are set
        #logging.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")
        
        time.sleep(1)  # Delay for 1 second
    @staticmethod
    def from_json(json_data):
        gNodeBs = []
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs.append(gnodeb)
        return gNodeBs
    
    @classmethod
    def from_dict(cls, data):
        from network.cell import Cell
        # Create an instance of gNodeB from serialized data
        gnodeb_instance = cls()  # You may need to pass appropriate arguments to the constructor

        # Assuming data is a dictionary with keys corresponding to the names of the gNodeB attributes
        for key, value in data.items():
            setattr(gnodeb_instance, key, value)

        # Reconstruct Cells and other complex attributes if necessary
        # For example, if Cells are serialized as a list of dictionaries:
        
        gnodeb_instance.Cells = [Cell.from_dict(cell_data) for cell_data in data.get('Cells', [])]

        return gnodeb_instance
    ###############################################################################################################
    def __getstate__(self):
        state = self.__dict__.copy()  
        if 'lock' in state:
            del state['lock']
        #print("State during pickling:", state) # Print state
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()

    ###############################################################################################################
    # add serialization methods to the gNodeB class to convert gNodeB instances into a format suitable for InfluxDB
    def serialize_for_influxdb(self):
        point = Point("gnodeb_metrics") \
            .tag("gnodeb_id", self.ID) \
            .tag("entity_type", "gnodeb") 

        # Convert the location list to a string if it's not None
        location_str = ','.join(map(str, self.Location)) if self.Location is not None else None

        # Ensure the 'region' field is a string
        region_str = str(self.Region) if self.Region is not None else None

        fields = {
            "latitude": self.Latitude,
            "longitude": self.Longitude,
            "coverage_radius": self.CoverageRadius,
            "transmission_power": self.TransmissionPower,
            "frequency": self.Frequency,
            "region": region_str,  # Use the converted string for 'region'
            "max_ues": self.MaxUEs,
            "cell_count": self.CellCount,
            "measurement_bandwidth": self.MeasurementBandwidth,
            "blacklisted_cells": self.BlacklistedCells,
            "handover_success_count": self.handover_success_count,
            "handover_failure_count": self.handover_failure_count,
            "location": location_str,  
            "bandwidth": self.Bandwidth,
            "handover_margin": self.HandoverMargin,
            "handover_hysteresis": self.HandoverHysteresis,
            "time_to_trigger": self.TimeToTrigger,
            "inter_freq_handover": self.InterFreqHandover,
            "xn_interface": self.XnInterface,
            "son_capabilities": self.SONCapabilities,
            "load_balancing_offset": self.LoadBalancingOffset,
            "cell_ids": ','.join(map(str, self.CellIds)) if self.CellIds is not None else None
        }

        for field, value in fields.items():
            if value is not None:
                point = point.field(field, value)

        point = point.time(time.time_ns(), WritePrecision.NS)
        return point
######################################################################################################
##################################################Cell and UE Management##########################
    def get_ue_by_id(self, ue_id):
        # Retrieve the UE object from the internal list of UEs managed by this gNodeB
        # Assuming self.ues is a dictionary with UE IDs as keys and UE objects as values
        return self.ues.get(ue_id, None)
################################################################################################
    def delete_cell(self, cell_id):
        # Find the cell to be deleted
        cell_to_delete = next((cell for cell in self.Cells if cell.ID == cell_id), None)

        if cell_to_delete is None:
            print(f"No cell with ID {cell_id} found in gNodeB with ID {self.ID}")
            return

    # Attempt to handover UEs to other cells
        from .handover_utils import perform_handover, check_handover_feasibility
        for ue_id in cell_to_delete.ConnectedUEs:
            ue = self.find_ue_by_id(ue_id)
        if ue:
            # Determine a new cell for handover
            new_cell = self.find_available_cell()  # This method should identify a suitable cell
            if new_cell and check_handover_feasibility(self.network_state, new_cell.ID, ue):
                # Perform handover to the new cell
                perform_handover(self, ue, new_cell, self.network_state)
            else:
                print(f"No available or suitable cell for UE with ID {ue.ID} to handover.")

    # Remove the cell from the Cells list
        self.Cells.remove(cell_to_delete)
        print(f"Cell with ID {cell_id} has been deleted from gNodeB with ID {self.ID}")
###################################################################################################
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
        #return next((cell for cell in self.Cells if cell.ID == cell_id), None)
        
    def update_cell_capacity(self, new_capacity):
        # Check if the new capacity is valid
        if new_capacity < 0:
            raise ValueError("Cell capacity cannot be negative.")
        
        # Update the CellCount attribute
        self.CellCount = new_capacity
        
        # Log the change
        cell_logger.info(f"gNodeB '{self.ID}' cell capacity updated to {self.CellCount}.")

    def add_cell_to_gNodeB(self, cell):
        # Assuming 'cell' is an instance of Cell
        existing_cell_ids = [existing_cell.ID for existing_cell in self.Cells]
        if cell.ID in existing_cell_ids:
            print(f"Cell '{cell.ID}' is already added to gNodeB '{self.ID}'.")
            cell_logger.info(f"Cell '{cell.ID}' is already added to gNodeB '{self.ID}'.")
        elif len(self.Cells) < self.CellCount:  # Use CellCount to check the capacity for cells
            self.Cells.append(cell)
            print(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")
            cell_logger.info(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")
            time.sleep(1)  # Delay for 1 second
        else:
            print(f"gNodeB '{self.ID}' has reached its maximum cell capacity.")
###################################################################################################
#####################################Load Calculation##############################################
    def calculate_cell_load(self, cell, traffic_controller):
        # Calculate the load based on the number of connected UEs
        ue_based_load = len(cell.ConnectedUEs) / cell.MaxConnectedUEs if cell.MaxConnectedUEs > 0 else 0

        # Calculate the load based on the throughput
        total_throughput = 0
        for ue in cell.assigned_UEs:
        # Assume a function to calculate UE throughput exists
            ue_throughput = self.calculate_ue_throughput(ue)
            total_throughput += ue_throughput
        max_throughput_bytes = 100 * 1024 * 1024
        throughput_based_load = total_throughput / max_throughput_bytes if cell.max_throughput > 0 else 0

    # Retrieve quality metrics (jitter, packet loss, delay) for each UE from the TrafficController
        jitter_total = sum(traffic_controller.get_traffic_parameters(ue)['jitter'] for ue in cell.assigned_UEs)
        packet_loss_total = sum(traffic_controller.get_traffic_parameters(ue)['packet_loss'] for ue in cell.assigned_UEs)
        delay_total = sum(traffic_controller.get_traffic_parameters(ue)['delay'] for ue in cell.assigned_UEs)

    # Calculate average quality metrics across all UEs
        num_ues = len(cell.assigned_UEs)
        jitter_avg = jitter_total / num_ues if num_ues > 0 else 0
        packet_loss_avg = packet_loss_total / num_ues if num_ues > 0 else 0
        delay_avg = delay_total / num_ues if num_ues > 0 else 0

    # Combine all loads with appropriate weights
        combined_load = (0.4 * ue_based_load) + (0.4 * throughput_based_load) + (0.2 * (jitter_avg + packet_loss_avg + delay_avg) / 3)

    # Convert combined load to a percentage
        combined_load_percentage = combined_load * 100

        return combined_load_percentage
##########################################################################################################################
    def find_underloaded_cell(self):
        underloaded_cell = None
        lowest_load = float('inf')

        for cell in self.Cells:
            cell_load = self.calculate_cell_load(cell)
            if cell_load < 0.5 and cell_load < lowest_load:  # Threshold is 50%
                underloaded_cell = cell
                lowest_load = cell_load

        return underloaded_cell
##########################################################################################################################
    def select_ues_for_load_balancing(self, overloaded_cell, underloaded_cell):
        ue_objects = [self.get_ue_by_id(ue_id) for ue_id in overloaded_cell.ConnectedUEs]

        # Prioritize UEs based on service type (higher priority for 'video', 'game', 'data') and data usage
        prioritized_ues = sorted(ue_objects, key=lambda ue: (ue.serviceType in ['video', 'game', 'data'], ue.get_data_usage()), reverse=True)

        # Select a subset of UEs for handover
        # The exact logic for how many UEs to move can be adjusted as needed
        ues_to_move = prioritized_ues[:len(prioritized_ues) // 3]

        return ues_to_move
############################################################################################################################
    def find_available_cell(self):
        best_cell = None
        lowest_load = float('inf')

        # Iterate over all cells to find the one with the lowest load that is not near capacity
        for cell in self.Cells:
            cell_load = self.calculate_cell_load(cell)

            # Check if the cell is underloaded (e.g., load less than 80%) and has a lower load than the current best cell
            if cell_load < 0.8 and cell_load < lowest_load:  # 0.8 represents 80% load
                best_cell = cell
                lowest_load = cell_load

        return best_cell
#######################################Periodic Updates###############################################
    def update(self, shared_state=None):
        from network.handover_utils import handle_load_balancing, monitor_and_log_cell_load

        # If shared_state is provided, use it; otherwise, continue with the current state
        state = shared_state if shared_state is not None else self

        # Call this method regularly to update handover decisions
        handle_load_balancing(state, state.calculate_cell_load, state.find_underloaded_cell, state.select_ues_for_load_balancing)

        # Now also call monitor_and_log_cell_load to log the cell load
        monitor_and_log_cell_load(state)
######################################################################################################
