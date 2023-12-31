#Defines the Cell class, which is part of a gNodeB.// this is located inside network directory
from logs.logger_config import cell_logger
import datetime
from logs.logger_config import ue_logger
from logs.logger_config import cell_logger
import time 
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from database.time_utils import get_current_time_ntp, server_pools

class Cell:
    def __init__(self, cell_id, gnodeb_id, frequencyBand, duplexMode, tx_power, bandwidth, ssb_periodicity, ssb_offset, max_connect_ues, max_throughput,  channel_model, trackingArea=None, network_state=None, is_active=True, sectors=None):
        # Check if the cell ID already exists in the network state
        from .network_state import NetworkState
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
        self.max_throughput = max_throughput
        self.ChannelModel = channel_model
        self.TrackingArea = trackingArea 
        self.ConnectedUEs = []
        self.assigned_UEs = []  # Initialize the list of assigned UEs
        self.last_ue_update = None
        self.last_update = None
        self.IsActive = is_active
        self.current_ue_count = 0
        self.Sectors = sectors if sectors is not None else []
        current_time = get_current_time_ntp()
        # Logging statement should be here, after all attributes are set
        cell_logger.info(f" A Cell '{cell_id}' has been created at '{current_time}' in gNodeB '{gnodeb_id}' with max capacity {self.MaxConnectedUEs}.")
        
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
            trackingArea=json_data.get("trackingArea"),
            max_throughput=json_data["max_throughput"],
            sectors=json_data.get("sectors"),

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
            'max_throughput': self.max_throughput,
            'ChannelModel': self.ChannelModel,
            'TrackingArea': self.TrackingArea,
            'CellisActive': self.IsActive

        }
    def add_sector(self, sector):
        if not hasattr(self, 'sectors'):
            self.sectors = []
        self.sectors.append(sector)

    # Method to get the count of active UEs and update the last attached cell and its gNodeB
    def update_ue_count(self):
        self.last_update = get_current_time_ntp()
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
        if any(ue in cell.ConnectedUEs for cell in network_state.cells.values()):
            raise Exception(f"UE '{ue.ID}' is already connected to a cell.")

        # Check if the cell has reached its maximum capacity
        if len(self.ConnectedUEs) >= self.MaxConnectedUEs:
            raise Exception(f"Cell '{self.ID}' has reached its maximum capacity.")

        # Add the UE to the cell
        current_time = get_current_time_ntp()
        self.ConnectedUEs.append(ue)
        self.current_ue_count = self.update_ue_count()  # Update the UE count after adding
        ue_logger.info(f"UE with ID {ue.ID} added to Cell {self.ID} at '{current_time}'")
        cell_logger.info(f"UE '{ue.ID}' has been added to Cell '{self.ID}'.")

        # Update the network state here
        network_state.update_state({**network_state.gNodeBs}, {**network_state.cells}, {**network_state.ues})

        # Log the addition
        cell_logger.info(f"UE '{ue.ID}' has been attached to Cell '{self.ID}' at '{current_time}'.")
        ue_logger.info(f"UE '{ue.ID}' has been attached to Cell '{self.ID}' at '{current_time}'.")
        print(f"UE '{ue.ID}' has been attached to Cell '{self.ID}' at '{current_time}'.")
#########################################################################################        

    def remove_ue(self, ue, network_state):
        current_time = get_current_time_ntp()
        if ue in self.ConnectedUEs:
            self.ConnectedUEs.remove(ue)
            self.current_ue_count -= 1
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
            .field("max_throughput", self.max_throughput) \
            .field("channel_model", self.ChannelModel) \
            .field("trackingArea", self.TrackingArea) \
            .field("CellisActive",self.IsActive)
        return point