#command_handler.py inside the network folder and owner of a command-based approach for adding, removing, or updating UEs or ... 
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
    def _add_ue(data):
        # Assuming data contains all necessary UE parameters
        ue = UE(config={}, **data)
        # Add UE to database or in-memory storage as needed
        # This is a placeholder for actual logic
        print(f"UE {ue.ID} added successfully.")

    @staticmethod
    def _remove_ue(data):
        ue_id = data['ue_id']
        
        # Attempt to find the sector_id dynamically if not provided in the request data
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
    def _update_ue(data):
        ue_id = data['ue_id']
        ue = UE.get_ue_instance_by_id(ue_id)
        if ue:
            ue.update_parameters(**data)
            print(f"UE {ue_id} updated successfully.")
        else:
            print(f"UE {ue_id} not found.")