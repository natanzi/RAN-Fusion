#This is UE class, ue.py in network directory
import random
import math
import json
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from logs.logger_config import ue_logger
from datetime import datetime
from influxdb_client import Point

class UE:
    def __init__(self, ue_id, location, connected_cell_id, connected_sector, gnodeb_id, is_mobile, initial_signal_strength, rat, max_bandwidth, duplex_mode, tx_power, modulation, coding, mimo, processing, bandwidth_parts, channel_model, velocity, direction, traffic_model, scheduling_requests, rlc_mode, snr_thresholds, ho_margin, n310, n311, model, service_type=None, datasize=None, imei=None, screensize=None, batterylevel=None):
        self.ID = ue_id
        self.IMEI = imei or self.allocate_imei()  # Use provided IMEI or generate a new one
        self.Location = location
        self.ConnectedCellID = connected_cell_id
        self.ConnectedSector = connected_sector
        self.gNodeB_ID = gnodeb_id
        self.IsMobile = is_mobile
        self.ServiceType = service_type if service_type else random.choice(["video", "game", "voice", "data", "IoT"])
        self.SignalStrength = initial_signal_strength
        self.RAT = rat
        self.MaxBandwidth = max_bandwidth
        self.DuplexMode = duplex_mode
        self.TxPower = tx_power
        self.Modulation = modulation
        self.Coding = coding
        self.MIMO = mimo
        self.Processing = processing
        self.BandwidthParts = bandwidth_parts
        self.ChannelModel = channel_model
        self.Velocity = velocity
        self.Direction = direction
        self.TrafficModel = traffic_model
        self.SchedulingRequests = scheduling_requests
        self.RLCMode = rlc_mode
        self.SNRThresholds = snr_thresholds
        self.HOMargin = ho_margin
        self.N310 = n310
        self.N311 = n311
        self.Model = model
        self.ScreenSize = screensize or f"{random.uniform(5.0, 7.0):.1f} inches"  # Use provided screen size or randomly generate
        self.BatteryLevel = batterylevel or random.randint(10, 100)  # Use provided battery level or randomly generate
        self.TrafficVolume = 0  # Initialize with a default value
        self.DataSize = datasize
        ue_logger.info(f"UE initialized with ID {ue_id} at {datetime.datetime.now()}")

    @staticmethod
    def allocate_imei():
        # Generate and return a random IMEI during UE initialization
        while True:
            start = str(random.randint(10000000, 99999999))  # Generate an 8-digit TAC
            while len(start) < 14:
                start += str(random.randint(0, 9))
            imei = start + str(UE.calc_check_digit(start))
            break
        return imei

    @staticmethod
    def calc_check_digit(number):
        alphabet = '0123456789'
        n = len(alphabet)
        number = tuple(alphabet.index(i) for i in reversed(str(number)))
        return (sum(number[::2]) + sum(sum(divmod(i * 2, n)) for i in number[1::2])) % n
    
    @staticmethod
    def from_json(json_data):
        ues = []
        for item in json_data["ues"]:
            ue = UE(
                ue_id=item["ue_id"],
                location=(item["location"]["latitude"], item["location"]["longitude"]),
                connected_cell_id=item["connectedCellID"],
                connected_sector=None,  # JSON does not have this field; assuming None or provide a default value
                gnodeb_id=item.get("gnodeb_id"),  # Extract gnodeb_id from the JSON item
                is_mobile=item["isMobile"],
                initial_signal_strength=item["initialSignalStrength"],
                rat=item["rat"],
                max_bandwidth=item["maxBandwidth"],
                duplex_mode=item["duplexMode"],
                tx_power=item["txPower"],
                modulation=item["modulation"],
                coding=item["coding"],
                mimo=item["mimo"],
                processing=item["processing"],
                bandwidth_parts=item["bandwidthParts"],
                channel_model=item["channelModel"],
                velocity=item["velocity"],
                direction=item["direction"],
                traffic_model=item["trafficModel"],
                scheduling_requests=item["schedulingRequests"],
                rlc_mode=item["rlcMode"],
                snr_thresholds=item["snrThresholds"],
                ho_margin=item["hoMargin"],
                n310=item["n310"],
                n311=item["n311"],
                model=item["model"],
                service_type=item.get("serviceType"),  # Optional, use get
                datasize=item.get("datasize"),  # Optional, use get
                imei=item.get("IMEI"),  # Extract IMEI if present
                screensize=item.get("screensize"),  # Extract screensize if present
                batterylevel=item.get("batterylevel")  # Extract batterylevel if present
            )
            ues.append(ue)
        return ues
#########################################################################################
####################################################################################################        
    def serialize_for_influxdb(self):
        point = Point("ue_metrics") \
            .tag("ue_id", self.ID) \
            .tag("connected_cell_id", self.ConnectedCellID) \
            .tag("connected_sector_id", self.ConnectedSector) \
            .tag("entity_type", "ue") \
            .tag("gnb_id", self.gNodeB_ID) \
            .field("imei", self.IMEI) \
            .field("service_type", self.ServiceType) \
            .field("signal_strength", self.SignalStrength) \
            .field("rat", self.RAT) \
            .field("max_bandwidth", self.MaxBandwidth) \
            .field("duplex_mode", self.DuplexMode) \
            .field("tx_power", self.TxPower) \
            .field("modulation", ','.join(self.Modulation) if isinstance(self.Modulation, list) else self.Modulation) \
            .field("coding", self.Coding) \
            .field("mimo", self.MIMO) \
            .field("processing", self.Processing) \
            .field("bandwidth_parts", ','.join(map(str, self.BandwidthParts)) if isinstance(self.BandwidthParts, list) else self.BandwidthParts) \
            .field("channel_model", self.ChannelModel) \
            .field("velocity", float(self.Velocity)) \
            .field("direction", self.Direction) \
            .field("traffic_model", self.TrafficModel) \
            .field("scheduling_requests", int(self.SchedulingRequests)) \
            .field("rlc_mode", self.RLCMode) \
            .field("snr_thresholds", ','.join(map(str, self.SNRThresholds))) \
            .field("ho_margin", str(self.HOMargin)) \
            .field("n310", str(self.N310)) \
            .field("n311", str(self.N311)) \
            .field("model", self.Model) \
            .field("screen_size", self.ScreenSize) \
            .field("battery_level", str(self.BatteryLevel))
        return point
        

