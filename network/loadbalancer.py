# loadbalancer.py and it is inside the network folder
from datetime import datetime
import logging
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger
from database.database_manager import DatabaseManager
import time

class LoadBalancer:

    def __init__(self):
        self.db_manager = DatabaseManager()

    def handle_load_balancing(self, entity_type, entity_id):
        """
        Perform load balancing based on the type and ID of the overloaded entity.
        :param entity_type: Type of the entity ('gNodeB', 'cell', or 'sector')
        :param entity_id: ID of the overloaded entity

        """
        if entity_type == 'gNodeB':
            # Logic to balance load across cells within the specified gNodeB
            pass
        elif entity_type == 'cell':
            # Logic to balance load across sectors within the specified cell, or move UEs to other cells
            pass

        elif entity_type == 'sector':

            if not self.is_sector_overloaded(entity_id):
                return 
            sorted_ues = self.get_sorted_ues_by_throughput(entity_id)
            target_sector = self.find_target_sector(entity_id)  # Implementation needed    

            for ue in sorted_ues:
                if self.move_ue_to_sector(ue, target_sector):
                    # Assuming move_ue_to_sector updates the database and memory
                    continue
                else:
                    # Handle failure, potentially roll back
                    break
            else:
                raise ValueError("Unsupported entity type for load balancing.")

            # Sector is not overloaded, no action required
            #1- first we should make sure is really overloaded?
            #2- if yes we should get the list of UE associated with the sector with their throuput and sort it from high throuput to low thruput
            #3- then we should find less loaded neibers sectors list from get_sorted_entities_by_load() of the class of NetworkLoadManager in this file NetworkLoadManager.py this is target sector
            #5- we should move UE from the high loeaded sector [source]  to the neibers sector which has choosed as target sector in step 3
            #6- in case of any failure, we should roleback the UE to the source sector.
            #6- we should update the UE with the new sector ID in the database
            #7- we make sure the ue in new sector is updated in the list of the sector id in memory
###########################################################################################################################################
            
################################################Handover Execution#######################################################
    def is_handover_required(ue, handover_threshold):
        """
        Determine if a handover is required based on the UE conditions and cell load.

        :param ue: The user equipment (UE) instance.
        :param handover_threshold: The threshold for triggering a handover.
        :return: A tuple (Boolean, Cell) where the boolean indicates if handover is required,
        and Cell is the target cell for handover if one is required.
        """
        current_cell = next((cell for cell in gNodeB.Cells if cell.ID == ue.ConnectedCellID), None)
        if current_cell is None:
            return False, None

        current_cell_load = current_cell.calculate_cell_load()
        if current_cell_load > handover_threshold:
            target_cell = gNodeB.find_underloaded_cell()
            if target_cell and check_handover_feasibility(target_cell, ue):
                return True, target_cell
            
        return False, None
###########################################################################################################################################
    def check_handover_feasibility(target_cell, ue):
        if target_cell is None:
            return False

        if len(target_cell.ConnectedUEs) >= target_cell.MaxConnectedUEs:
            return False

        if target_cell.is_in_restricted_region():
            return False

        if not ue.is_eligible_for_handover():
            return False

        # Check the load of the target cell instead of gNodeB load
        cell_load = target_cell.calculate_cell_load()
        if cell_load > 90:  # Adjusted to check cell load instead of gNodeB load
            return False

        return True
###########################################################################################################################################
    def perform_handover(gnodeb, ue, target_cell):
        from .cell import Cell
        handover_successful = False
        current_cell_id = ue.ConnectedCellID
        original_cell = next((cell for cell in gnodeb.Cells if cell.ID == current_cell_id), None)
        all_cells = gnodeb.Cells  # Directly using gNodeB's Cells attribute

    # Ensure target_cell is provided
    if not target_cell:
        return False  # Optionally, handle this situation more gracefully

    if check_handover_feasibility(target_cell, ue):
        handover_successful = ue.perform_handover(target_cell)

        if handover_successful:
            # Process after successful handover
            if original_cell:
                original_cell.ConnectedUEs.remove(ue.ID)
            target_cell.ConnectedUEs.append(ue.ID)
            gnodeb.update_cell(target_cell)  # Assuming gNodeB has a method to update cell info

            # Logging the successful handover
            gnodeb_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
            cell_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
            ue_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")

            # Updating the database
            database_manager = DatabaseManager()
            database_manager.save_ue_state(ue)  # Assuming method to save UE state
            database_manager.save_cell_state(target_cell)  # Assuming method to save Cell state
        else:
            # Handling handover failure
            log_handover_failure("Handover execution failed", ue, original_cell, target_cell)
    else:
        # Handling feasibility check failure
        log_handover_failure("Handover feasibility check failed", ue, original_cell, target_cell)

        update_handover_counts(gnodeb, handover_successful)
        return handover_successful
###########################################################################################################################################
    def log_handover_failure(message, ue, original_cell, target_cell, rollback=False):
        gnodeb_logger.error(f"{message} for UE {ue.ID} from Cell {original_cell.ID} to Cell {target_cell.ID if target_cell else 'None'}.")
        cell_logger.error(f"{message} for UE {ue.ID} from Cell {original_cell.ID}.")
        ue_logger.error(f"{message} for UE {ue.ID}.")

        if rollback:
            rollback_successful = ue.perform_handover(original_cell)
            if rollback_successful:
                gnodeb_logger.info(f"UE {ue.ID} successfully rolled back to the original cell {original_cell.ID}.")
            else:
                gnodeb_logger.critical(f"Rollback failed for UE {ue.ID} to original cell {original_cell.ID}.")
###########################################################################################################################################
    def update_handover_counts(gnodeb, handover_successful):
        if handover_successful:
            gnodeb.handover_success_count += 1
        else:
            gnodeb.handover_failure_count += 1

##########################################################################################################################################

