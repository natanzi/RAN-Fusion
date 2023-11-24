import random
import math
import json
from database.database_manager import DatabaseManager
from traffic.traffic_generator import generate_voice_traffic, generate_video_traffic, generate_gaming_traffic, generate_iot_traffic, generate_data_traffic
db_manager = DatabaseManager()

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
        self.ScreenSize = f"{random.uniform(5.0, 7.0):.1f} inches"  # Always randomly generate screen size
        self.BatteryLevel = random.randint(10, 100)  # Always randomly generate battery level

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

    def generate_traffic(self):
        # Convert service type to lowercase to ensure case-insensitive comparison
        service_type_lower = self.ServiceType.lower()

        if service_type_lower == "voice":
            return generate_voice_traffic()
        elif service_type_lower == "video":
            return generate_video_traffic()
        elif service_type_lower == "game":
            return generate_gaming_traffic()
        elif service_type_lower == "iot":
            return generate_iot_traffic()
        elif service_type_lower == "data":  
            return generate_data_traffic()
        else:
            raise ValueError(f"Unknown service type: {self.ServiceType}")


    def perform_handover(self, new_cell):
        # Assuming new_cell is an instance of the Cell class
        self.ConnectedCellID = new_cell.ID
        new_cell.add_ue(self)

        # Initialize UEs and assign them to Cells
    ues = []
    db_manager = DatabaseManager(db_path='path_to_your_database')
    for ue_data in ue_config['ues']:
        # Remove the keys that are not expected by the UE constructor
        ue_data.pop('IMEI', None)
        ue_data.pop('screensize', None)
        ue_data.pop('batterylevel', None)
        # Adjust the keys to match the UE constructor argument names
        ue_data['ue_id'] = ue_data.pop('ue_id')
        ue_data['location'] = (ue_data['location']['latitude'], ue_data['location']['longitude'])
        ue_data['connected_cell_id'] = ue_data.pop('connectedCellId')
        ue_data['is_mobile'] = ue_data.pop('isMobile')
        ue_data['initial_signal_strength'] = ue_data.pop('initialSignalStrength')
        ue_data['rat'] = ue_data.pop('rat')
        ue_data['max_bandwidth'] = ue_data.pop('maxBandwidth')
        ue_data['duplex_mode'] = ue_data.pop('duplexMode')
        ue_data['tx_power'] = ue_data.pop('txPower')
        ue_data['modulation'] = ue_data.pop('modulation')
        ue_data['coding'] = ue_data.pop('coding')
        ue_data['mimo'] = ue_data.pop('mimo')
        ue_data['processing'] = ue_data.pop('processing')
        ue_data['bandwidth_parts'] = ue_data.pop('bandwidthParts')
        ue_data['channel_model'] = ue_data.pop('channelModel')
        ue_data['velocity'] = ue_data.pop('velocity')
        ue_data['direction'] = ue_data.pop('direction')
        ue_data['traffic_model'] = ue_data.pop('trafficModel')
        ue_data['scheduling_requests'] = ue_data.pop('schedulingRequests')
        ue_data['rlc_mode'] = ue_data.pop('rlcMode')
        ue_data['snr_thresholds'] = ue_data.pop('snrThresholds')
        ue_data['ho_margin'] = ue_data.pop('hoMargin')
        ue_data['n310'] = ue_data.pop('n310')
        ue_data['n311'] = ue_data.pop('n311')
        ue_data['model'] = ue_data.pop('model')

        ue = UE(**ue_data)
        # Assign UE to a random cell of a random gNodeB, if available
        selected_gNodeB = random.choice(gNodeBs)
        if selected_gNodeB.Cells:
            selected_cell = random.choice(selected_gNodeB.cells)
            ue.connected_cell_id = selected_cell.cell_id
        
        # Write UE static data to the database
        db_manager.insert_ue_static_data(ue)

        ues.append(ue)

    # Create additional UEs if needed
    additional_ues_needed = max(0, num_ues_to_launch - len(ues))
    for _ in range(additional_ues_needed):
        selected_gNodeB = random.choice(gNodeBs)
        random_location = random_location_within_radius(
            selected_gNodeB.Latitude, selected_gNodeB.Longitude, selected_gNodeB.CoverageRadius
        )
        new_ue = UE(
            ue_id=f"UE{random.randint(1000, 9999)}",
            location=random_location,
            connected_cell_id=None,  # Placeholder for no initial cell connection
            is_mobile=True,  # Assuming the UE is mobile
            service_type=random.choice(["video", "game", "voice", "data", "IoT"]),
            initial_signal_strength=random.uniform(0, 1),  # Random initial signal strength
            rat="5G",  # Assuming a 5G UE
            max_bandwidth=100,  # Example bandwidth value
            duplex_mode="FDD",  # Assuming Frequency Division Duplexing
            tx_power=23,  # Transmission power in dBm
            modulation="QAM",  # Example modulation
            coding="LDPC",  # Example coding scheme
            mimo="4x4",  # Example MIMO configuration
            processing="high",  # Processing capability
            bandwidth_parts=[10, 20, 30],  # Bandwidth parts
            channel_model="urban",  # Channel model
            velocity=random.uniform(0, 100),  # Random velocity
            direction=random.randint(0, 360),  # Random direction
            traffic_model="random",  # Traffic model
            scheduling_requests=True,  # Scheduling requests
            rlc_mode="UM",  # RLC mode
            snr_thresholds=[10, 20, 30],  # SNR thresholds
            ho_margin=3,  # Handover margin
            n310=5,  # N310 counter value
            n311=10,  # N311 counter value
            model="ModelX",  # Device model
        )
        if selected_gNodeB.Cells:
            selected_cell = random.choice(selected_gNodeB.Cells)
            new_ue.ConnectedCellID = selected_cell.ID
        
        # Write UE static data to the database
        db_manager.insert_ue_static_data(new_ue)

        ues.append(new_ue)

    # Commit changes to the database
    db_manager.commit_changes()
    db_manager.close_connection()