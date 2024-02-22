#command_handler.py inside the network folder and owner of a command-based approach for adding, removing, or updating UEs or ...in fact: the CommandHandler class acts as middleware that can be utilized by both API.py and simulator_cli.py for executing commands such as add_ue. This design allows for a unified command processing mechanism across different interfaces of the system, ensuring consistency and reducing code duplication. 
from .ue import UE
from database.database_manager import DatabaseManager
from network.sector_manager import SectorManager
from logs.logger_config import API_logger
from flask import jsonify
from network.ue_manager import UEManager

class CommandHandler:

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
        # Assuming data now includes 'service_class' along with other UE attributes
        ue = UE(data['ue_id'], data['imei'], data['location'], data['connected_cell_id'], data['gNodeB_id'], data['signal_strength'], data['rat'], data['max_bandwidth'], data['duplex_mode'], service_class=data['service_class'])
        # Add the UE to the sector
        sector_manager = SectorManager()
        success = sector_manager.add_ue_to_sector(data['sector_id'], ue)
        if success:
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