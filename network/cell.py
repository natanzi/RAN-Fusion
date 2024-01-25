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
    def __init__(self, cell_id, gnodeb_id, frequencyBand, duplexMode, tx_power, bandwidth, ssbPeriodicity, ssbOffset, maxConnectUes, max_throughput,  channelModel, sectorCount, trackingArea=None, is_active=True):
        print(f"START-Creating cell {cell_id}")
        # Check if the cell ID already exists in the network state
        self.ID = cell_id
        self.gNodeB_ID = gnodeb_id
        self.FrequencyBand = frequencyBand
        self.DuplexMode = duplexMode
        self.TxPower = tx_power
        self.Bandwidth = bandwidth
        self.SSBPeriodicity = ssbPeriodicity
        self.SSBOffset = ssbOffset
        self.maxConnectUes = maxConnectUes
        self.max_throughput = max_throughput
        self.ChannelModel = channelModel
        self.TrackingArea = trackingArea 
        self.ConnectedUEs = []
        self.assigned_UEs = []  # Initialize the list of assigned UEs
        self.last_ue_update = None
        self.last_update = None
        self.IsActive = is_active
        self.current_ue_count = 0
        self.sectors = []
        self.SectorCount = sectorCount
        current_time = get_current_time_ntp()
        # Logging statement should be here, after all attributes are set
        cell_logger.info(f" A Cell '{cell_id}' has been created at '{current_time}' in gNodeB '{gnodeb_id}' with max capacity {self.maxConnectUes}.")
        
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
####################################################################################### 
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
            .field("max_connect_ues", self.maxConnectUes) \
            .field("max_throughput", self.max_throughput) \
            .field("channel_model", self.ChannelModel) \
            .field("trackingArea", self.TrackingArea) \
            .field("CellisActive", self.IsActive) \
            .field("sector_count", len(self.sectors))

        # Loop to add details about each sector
        for i, sector in enumerate(self.sectors):
            point.field(f"sector_{i}_id", sector.sector_id)
            # Add other relevant sector fields here

        return point