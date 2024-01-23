#This is UE class, ue.py in network directory
import random
import math
import json
from database.database_manager import DatabaseManager
from .utils import random_location_within_radius
from logs.logger_config import ue_logger
from datetime import datetime
from influxdb_client import Point
import threading

class UE:
    def __init__(self, ue_id, location, connected_cell_id, connected_sector, gnodeb_id, is_mobile, initial_signal_strength, rat, max_bandwidth, duplex_mode, tx_power, modulation, coding, mimo, processing, bandwidth_parts, channel_model, velocity, direction, traffic_model, scheduling_requests, rlc_mode, snr_thresholds, ho_margin, n310, n311, model, service_type=None, datasize=None):
        self.lock = threading.Lock()
        self.ID = ue_id
        self.IMEI = self.allocate_imei()  # Always generate a new IMEI
        self.Location = location
        self.ConnectedCellID = connected_cell_id
        self.connected_sector = connected_sector
        self.gNodeB_ID = gnodeb_id
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
        self.traffic_volume = 0  # Initialize with a default value or a calculated value
        self.DataSize = datasize
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
            ue_id = item["ue_id"] 
            gnodeb_id = item.get("gNodeB_ID")  # Extract gNodeB_ID from the JSON item
            service_type = item.get("serviceType")
            datasize = item.get("datasize")
            ue = UE(
                ue_id=ue_id,
                location=(item["location"]["latitude"], item["location"]["longitude"]),
                connected_cell_id=item["connectedCellId"],
                connected_sector = item["connectedSectorId"],
                is_mobile=item["isMobile"],
                gnodeb_id=gnodeb_id, 
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
#########################################################################################
    def add_ue(self, ue):
        with self.lock:  # Ensure thread safety
            print(f"Debug: Attempting to add UE with ID {ue.ID}")
            if ue.ID in self.ues:
                error_message = f"UE with ID {ue.ID} already exists in the network"
                print(f"Debug: {error_message}")
                raise ValueError(error_message)
            self.ues[ue.ID] = ue
            print(f"Debug: UE with ID {ue.ID} has been added to the network")

    def verify_no_duplicate_ues(self):
        with self.lock:
            ue_ids = [ue.ID for ue in self.ues.values()]
            if len(ue_ids) != len(set(ue_ids)):
                error_message = "Duplicate UE IDs detected after addition."
                print(f"Debug: {error_message}")
                raise ValueError(error_message)
#########################################################################################    
    def generate_traffic(self):
        from traffic.traffic_generator import TrafficController
        traffic_controller = TrafficController()
        # Convert service type to lowercase to ensure case-insensitive comparison
        service_type_lower = self.ServiceType.lower()

        # Initialize variables to store traffic data
        data_size = 0
        interval = 0
        delay = 0
        jitter = 0
        packet_loss_rate = 0

        if service_type_lower == "voice":
            # Assuming generate_voice_traffic returns five values
            data_size, interval, delay, jitter, packet_loss_rate = traffic_controller.generate_voice_traffic()
            print(f"Debug: Generated voice traffic for UE {self.ID} - Data Size: {data_size}, Interval: {interval}, Delay: {delay}, Jitter: {jitter}, Packet Loss Rate: {packet_loss_rate}")
        elif service_type_lower == "video":
            data_size, interval, delay, jitter, packet_loss_rate = traffic_controller.generate_video_traffic()
            print(f"Debug: Generated video traffic for UE {self.ID} - Data Size: {data_size}, Interval: {interval}, Delay: {delay}, Jitter: {jitter}, Packet Loss Rate: {packet_loss_rate}")
        elif service_type_lower == "game":
            data_size, interval, delay, jitter, packet_loss_rate = traffic_controller.generate_gaming_traffic()
            print(f"Debug: Generated gaming traffic for UE {self.ID} - Data Size: {data_size}, Interval: {interval}, Delay: {delay}, Jitter: {jitter}, Packet Loss Rate: {packet_loss_rate}")
        elif service_type_lower == "iot":
            data_size, interval, delay, jitter, packet_loss_rate = traffic_controller.generate_iot_traffic()
            print(f"Debug: Generated IoT traffic for UE {self.ID} - Data Size: {data_size}, Interval: {interval}, Delay: {delay}, Jitter: {jitter}, Packet Loss Rate: {packet_loss_rate}")
        elif service_type_lower == "data":
            data_size, interval, delay, jitter, packet_loss_rate = traffic_controller.generate_data_traffic()
            print(f"Debug: Generated data traffic for UE {self.ID} - Data Size: {data_size}, Interval: {interval}, Delay: {delay}, Jitter: {jitter}, Packet Loss Rate: {packet_loss_rate}")
        else:
            raise ValueError(f"Unknown service type: {self.ServiceType}")

####################################################################################
    def perform_handover(self, old_cell, new_cell):
        try:
            print(f"Debug: Starting handover process for UE {self.ID} from Cell {old_cell.ID} to Cell {new_cell.ID}")
            # Check if the handover is feasible (this method should be implemented)
            handover_successful = self.check_handover_feasibility(old_cell, new_cell)
            if handover_successful:
                print(f"Debug: Handover is feasible for UE {self.ID}")
                # Remove UE from the old cell's list of connected UEs
                old_cell.remove_ue(self)
                print(f"Debug: UE {self.ID} removed from Cell {old_cell.ID}")
                # Add UE to the new cell
                new_cell.add_ue(self)
                print(f"Debug: UE {self.ID} added to Cell {new_cell.ID}")
                # Update the UE's connected cell ID
                self.ConnectedCellID = new_cell.ID
            
                print(f"Debug: Network state updated for UE {self.ID} handover")
                # Log the successful handover
                ue_logger.info(f"UE {self.ID} handovered from Cell {old_cell.ID} to Cell {new_cell.ID}")
            else:
                print(f"Debug: Handover failed for UE {self.ID} from Cell {old_cell.ID} to Cell {new_cell.ID}")
                # Log the failed handover
                ue_logger.error(f"Handover failed for UE {self.ID} from Cell {old_cell.ID} to Cell {new_cell.ID}")
            return handover_successful
        except Exception as e:
            print(f"Debug: Exception occurred during handover for UE {self.ID}: {e}")
            # Log any exception that occurs during the handover
            ue_logger.error(f"Handover exception for UE {self.ID}: {e}")
            return False
######################################################################################
    def is_in_restricted_region(self):
        # Logic to determine if the cell is in a restricted region
        # ...
        return False
######################################################################################
    def is_eligible_for_handover(self):
        """
        Determines if the UE is eligible for handover based on its properties 
        and the ...

        :param : The current state of the network.
        :return: Boolean indicating eligibility for handover.
        """
        # Example: Check service type
        if self.serviceType in ['restricted_service_type']:
            return False

        # Additional checks can be added here based on ?
        # For example, checking network policies, cell congestion, etc.
        # ...

        return True
######################################################################################
    def update_traffic_model(self, traffic_params):
        # Update the UE's traffic model with the new parameters
        # traffic_params is expected to be a dictionary containing the new traffic parameters

        # Check if the required keys are present in the traffic_params dictionary
        required_keys = ['data_size', 'interval', 'delay', 'jitter', 'packet_loss_rate']
        if not all(key in traffic_params for key in required_keys):
            raise ValueError("Missing traffic parameters for updating the traffic model.")

        # Update the traffic model parameters
        self.TrafficModel['data_size'] = traffic_params['data_size']
        self.TrafficModel['interval'] = traffic_params['interval']
        self.TrafficModel['delay'] = traffic_params['delay']
        self.TrafficModel['jitter'] = traffic_params['jitter']
        self.TrafficModel['packet_loss_rate'] = traffic_params['packet_loss_rate']

        # Log the update
        ue_logger.info(f"Traffic model updated for UE {self.ID} with parameters: {traffic_params}")
####################################################################################################
    def perform_handover(self, old_cell, new_cell):
        try:
            print(f"Debug: Starting handover process for UE {self.ID} from Cell {old_cell.ID} to Cell {new_cell.ID}")
            # Check if the handover is feasible (this method should be implemented)
            handover_successful = self.check_handover_feasibility(old_cell, new_cell)
            if handover_successful:
                print(f"Debug: Handover is feasible for UE {self.ID}")
                # Remove UE from the old cell's list of connected UEs
                old_cell.remove_ue(self)
                print(f"Debug: UE {self.ID} removed from Cell {old_cell.ID}")
                # Add UE to the new cell
                new_cell.add_ue(self)
                print(f"Debug: UE {self.ID} added to Cell {new_cell.ID}")
                # Update the UE's connected cell ID
                self.ConnectedCellID = new_cell.ID
                print(f"Debug: Network state updated for UE {self.ID} handover")
                # Log the successful handover
                ue_logger.info(f"UE {self.ID} handovered from Cell {old_cell.ID} to Cell {new_cell.ID}")
            else:
                print(f"Debug: Handover failed for UE {self.ID} from Cell {old_cell.ID} to Cell {new_cell.ID}")
                # Log the failed handover
                ue_logger.error(f"Handover failed for UE {self.ID} from Cell {old_cell.ID} to Cell {new_cell.ID}")
            return handover_successful
        except Exception as e:
            print(f"Debug: Exception occurred during handover for UE {self.ID}: {e}")
            # Log any exception that occurs during the handover
            ue_logger.error(f"Handover exception for UE {self.ID}: {e}")
            return False
####################################################################################################
    def start_traffic(self):
        # Logic to start traffic generation for this UE
        # This could involve setting a flag or starting a traffic generation thread
        self.is_traffic_active = True
        ue_logger.info(f"Traffic generation started for UE {self.ID}.")
        print(f"Debug: Traffic generation started for UE {self.ID}.")

    def stop_traffic(self):
        # Logic to stop traffic generation for this UE
        # This could involve clearing a flag or stopping a traffic generation thread
        self.is_traffic_active = False
        ue_logger.info(f"Traffic generation stopped for UE {self.ID}.")
        print(f"Debug: Traffic generation stopped for UE {self.ID}.")
####################################################################################################        
    def serialize_for_influxdb(self):
        point = Point("ue_metrics") \
            .tag("ue_id", self.ID) \
            .tag("connected_cell_id", self.ConnectedCellID) \
            .tag("connected_sector_id", self.connected_sector)\
            .tag("entity_type", "ue") \
            .tag("gnb_id", self.gNodeB_ID)\
            .field("imei", self.IMEI) \
            .field("service_type", self.ServiceType) \
            .field("signal_strength", self.SignalStrength) \
            .field("rat", self.RAT) \
            .field("max_bandwidth", self.MaxBandwidth) \
            .field("duplex_mode", self.DuplexMode) \
            .field("tx_power", self.TxPower) \
            .field("modulation", self.Modulation) \
            .field("coding", self.Coding) \
            .field("mimo", self.MIMO) \
            .field("processing", self.Processing) \
            .field("bandwidth_parts", self.BandwidthParts) \
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
            .field("model", str(self.Model)) \
            .field("screen_size", str(self.ScreenSize)) \
            .field("battery_level", str(self.BatteryLevel))
        return point
        

