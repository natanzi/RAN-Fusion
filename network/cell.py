#Defines the Cell class, which is part of a gNodeB.// this is located inside network directory
import logging
from .network_state import NetworkState
import datetime
from logs.logger_config import ue_logger
from logs.logger_config import cell_logger
import time 
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from database.time_utils import get_current_time_ntp, server_pools

class Cell:
    def __init__(self, cell_id, gnodeb_id, frequencyBand, duplexMode, tx_power, bandwidth, ssb_periodicity, ssb_offset, max_connect_ues, channel_model, trackingArea=None, network_state=None):
        # Check if the cell ID already exists in the network state
        if network_state and network_state.get_cell_info(cell_id):
            raise ValueError(f"Duplicate cell ID {cell_id} is not allowed.")
        self.ID = cell_id
        self.gNodeB_ID = gnodeb_id
        self.FrequencyBand = frequencyBand
        self.DuplexMode = duplexMode
        self.TxPower = tx_power
        self.Bandwidth = bandwidth
        self.SSBPeriodicity = ssb_periodicity
        self.SSBOffset = ssb_offset
        self.MaxConnectedUEs = max_connect_ues
        self.ChannelModel = channel_model
        self.TrackingArea = trackingArea 
        self.ConnectedUEs = []
        self.assigned_UEs = []  # Initialize the list of assigned UEs
        self.last_ue_update = None
        self.last_update = None
        current_time = get_current_time_ntp(server_pools)
        # Logging statement should be here, after all attributes are set
        cell_logger.info(f"Cell '{cell_id}' has been created at '{current_time}' in gNodeB '{self.ID}' with max capacity {self.MaxConnectedUEs}.")
        
    @staticmethod
    def from_json(json_data):
        return Cell(
            cell_id=json_data["cell_id"],
            gnodeb_id=json_data["gnodeb_id"],
            frequencyBand=json_data["frequencyBand"],
            duplexMode=json_data["duplexMode"],
            tx_power=json_data["tx_power"],
            bandwidth=json_data["bandwidth"],
            ssb_periodicity=json_data["ssbPeriodicity"],
            ssb_offset=json_data["ssbOffset"],
            max_connect_ues=json_data["maxConnectUes"],
            channel_model=json_data["channelModel"],
            trackingArea=json_data.get("trackingArea")
        )
    def to_dict(self):
        return {
            'ID': self.ID,
            'gNodeB_ID': self.gNodeB_ID,
            'FrequencyBand': self.FrequencyBand,
            'DuplexMode': self.DuplexMode,
            'TxPower': self.TxPower,
            'Bandwidth': self.Bandwidth,
            'SSBPeriodicity': self.SSBPeriodicity,
            'SSBOffset': self.SSBOffset,
            'MaxConnectedUEs': self.MaxConnectedUEs,
            'ChannelModel': self.ChannelModel,
            'TrackingArea': self.TrackingArea,
            # Assuming you don't need to include the 'ConnectedUEs' list
        }
    # Method to get the count of active UEs and update the last attached cell and its gNodeB
    def update_ue_count(self):
        self.last_update = get_current_time_ntp(server_pools)
        if self.ConnectedUEs:
            self.last_ue_update = {
                'ue_id': self.ConnectedUEs[-1].ID,
                'cell_id': self.ID,
                'gnodeb_id': self.gNodeB_ID,
                'timestamp': self.last_update
            }
        return len(self.ConnectedUEs)
#########################################################################################        
    def add_ue(self, ue, network_state):
    # Check if the UE is already connected to any cell
        for cell_id, cell in network_state.cells.items():
            if ue in cell.ConnectedUEs:
                raise Exception(f"UE '{ue.ID}' is already connected to Cell '{cell_id}'.")

        if len(self.ConnectedUEs) < self.MaxConnectedUEs:
            current_time = get_current_time_ntp(server_pools)
            self.ConnectedUEs.append(ue)
            print(f"UE '{ue.ID}' has been attached to Cell '{self.ID}' at '{current_time}'.")
            self.update_ue_count()
            # Update the network state here
            network_state.update_state(network_state.gNodeBs, list(network_state.cells.values()), list(network_state.ues.values()))
            ue_logger.info(f"UE with ID {ue.ID} added to Cell {self.ID} at '{current_time}'")
            cell_logger.info(f"UE '{ue.ID}' has been added to Cell '{self.ID}'.")
        else:
            raise Exception("Maximum number of connected UEs reached for this cell.")

    def remove_ue(self, ue, network_state):
        current_time = get_current_time_ntp(server_pools)
        if ue in self.ConnectedUEs:
            self.ConnectedUEs.remove(ue)
            print(f"UE '{ue.ID}' has been detached from Cell '{self.ID}' at {current_time}.")
            self.update_ue_count()
            # Update the network state here if necessary
            network_state.update_state(network_state.gNodeBs, list(network_state.cells.values()), list(network_state.ues.values()))
            ue_logger.info(f"UE with ID {ue.ID} removed from Cell {self.ID} at at '{current_time}'")
        else:
            print(f"UE '{ue.ID}' is not connected to Cell '{self.ID}' and cannot be removed.")
            ue_logger.warning(f"Attempted to remove UE with ID {ue.ID} from Cell {self.ID} which is not connected.")
    
    def serialize_for_influxdb(self):
        point = Point("cell_metrics") \
            .tag("cell_id", self.ID) \
            .tag("gnodeb_id", self.gNodeB_ID) \
            .tag("entity_type", "cell") \
            .field("frequencyBand", self.FrequencyBand) \
            .field("duplexMode", self.DuplexMode) \
            .field("tx_power", self.TxPower) \
            .field("bandwidth", self.Bandwidth) \
            .field("ssb_periodicity", self.SSBPeriodicity) \
            .field("ssb_offset", self.SSBOffset) \
            .field("max_connect_ues", self.MaxConnectedUEs) \
            .field("channel_model", self.ChannelModel) \
            .field("trackingArea", self.TrackingArea)
        return point