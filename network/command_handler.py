#command_handler.py inside the network folder and owner of a command-based approach for adding, removing, or updating UEs or ...in fact: the CommandHandler class acts as middleware that can be utilized by both API.py and simulator_cli.py for executing commands such as add_ue. This design allows for a unified command processing mechanism across different interfaces of the system, ensuring consistency and reducing code duplication. 
from .ue import UE
from database.database_manager import DatabaseManager
from network.sector_manager import SectorManager
from logs.logger_config import API_logger
from flask import jsonify
from network.ue_manager import UEManager
from traffic.traffic_generator import TrafficController

class CommandHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandHandler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def handle_command(command_type, data):
        if command_type == 'add_ue':
            CommandHandler._add_ue(data)
        elif command_type == 'del_ue':
            CommandHandler._del_ue(data)
        elif command_type == 'update_ue':
            CommandHandler._update_ue(data)
        else:
            raise ValueError("Unsupported command type")

    @staticmethod
    def _del_ue(data):
        ue_id = data['ue_id']
    
        # Use UEManager to handle UE removal comprehensively
        ue_manager = UEManager.get_instance()
    
        # First, check if the UE exists in the system
        if ue_manager.get_ue_by_id(ue_id) is None:
            API_logger.error(f"UE {ue_id} not found in any sector or system")
            return jsonify({'error': f"UE {ue_id} not found in any sector or system"}), 404
    
        # Proceed with the removal process using UEManager's delete_ue method
        removed = ue_manager.delete_ue(ue_id)
    
        if removed:
            API_logger.info(f"UE {ue_id} removed successfully.")
            return jsonify({'message': f"UE {ue_id} removed successfully."}), 200
        else:
            API_logger.error(f"Failed to remove UE {ue_id}.")
            return jsonify({'error': f"Failed to remove UE {ue_id}."}), 500
    
    @staticmethod
    def _add_ue(data):
        # Create the UE instance
        ue = UE(
            ue_id=data['ue_id'],
            imei=data['IMEI'],
            location=data['location'],
            connected_cell_id=data['connectedCellID'],
            gNodeB_id=data['gnodeb_id'],
            signal_strength=data['initialSignalStrength'],
            rat=data['rat'],
            max_bandwidth=data['maxBandwidth'],
            duplex_mode=data['duplexMode'],
            # Add other parameters as needed
            service_class=data.get('service_type'),  # Assuming service_class is equivalent to service_type
            tx_power=data['txPower'],
            modulation=data['modulation'],
            coding=data['coding'],
            mimo=data['mimo'],
            processing=data['processing'],
            bandwidth_parts=data['bandwidthParts'],
            channel_model=data['channelModel'],
            velocity=data['velocity'],
            direction=data['direction'],
            traffic_model=data['trafficModel'],
            scheduling_requests=data['schedulingRequests'],
            rlc_mode=data['rlcMode'],
            snr_thresholds=data['snrThresholds'],
            ho_margin=data['hoMargin'],
            n310=data['n310'],
            n311=data['n311'],
            model=data['model'],
            screensize=data['screensize'],
            batterylevel=data['batterylevel'],
            datasize=data['datasize']
        )

        # Assuming SectorManager and UEManager have methods to handle UE addition
        sector_manager = SectorManager.get_instance()
        ue_manager = UEManager.get_instance()

        # Add the UE to the sector
        success = sector_manager.add_ue_to_sector(data['sector_id'], ue)
        if success:
            # Optionally, start traffic generation for the newly added UE
            traffic_controller = TrafficController.get_instance()
            traffic_controller.start_ue_traffic(ue.ue_id)
            return jsonify({'message': 'UE successfully added'}), 200
        else:
            return jsonify({'error': 'Failed to add UE'}), 400

    @staticmethod
    def _update_ue(data):
        ue_id = data['ue_id']
        ue = UE.get_ue_instance_by_id(ue_id)
        if ue:
            ue.update_parameters(**data)
            print(f"UE {ue_id} updated successfully.")
        else:
            print(f"UE {ue_id} not found.")