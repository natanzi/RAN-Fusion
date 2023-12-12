#This is UE class, ue.py in network directory
import random
import math
import json
from database.database_manager import DatabaseManager
from .network_state import NetworkState
from .utils import random_location_within_radius
from traffic.traffic_generator import TrafficController
from network.network_state import NetworkState
from log.logger_config import ue_logger
from datetime import datetime

class UE:
    def __init__(self, ue_id, location, connected_cell_id, is_mobile, initial_signal_strength, rat, max_bandwidth, duplex_mode, tx_power, modulation, coding, mimo, processing, bandwidth_parts, channel_model, velocity, direction, traffic_model, scheduling_requests, rlc_mode, snr_thresholds, ho_margin, n310, n311, model, service_type=None):
        self.ID = ue_id
        self.IMEI = self.allocate_imei()  # Always generate a new IMEI
        self.Location = location
        self.ConnectedCellID = connected_cell_id
        self.IsMobile = is_mobile
        self.ServiceType = service_type if service_type else random.choice(["video", "game", "voice", "data", "IoT"])  # Use provided service type or randomly pick one
        self.SignalStrength = initial_signal_strength
        self.RAT = rat
        self.MaxBandwidth = max_bandwidth
        self.DuplexMode = duplex_mode
        self.TxPower = tx_power
        self.Modulation = random.choice(["QPSK", "16QAM", "64QAM"]) if modulation is None else modulation
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
        self.ScreenSize = f"{random.uniform(5.0, 7.0):.1f} inches"  # Always randomly generate screen size
        self.BatteryLevel = random.randint(10, 100)  # Always randomly generate battery level
        ue_logger.info(f"UE initialized with ID {ue_id} at {datetime.now()}")
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
            ue_id = item["ue_id"]  # Use the provided UE ID
            ue = UE(
                ue_id=ue_id,
                location=(item["location"]["latitude"], item["location"]["longitude"]),
                connected_cell_id=item["connectedCellId"],
                is_mobile=item["isMobile"],
                service_type=item.get("serviceType"),  # Check if serviceType is provided
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
                model=item["model"]
                # Note: screenSize and batteryLevel are not included here as they are generated within the constructor
            )
            ues.append(ue)
        return ues

    def generate_traffic(self, traffic_multiplier=1):
        traffic_controller = TrafficController()  # Create an instance of TrafficController

        # Convert service type to lowercase to ensure case-insensitive comparison
        service_type_lower = self.ServiceType.lower()

        if service_type_lower == "voice":
            return traffic_controller.generate_voice_traffic()
        elif service_type_lower == "video":
            return traffic_controller.generate_video_traffic()
        elif service_type_lower == "game":
            return traffic_controller.generate_gaming_traffic()
        elif service_type_lower == "iot":
            return traffic_controller.generate_iot_traffic()
        elif service_type_lower == "data":  
            return traffic_controller.generate_data_traffic()
        else:
            raise ValueError(f"Unknown service type: {self.ServiceType}")
        
        # Scale the data size by the traffic multiplier
        data_size *= traffic_multiplier
        return data_size, interval

    def perform_handover(self, new_cell):
        old_cell_id = self.ConnectedCellID  # Store the old cell ID for logging
        self.ConnectedCellID = new_cell.ID
        new_cell.add_ue(self)
        
        # Assuming you have a way to determine if the handover was successful
        handover_successful = True  # or some condition that determines success
        
        # Update the network state to reflect the handover
        network_state = NetworkState() 
        network_state.update_state(self.gNodeBs, self.cells, self.ues)
        
        # Log the handover event
        if handover_successful:
            ue_logger.info(f"UE {self.ID} handovered from Cell {old_cell_id} to Cell {new_cell.ID}")
        else:
            ue_logger.error(f"Handover failed for UE {self.ID} from Cell {old_cell_id} to Cell {new_cell.ID}")
