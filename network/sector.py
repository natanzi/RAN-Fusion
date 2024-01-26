#this is sectory.py which is located in network directory
#You can extend this class with additional methods to handle sector-specific logic, such as calculating signal strength, managing handovers, or adjusting parameters for load balancing. Remember to test this class thoroughly to ensure it integrates well with the rest of your codebase.
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
import time
import threading
from logs.logger_config import sector_logger
sector_lock = threading.Lock()

# Assume a global list or set for UE IDs is defined at the top level of your module
global_ue_ids = set()

class Sector:
    def __init__(self, sector_id, cell_id, cell, capacity, azimuth_angle, beamwidth, frequency, duplex_mode, tx_power, bandwidth, mimo_layers, beamforming, ho_margin, load_balancing, connected_ues=None, current_load=0):
        self.sector_id = sector_id  # Unique identifier for the sector
        self.cell_id = cell_id  # Identifier of the cell this sector belongs to
        self.cell = cell  # Cell object this sector is part of
        self.capacity = int(capacity)  # Maximum number of UEs that can be hosted in this sector
        self.azimuth_angle = azimuth_angle  # Orientation of the sector in degrees
        self.beamwidth = beamwidth  # Width of the transmission beam in degrees
        self.frequency = frequency  # Operating frequency of the sector
        self.duplex_mode = duplex_mode  # Duplexing mode used (e.g., FDD, TDD)
        self.tx_power = tx_power  # Transmission power of the sector
        self.bandwidth = bandwidth  # Bandwidth allocated to the sector
        self.mimo_layers = mimo_layers  # Number of MIMO layers used in the sector
        self.beamforming = beamforming  # Indicates if beamforming is used
        self.ho_margin = ho_margin  # Handover margin used for making handover decisions
        self.load_balancing = load_balancing  # Indicates if load balancing is enabled
        self.connected_ues = connected_ues if connected_ues is not None else []  # List of UEs currently connected to the sector
        self.current_load = current_load  # Current load on the sector

    @classmethod
    def from_json(cls, data, cell):
    # Ensure the 'capacity' key exists in data, if not, set a default value or handle it appropriately
        if 'capacity' not in data:
            # Handle the missing 'capacity' key, for example by setting a default value
            data['capacity'] = 3  # Replace with an actual default value or raise an error
        else:
            data['capacity'] = int(data['capacity'])  # Ensure capacity is an integer

        # The 'cell' object is passed as an argument, so we set it directly
        data['cell'] = cell

        # The 'cell_id' is obtained from the 'cell' object
        data['cell_id'] = cell.ID

        return cls(**data)

    def serialize_for_influxdb(self):
        point = Point("sector_metrics") \
            .tag("sector_id", self.sector_id) \
            .tag("cell_id", self.cell_id) \
            .field("azimuth_angle", self.azimuth_angle) \
            .field("beamwidth", self.beamwidth) \
            .field("frequency", self.frequency) \
            .field("duplex_mode", self.duplex_mode) \
            .field("tx_power", self.tx_power) \
            .field("bandwidth", self.bandwidth) \
            .field("mimo_layers", self.mimo_layers) \
            .field("beamforming", int(self.beamforming)) \
            .field("ho_margin", self.ho_margin) \
            .field("load_balancing", self.load_balancing) \
            .field("connected_ues", len(self.connected_ues)) \
            .field("current_load", self.current_load) \
            .field("capacity", self.capacity) \
            .time(time.time_ns(), WritePrecision.NS)
        return point

    def add_ue(self, ue):
        with sector_lock:  # Use the correct lock defined at the global scope
            if ue.ID not in self.connected_ues:
                self.connected_ues.append(ue.ID)  # Store only the ID, not the UE object
                self.current_load += 1  # Increment the current load
                global_ue_ids.add(ue.ID)  # Add the UE ID to the global list
                sector_logger.info(f"UE with ID {ue.ID} has been added to the sector. Current load: {self.current_load}")
            else:
                sector_logger.warning(f"UE with ID {ue.ID} is already connected to the sector.")

    def remove_ue(self, ue):
        with sector_lock:
            if ue.ID in self.connected_ues:
                self.connected_ues.remove(ue.ID)  # Remove the ID, not the UE object
                self.current_load -= 1  # Decrement the current load
                global_ue_ids.discard(ue.ID)  # Remove the UE ID from the global list
                sector_logger.info(f"UE with ID {ue.ID} has been removed from the sector. Current load: {self.current_load}")
            else:
                sector_logger.warning(f"UE with ID {ue.ID} is not connected to the sector.")
