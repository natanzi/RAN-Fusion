#command_handler.py inside the network folder and owner of a command-based approach for adding, removing, or updating UEs or ...in fact: the CommandHandler class acts as middleware that can be utilized by both API.py and simulator_cli.py for executing commands such as add_ue. This design allows for a unified command processing mechanism across different interfaces of the system, ensuring consistency and reducing code duplication. 
from .ue import UE
from database.database_manager import DatabaseManager
from network.sector_manager import SectorManager
from logs.logger_config import API_logger
from flask import jsonify

class CommandHandler:

    @staticmethod
    def handle_command(command_type, data):
        if command_type == 'add_ue':
            CommandHandler._add_ue(data)
        elif command_type == 'remove_ue':
            CommandHandler._remove_ue(data)
        elif command_type == 'update_ue':
            CommandHandler._update_ue(data)
        else:
            raise ValueError("Unsupported command type")

    @staticmethod
    def _remove_ue(data):
        ue_id = data['ue_id']
        
        # Attempt to find the sector_id dynamically
        sector_manager = SectorManager.get_instance()
        sector_id = sector_manager.find_sector_by_ue_id(ue_id)
        
        if sector_id is None:
            API_logger.error(f"UE {ue_id} not found in any sector")
            return jsonify({'error': f"UE {ue_id} not found"}), 404
        
        # Proceed with the removal process
        removed = sector_manager.remove_ue_from_sector(sector_id, ue_id)
        
        if removed:
            # Assuming the database manager is also accessible globally or via singleton
            db_manager = DatabaseManager.get_instance()
            db_manager.remove_ue_state(ue_id, sector_id)
            API_logger.info(f"UE {ue_id} removed successfully from sector {sector_id}.")
            return jsonify({'message': f"UE {ue_id} removed successfully from sector {sector_id}."}), 200
        else:
            API_logger.error(f"Failed to remove UE {ue_id} from sector {sector_id} or sector/UE not found.")
            return jsonify({'error': f"Failed to remove UE {ue_id} from sector {sector_id} or sector/UE not found."}), 500
    
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