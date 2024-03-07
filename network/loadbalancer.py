#################################################################################################################
# loadbalancer.py and it is inside the network folder The LoadBalancer class is responsible for managing the    #
# load across sectors, cells, and gNodeBs within the network simulation. It aims to distribute the network load #
#evenly to prevent any single entity from becoming overloaded. This class follows the Singleton design pattern  #
# to ensure that only one instance of the LoadBalancer exists throughout the application lifecycle.             #
# Steps Recap:                                                                                                  #
#1 - Check if current source sector exceeds load threshold and Verify actual overload status                    # 
#2 - Get UEs connected to source sector and Sort by highest throughput users first (Prioritize heavy users)     # 
#3 - Find underloaded neighbor sectors and Filter sectors by % load                                             #
#4 - Handover UEs to underloaded neighbor sectors and For each UE:                                              #
#       - Attempt handover to neighbor targets                                                                  #
#       - If failure, try next target                                                                           #
#       - If all targets fail, revert UE                                                                        #
#5 - If no viable neighbor sectors:-Find least loaded neighbor cells                                            #
#6 - Choose best sector in underloaded cell- Identify best target sector                                        #
#7 - Handover UE to new cell target sector and Validate mobility successful                                     #
#8 - Rollback any unsuccessful handovers and Revert UE association if handover fails                            #
#9 - Update database for successful handovers and Ensure accurate view of network                               #
#10- Sync new UE to sector mapping and Keep in-memory mapping in sync                                           #
#                                                                                                               #
#   Note: In this version we do not support Cross-gNodeB Handovers!                                             #
#################################################################################################################
from datetime import datetime
import logging
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger, sector_logger
from database.database_manager import DatabaseManager
import time
from network.ue_manager import UEManager
from network.sector_manager import SectorManager
import threading

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

    def __init__(self, auto_balancing_enabled=True):
        self.db_manager = DatabaseManager.get_instance()
        self.handover_success_count = 0
        self.handover_failure_count = 0
        self.lock = threading.Lock()
        self.auto_balancing_enabled = auto_balancing_enabled  # Load balancing mode flag

    
    def update_handover_counts(self, handover_successful):
        with self.lock:
            if handover_successful:
                self.handover_success_count += 1
            else:
                self.handover_failure_count += 1
    
    def handle_load_balancing(self, entity_type, entity_id):
        """
        Perform load balancing based on the type and ID of the overloaded entity.
        :param entity_type: Type of the entity ('gNodeB', 'cell', or 'sector')
        :param entity_id: ID of the overloaded entity
        """
        if not self.auto_balancing_enabled:
            logging.info("Automatic load balancing is disabled. Manual intervention required.")
            return  # Exit the method if auto balancing is not enabled
        
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

###########################################################################################################################################
    def balance_sector_load(self, sector_id):
        if not self.is_sector_overloaded(sector_id):
            return
        sorted_ues = self.get_sorted_ues_by_throughput(sector_id)
        target_sector = self.find_target_sector(sector_id)
        if not target_sector:
            # Log the event
            sector_logger.warning(f"No suitable target sector found for sector {sector_id}.")
            # Consider alternative strategies or abort the operation
            return

        for ue in sorted_ues:
            if not self.move_ue_to_sector(ue.ID, target_sector.sector_id):  # Assuming UE object has ID attribute and target_sector is a Sector object
                # Log failure
                sector_logger.error(f"Failed to move UE {ue.ID} to target sector {target_sector.sector_id}. Initiating rollback.")
                # Rollback strategy: Attempt to move the UE back to its original sector or handle according to your rollback policy
                if self.rollback_ue_move(ue.ID, sector_id):  # Assuming rollback_ue_move is a method to handle rollback
                    sector_logger.info(f"Rollback successful for UE {ue.ID}.")
                else:
                    sector_logger.critical(f"Rollback failed for UE {ue.ID}. Immediate attention required.")
                break  # Exit the loop after handling the failure according to your strategy

        # Update database and in-memory state after successful load balancing
        self.update_database_and_memory(sector_id, target_sector.sector_id, sorted_ues)
###########################################################################################################################################
    def is_sector_overloaded(self, sector_id):
        # Existing logic to determine if a sector is overloaded
        sector_load = self.network_load_manager.calculate_sector_load(sector_id)
        return sector_load > 80  # Assuming 80% as the overload threshold

    def get_sorted_ues_by_throughput(self, sector_id):
        # Existing logic to sort UEs by throughput
        sector = self.network_load_manager.sector_manager.get_sector(sector_id)
        sorted_ues = sorted(sector.ues, key=lambda ue: ue.throughput, reverse=True)
        return sorted_ues
    
    def find_target_sector(self, sector_id):
        # Use NetworkLoadManager to find a less loaded neighboring sector
        sorted_neighbors = self.network_load_manager.get_sorted_entities_by_load(sector_id)
        if sorted_neighbors:
            return sorted_neighbors[0]  # Assuming the first one is the least loaded
        return None

    def move_ue_to_sector(self, ue_id, target_sector_id):
        ue = self.get_ue_by_id(ue_id)
        original_sector_id = ue.ConnectedCellID
        handover_successful = self.perform_handover(ue, target_sector_id)
    
        if not handover_successful:
            sector_logger.error(f"Handover failed for UE {ue_id} to target sector {target_sector_id}. Attempting rollback.")
            self.rollback_ue_move(ue_id, original_sector_id)

    # Assuming we have access to a method to get the gNodeB and original sector (cell) of the UE
        gnodeb = self.get_gnodeb_for_ue(ue_id)
        original_sector = self.get_sector_for_ue(ue_id)

    # Attempt the handover to the target sector
        target_cell = self.get_cell_by_sector_id(target_sector_id)  # Assuming a method to get the cell by sector ID
        handover_successful = self.perform_handover(gnodeb, ue, target_cell)

        if handover_successful:
            print(f"Handover successful for UE {ue_id} to sector {target_sector_id}.")
            # Update the UE's sector in the database and in-memory state
            self.update_ue_sector_in_db_and_memory(ue_id, target_sector_id)
            return True
        else:
            print(f"Handover failed for UE {ue_id}. Attempting rollback to original sector {original_sector.ID}.")
            # Attempt rollback to the original sector
            rollback_successful = self.perform_handover(gnodeb, ue, original_sector)
            if rollback_successful:
                print(f"Rollback successful for UE {ue_id} to original sector {original_sector.ID}.")
            else:
                print(f"Critical: Rollback failed for UE {ue_id}. Immediate attention required.")
            return False

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
            ue_logger.warning("Target cell not provided", ue, original_cell, target_cell, rollback=False)
            update_handover_counts(gnodeb, False)  # Update handover failure count
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

        update_handover_counts(gnodeb, handover_successful)  # Update handover counts based on success or failure
        return handover_successful
###########################################################################################################################################           
    def update_database_and_memory(self, source_sector_id, target_sector_id, ues_moved):
    # Pseudo-code to update the database and in-memory state
        pass  # Placeholder for actual implementation
###########################################################################################################################################
    def rollback_ue_move(self, ue_id, original_sector_id):
        try:
            ue = self.get_ue_by_id(ue_id)
            original_sector = self.get_sector_by_id(original_sector_id)
            rollback_successful = self.perform_handover(ue, original_sector)
            if rollback_successful:
                sector_logger.info(f"Rollback successful for UE {ue_id} to sector {original_sector_id}.")
            else:
                sector_logger.critical(f"Rollback attempt failed for UE {ue_id} to sector {original_sector_id}.")
        except Exception as e:
            sector_logger.critical(f"Exception during rollback for UE {ue_id}: {str(e)}")
###########################################################################################################################################            
    def update_state_after_rollback(self, ue_id, original_sector_id):
        # Update the database
        self.db_manager.update_ue_sector(ue_id, original_sector_id)
        # Update in-memory state
        ue = self.get_ue_by_id(ue_id)
        ue.ConnectedCellID = original_sector_id
        sector_logger.info(f"State updated for UE {ue_id} after rollback to sector {original_sector_id}.")