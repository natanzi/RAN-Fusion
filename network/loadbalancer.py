# loadbalancer.py and it is inside the network folder
from datetime import datetime
import logging
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger
from database.database_manager import DatabaseManager
import time

class LoadBalancer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LoadBalancer, cls).__new__(cls)
            # Initialize any necessary attributes here
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def __init__(self):
        self.db_manager = DatabaseManager.get_instance()

    def handle_load_balancing(self, entity_type, entity_id):
        """
        Perform load balancing based on the type and ID of the overloaded entity.
        :param entity_type: Type of the entity ('gNodeB', 'cell', or 'sector')
        :param entity_id: ID of the overloaded entity
        """
        if entity_type == 'gNodeB':
            # Placeholder for gNodeB load balancing logic
            pass
        elif entity_type == 'cell':
            # Placeholder for cell load balancing logic
            pass
        elif entity_type == 'sector':

            self.balance_sector_load(entity_id)
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
    def balance_sector_load(self, sector_id):
        if not self.is_sector_overloaded(sector_id):
            return

        sorted_ues = self.get_sorted_ues_by_throughput(sector_id)
        target_sector = self.find_target_sector(sector_id)

        if not target_sector:
            # Log and handle the case where no suitable target sector is found
            return

        for ue in sorted_ues:
            if not self.move_ue_to_sector(ue, target_sector):
                # Log failure and potentially rollback
                break  # or continue based on your rollback strategy

        # Update database and in-memory state after successful load balancing
        self.update_database_and_memory(sector_id, target_sector, sorted_ues)

    def is_sector_overloaded(self, sector_id):
        # Implement logic to determine if a sector is overloaded
        sector_load = self.network_load_manager.calculate_sector_load(sector_id)
        return sector_load > 80  # Assuming 80% as the overload threshold

    def get_sorted_ues_by_throughput(self, sector_id):
        # Implement logic to sort UEs by throughput
        sector = self.network_load_manager.sector_manager.get_sector(sector_id)
        sorted_ues = sorted(sector.ues, key=lambda ue: ue.throughput, reverse=True)
        return sorted_ues

    def find_target_sector(self, sector_id):
        # Use NetworkLoadManager to find a less loaded neighboring sector
        sorted_neighbors = self.network_load_manager.get_sorted_entities_by_load(sector_id)
        if sorted_neighbors:
            return sorted_neighbors[0]  # Assuming the first one is the least loaded
        return None

    def move_ue_to_sector(self, ue, target_sector):
        # Implement logic to move a UE to a new sector
        # This should include handover logic and database updates
        return perform_handover(ue, target_sector)

    def update_database_and_memory(self, source_sector_id, target_sector_id, ues_moved):
        # Implement logic to update the database and in-memory state
        pass  # Placeholder for actual implementation

#####################################################################################################################
    def find_target_sector_within_cell(self, current_sector_id):
        """
        Attempt to find a less loaded sector within the same cell.
        """
        current_cell = self.network_load_manager.sector_manager.get_cell_by_sector_id(current_sector_id)
        if not current_cell:
            return None
        less_loaded_sector = min(
            (sector for sector in current_cell.sectors if sector.ID != current_sector_id),
            key=lambda x: x.calculate_sector_load(),
            default=None
        )
        if less_loaded_sector and less_loaded_sector.calculate_sector_load() < 80:  # Assuming 80% as the threshold
            return less_loaded_sector
        return None
#####################################################################################################################
    def find_target_sector_in_different_cell(self, current_sector_id):
        """
        Find a less loaded sector in a different cell.
        """
        all_cells = self.network_load_manager.get_all_cells()
        for cell in all_cells:
            for sector in cell.sectors:
                if sector.calculate_sector_load() < 80:  # Assuming 80% as the threshold
                    return sector
        return None
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
            log_handover_failure("Target cell not provided", ue, original_cell, target_cell, rollback=False)
            update_handover_counts(gnodeb, False)
            return False  # Optionally, handle this situation more gracefully

        # Check handover feasibility
        if check_handover_feasibility(target_cell, ue):
            handover_successful = ue.perform_handover(original_cell, target_cell, gnodeb.network_state)

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
                log_handover_failure("Handover execution failed", ue, original_cell, target_cell, rollback=True)
        else:
            # Handling feasibility check failure
            log_handover_failure("Handover feasibility check failed", ue, original_cell, target_cell, rollback=False)

        update_handover_counts(gnodeb, handover_successful)
        return handover_successful

    def log_handover_failure(message, ue, original_cell, target_cell, rollback=False):
        gnodeb_logger.error(f"{message} for UE {ue.ID} from Cell {original_cell.ID} to Cell {target_cell.ID if target_cell else 'None'}.")
        cell_logger.error(f"{message} for UE {ue.ID} from Cell {original_cell.ID}.")
        ue_logger.error(f"{message} for UE {ue.ID}.")
        if rollback:
            rollback_successful = ue.perform_handover(target_cell, original_cell, gnodeb.network_state)
            if rollback_successful:
                gnodeb_logger.info(f"UE {ue.ID} successfully rolled back to the original cell {original_cell.ID}.")
            else:
                gnodeb_logger.critical(f"Rollback failed for UE {ue.ID} to original cell {original_cell.ID}.")

    def update_handover_counts(gnodeb, handover_successful):
        if handover_successful:
            gnodeb.handover_success_count += 1
        else:
            gnodeb.handover_failure_count += 1