#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random
import time
from database.time_utils import get_current_time_ntp
import logging
from utils.location_utils import get_nearest_gNodeB, get_ue_location_info
from network.cell import Cell
from network.init_cell import initialize_cells
from .init_cell import load_json_config
from time import sleep
from logs.logger_config import cell_logger, gnodeb_logger
from datetime import datetime
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
from database.time_utils import get_current_time_ntp, server_pools
from multiprocessing import Lock
from network.sector import Sector

current_time = get_current_time_ntp()
DEFAULT_BLACKLISTED_CELLS = []
DEFAULT_MEASUREMENT_BANDWIDTH = 20

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
    def __init__(self, gnodeb_id, latitude, longitude, coverageRadius, power, frequency, bandwidth, location, region, maxUEs, cellCount, sectorCount, handoverMargin, handoverHysteresis, timeToTrigger, interFreqHandover, xnInterface, sonCapabilities, loadBalancingOffset, cellIds, sectorIds, MeasurementBandwidth=None, BlacklistedCells=None, **kwargs):
        print("Debug Start: __init__ method in gNodeB class.")
        self.ID = gnodeb_id
        self.Latitude = latitude
        self.Longitude = longitude
        self.CoverageRadius = coverageRadius
        self.TransmissionPower = power
        self.Frequency = frequency
        self.Bandwidth = bandwidth
        self.Location = location
        self.Region = region if isinstance(region, str) else ','.join(region)
        self.MaxUEs = maxUEs
        self.HandoverMargin = handoverMargin
        self.HandoverHysteresis = handoverHysteresis
        self.TimeToTrigger = timeToTrigger
        self.InterFreqHandover = interFreqHandover
        self.XnInterface = xnInterface
        self.SONCapabilities = sonCapabilities
        self.MeasurementBandwidth = MeasurementBandwidth if MeasurementBandwidth is not None else DEFAULT_MEASUREMENT_BANDWIDTH
        self.BlacklistedCells = BlacklistedCells if BlacklistedCells is not None else DEFAULT_BLACKLISTED_CELLS
        self.LoadBalancingOffset = loadBalancingOffset
        self.CellIds = cellIds
        self.CellCount = cellCount
        self.SectorCount = sectorCount
        self.handover_success_count = 0
        self.handover_failure_count = 0
        self.SectorIds = sectorIds
        self.Cells = []
        gnodeb_logger.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells at '{current_time}'.")
        print(f"Debug End: gNodeB '{self.ID}' initialized with {self.CellCount} cells.")
        # Handle any additional keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        print(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells.")
        time.sleep(1)  # Delay for 1 second


    @staticmethod
    def from_json(json_data):
        gNodeBs_dict = {}
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs_dict[gnodeb.ID] = gnodeb
        return gNodeBs_dict
    ###############################################################################################################
    # add serialization methods to the gNodeB class to convert gNodeB instances into a format suitable for InfluxDB
    def serialize_for_influxdb(self):
        point = Point("gnodeb_metrics") \
            .tag("gnodeb_id", self.ID) \
            .tag("entity_type", "gnodeb")

        # Convert the location list to a string if it's not None
        location_str = ','.join(map(str, self.Location)) if self.Location is not None else None

        # Convert the blacklisted cells list to a string if it's not None
        blacklisted_cells_str = ','.join(map(str, self.BlacklistedCells)) if self.BlacklistedCells is not None else None

        # Ensure the 'region' field is a string
        region_str = str(self.Region) if self.Region is not None else None

        # Create a dictionary of fields to include in the Point
        fields = {
            "latitude": self.Latitude,
            "longitude": self.Longitude,
            "coverage_radius": self.CoverageRadius,
            "transmission_power": self.TransmissionPower,
            "frequency": self.Frequency,
            "region": region_str,
            "max_ues": self.MaxUEs,
            "cell_count": self.CellCount,
            "sector_count": self.SectorCount,
            "measurement_bandwidth": self.MeasurementBandwidth,
            "blacklisted_cells": blacklisted_cells_str,  # Use the serialized string
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
            "cell_ids": ','.join(map(str, self.CellIds)) if self.CellIds is not None else None,
            "sector_ids": ','.join([str(sector_id) for sector_id in self.SectorIds])
        }

        # Add fields to the Point if they are not None
        for field, value in fields.items():
            if value is not None:
                point = point.field(field, value)

        # Set the time for the Point
        point = point.time(time.time_ns(), WritePrecision.NS)

        return point
######################################################################################################
##################################################Cell and UE Management##########################
    def add_cell_to_gNodeB(self, cell):

            try:
                print(f"Debug: Attempting to add cell {cell.ID} to gNodeB {self.ID}")
                current_cell_ids = [c.ID for c in self.Cells]
                print(f"Debug: Current cells in gNodeB {self.ID} before adding: {current_cell_ids}")
                cell_logger.info(f"Current cells in gNodeB {self.ID} before adding: {current_cell_ids}")

                # Proactive check to prevent adding a cell with a duplicate ID
                if cell.ID in current_cell_ids:
                    print(f"Debug: Cell {cell.ID} is already added to gNodeB {self.ID}. Ignoring.")
                    cell_logger.warning(f"Cell {cell.ID} is already added to gNodeB {self.ID}. Ignoring.")
                    return

                if len(self.Cells) >= self.CellCount:
                    print(f"Debug: gNodeB {self.ID} has reached its maximum cell capacity. Cannot add more cells.")
                    cell_logger.error(f"gNodeB {self.ID} has reached its maximum cell capacity. Cannot add more cells.")
                    return

                # Set the parent gNodeB reference for the cell
                cell.set_gNodeB(self)

                # Add the cell to the gNodeB's list of cells
                self.Cells.append(cell)
                print(f"Debug: Cell {cell.ID} has been added to gNodeB {self.ID}.")
                cell_logger.info(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")

                # Add sectors to the cell if they are not already present
                for sector in cell.sectors:
                    if not cell.has_sector(sector):
                        self.add_sector_to_cell(sector, cell)
                        print(f"Debug: Sector {sector.ID} has been added to Cell {cell.ID}.")
                        cell_logger.info(f"Sector '{sector.ID}' has been added to Cell '{cell.ID}'.")

                # Reactive check to ensure no duplicate cells have been added
                self.verify_no_duplicate_cells()

                # Delay for 1 second as per the original requirement
                time.sleep(1)
            except Exception as e:
                print(f"Error: An exception occurred while adding cell {cell.ID} to gNodeB {self.ID}: {e}")
                cell_logger.error(f"An exception occurred while adding cell {cell.ID} to gNodeB {self.ID}: {e}")

    def verify_no_duplicate_cells(self):
        
            cell_ids = [cell.ID for cell in self.Cells]
            if len(cell_ids) != len(set(cell_ids)):
                raise ValueError("Duplicate Cell IDs detected after addition.")
###################################################################################################
    def add_sector_to_cell(self, sector, cell):
        print(f"Debug: Starting to add sector '{sector.ID}' to cell '{cell.ID}' in gNodeB '{self.ID}'.")  # Start message
        print(f"Debug: Sector object: {repr(sector)}")  # Print out the sector object
        try:
            #Check if the cell exists in this gNodeB
            if cell not in self.Cells:
                raise ValueError(f"Cell '{cell.ID}' does not exist in gNodeB '{self.ID}'")
            #Check if the sector already exists in the cell
            if cell.has_sector(sector):
                raise ValueError(f"Sector '{sector.ID}' already exists in Cell '{cell.ID}'")
            #Add the sector to the cell's list of sectors
            cell.add_sector(sector)
            #Log the addition of the sector
            cell_logger.info(f"Sector '{sector.ID}' has been added to Cell '{cell.ID}' in gNodeB '{self.ID}'.")
            print(f"Debug: Finished adding sector '{sector.ID}' to cell '{cell.ID}' in gNodeB '{self.ID}'.")  # End message
        except Exception as e:
            print(f"An error occurred: {e}")
###################################################################################################


