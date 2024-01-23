#this is sectory.py which is located in network directory
#You can extend this class with additional methods to handle sector-specific logic, such as calculating signal strength, managing handovers, or adjusting parameters for load balancing. Remember to test this class thoroughly to ensure it integrates well with the rest of your codebase.
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
import time

class Sector:
    def __init__(self, sector_id, cell_id, azimuth_angle, beamwidth, frequency, duplex_mode, tx_power, bandwidth, mimo_layers, beamforming, ho_margin, load_balancing, connected_ues=None, current_load=0):
        self.sector_id = sector_id
        self.cell_id = cell_id
        self.azimuth_angle = azimuth_angle
        self.beamwidth = beamwidth
        self.frequency = frequency
        self.duplex_mode = duplex_mode
        self.tx_power = tx_power
        self.bandwidth = bandwidth
        self.mimo_layers = mimo_layers
        self.beamforming = beamforming
        self.ho_margin = ho_margin
        self.load_balancing = load_balancing
        self.connected_ues = connected_ues if connected_ues is not None else []
        self.current_load = current_load

    @classmethod
    def from_json(cls, data):
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
            .time(time.time_ns(), WritePrecision.NS)
        return point

    # Add any additional methods required for sector operations below
    # Example: Method to update the current load of the sector
    def update_load(self, new_load):
        self.current_load = new_load
        # Additional logic to handle load changes can be added here

    # Example: Method to add a UE to the sector
    def add_ue(self, ue):
        if ue not in self.connected_ues:
            self.connected_ues.append(ue)
            # Update load or perform other necessary actions

    # Example: Method to remove a UE from the sector
    def remove_ue(self, ue):
        if ue in self.connected_ues:
            self.connected_ues.remove(ue)
            # Update load or perform other necessary actions