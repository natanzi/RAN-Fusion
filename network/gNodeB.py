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
from logs.logger_config import cell_logger, gnodeb_logger
from datetime import datetime
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision

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
        gnodeb_logger.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")

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
        from .handover_utils import handover_decision, perform_handover
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
        cell_logger.info(f"gNodeB '{self.ID}' cell capacity updated to {self.CellCount}.")

    def add_cell_to_gNodeB(self, cell):
    # Assuming 'cell' is an instance of Cell
        if len(self.Cells) < self.CellCount:  # Use CellCount to check the capacity for cells
            self.Cells.append(cell)
            print(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")
            cell_logger.info(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")
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
#####################################################################################################
    def find_underloaded_cell(self):
        # Find a cell with load below a certain threshold, e.g., 50%
        for cell in self.Cells:
            if self.calculate_cell_load(cell) < 0.5:
                return cell
        return None

    def select_ues_for_load_balancing(self, overloaded_cell, underloaded_cell):
        # Get UE objects from the overloaded cell
        ue_objects = [self.get_ue_by_id(ue_id) for ue_id in overloaded_cell.ConnectedUEs]

        # Prioritize UEs based on service type and data usage
        # Non-real-time services and lower data usage UEs are more likely to be selected
        prioritized_ues = sorted(ue_objects, key=lambda ue: (ue.ServiceType not in ['video', 'game'], ue.get_traffic_volume()))

        # Select a subset of UEs for handover
        # Assuming we want to move a third of the UEs, but this can be adjusted
        ues_to_move = prioritized_ues[:len(prioritized_ues) // 3]
    
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
    
    def get_ue_by_id(self, ue_id):
        # Assuming there is a method to get the UE object by its ID
        # This method should be implemented in the gNodeB class or elsewhere in the codebase
        # The method below is a placeholder and should be replaced with the actual implementation
        return next((ue for ue in self.all_ue_objects() if ue.ID == ue_id), None)
######################################################################################################
#######################################Periodic Updates###############################################
    def update(self):
        from network.handover_utils import handle_load_balancing, monitor_and_log_cell_load
    # Call this method regularly to update handover decisions
        handle_load_balancing(self, self.calculate_cell_load, self.find_underloaded_cell, self.select_ues_for_load_balancing)
    # Now also call monitor_and_log_cell_load to log the cell load
        monitor_and_log_cell_load(self)
    # handle_qos_based_handover(self, self.all_ues, self.find_cell_by_id)
######################################################################################################
