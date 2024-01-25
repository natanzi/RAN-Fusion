#This is UE class, ue.py in network directory
import random
import re
from datetime import datetime
from influxdb_client import Point
from logs.logger_config import ue_logger

class UE:
    def __init__(self, **kwargs):
        self.ID = kwargs.get('ue_id')
        self.IMEI = kwargs.get('imei') or self.allocate_imei()
        self.Location = kwargs.get('location')
        self.ConnectedCellID = kwargs.get('connected_cell_id')
        self.ConnectedSector = kwargs.get('connected_sector')
        self.gNodeB_ID = kwargs.get('gnodeb_id')
        self.IsMobile = kwargs.get('is_mobile')
        self.ServiceType = kwargs.get('service_type', random.choice(["video", "game", "voice", "data", "IoT"]))
        self.SignalStrength = kwargs.get('initial_signal_strength')
        self.RAT = kwargs.get('rat')
        self.MaxBandwidth = kwargs.get('max_bandwidth')
        self.DuplexMode = kwargs.get('duplex_mode')
        self.TxPower = kwargs.get('tx_power')
        self.Modulation = kwargs.get('modulation')
        self.Coding = kwargs.get('coding')
        self.MIMO = kwargs.get('mimo')
        self.Processing = kwargs.get('processing')
        self.BandwidthParts = kwargs.get('bandwidth_parts')
        self.ChannelModel = kwargs.get('channel_model')
        self.Velocity = kwargs.get('velocity')
        self.Direction = kwargs.get('direction')
        self.TrafficModel = kwargs.get('traffic_model')
        self.SchedulingRequests = kwargs.get('scheduling_requests')
        self.RLCMode = kwargs.get('rlc_mode')
        self.SNRThresholds = kwargs.get('snr_thresholds')
        self.HOMargin = kwargs.get('ho_margin')
        self.N310 = kwargs.get('n310')
        self.N311 = kwargs.get('n311')
        self.Model = kwargs.get('model')
        self.ScreenSize = kwargs.get('screensize', f"{random.uniform(5.0, 7.0):.1f} inches")
        self.BatteryLevel = kwargs.get('batterylevel', random.randint(10, 100))
        self.TrafficVolume = 0
        self.DataSize = kwargs.get('datasize')
        ue_logger.info(f"UE initialized with ID {self.ID} at {datetime.now()}")

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
    def camel_to_snake(name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @staticmethod
    def from_json(json_data):
        ues = []
        for item in json_data["ues"]:
            item = {UE.camel_to_snake(key): value for key, value in item.items()}
            ue = UE(**item)
            ues.append(ue)
        return ues

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
            .field("battery_level", str(self.BatteryLevel)) \
            .time(datetime.utcnow())
        return point