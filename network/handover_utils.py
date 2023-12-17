# handover_utils.py and it is inside the network folder
from datetime import datetime
import logging
from .cell import Cell
from .network_state import NetworkState
from traffic.network_metrics import calculate_cell_throughput  # If needed
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger
from database.database_manager import DatabaseManager  
from .handover import handover_decision
################################################Handover Execution#######################################################
def perform_handover(gnodeb, ue, target_cell, network_state):
    handover_successful = False
    current_cell_id = ue.ConnectedCellID
    original_cell = next((cell for cell in gnodeb.Cells if cell.ID == current_cell_id), None)

    if target_cell is None:
        target_cell = handover_decision(gnodeb, ue, gnodeb.Cells)

    if target_cell and check_handover_feasibility(network_state, target_cell.ID, ue):
        handover_successful = ue.perform_handover(target_cell)

        if handover_successful:
            if ue.ID not in original_cell.ConnectedUEs:
                if original_cell:
                    original_cell.ConnectedUEs.remove(ue.ID)
                target_cell.ConnectedUEs.append(ue.ID)
                network_state.update_state(gnodeb, target_cell, ue)

                gnodeb_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
                cell_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
                ue_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")

                database_manager = DatabaseManager()
                database_manager.set_network_state(network_state)
                database_manager.save_state_to_influxdb()
            else:
                log_handover_failure("Handover confirmation failed, UE still connected to the original cell", ue, original_cell, target_cell, rollback=True)
        else:
            log_handover_failure("Handover execution failed", ue, original_cell, target_cell, rollback=True)
    else:
        log_handover_failure("Handover feasibility check failed", ue, original_cell, target_cell)

    update_handover_counts(gnodeb, handover_successful, network_state)
    return handover_successful

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

def update_handover_counts(gnodeb, handover_successful, network_state):
    if handover_successful:
        gnodeb.handover_success_count += 1
        handle_load_balancing(gnodeb, network_state)
    else:
        gnodeb.handover_failure_count += 1
###########################################################################################################################################
def monitor_and_log_cell_load(gnodeb):
    cell_load_logger.info("Testing cell load logging.")
    for cell in gnodeb.Cells:
        # Use the gNodeB class method to calculate cell load
        cell_load_percentage = gnodeb.calculate_cell_load(cell) * 100  # Convert to percentage

        # Log the cell load percentage using cell_load_logger
        cell_load_logger.info(f'Cell {cell.ID} @ gNodeB {gnodeb.ID} - Load: {cell_load_percentage}%')

        # Check if the cell load exceeds the congestion threshold
        if cell_load_percentage > 80:  # Use the correct congestion threshold of 80%
            # Construct and log the congestion message
            congestion_message = f"gNodeB ID {gnodeb.ID} - Cell ID {cell.ID} is congested with a load of {cell_load_percentage}%."
            print(congestion_message)
            cell_logger.warning(congestion_message)
            gnodeb_logger.warning(congestion_message)  # Assuming gnodeb_logger is set up in logger_config.py
            
            # Trigger load balancing
            handle_load_balancing(gnodeb, gnodeb.calculate_cell_load, gnodeb.find_underloaded_cell, gnodeb.select_ues_for_load_balancing)
##########################################################################################################################################
def check_handover_feasibility(network_state, target_cell_id, ue):
    # Retrieve the target cell object using its ID
    target_cell = network_state.cells.get(target_cell_id)

    if target_cell is None:
        return False

    if len(target_cell.ConnectedUEs) >= target_cell.MaxConnectedUEs:
        return False

    # Assuming the function is_in_restricted_region is defined in the Cell class
    if target_cell.is_in_restricted_region():
        return False

    # Now using the method from the UE class
    if not ue.is_eligible_for_handover(network_state):
        return False

    return True
##########################################################################################################################################
def handle_load_balancing(gnodeb, network_state):
    for cell in gnodeb.Cells:
        cell_load = gnodeb.calculate_cell_load(cell)
        if cell_load > 0.8:  # Overloaded cell threshold
            underloaded_cell = gnodeb.find_underloaded_cell()
            if underloaded_cell:
                ues_to_move = gnodeb.select_ues_for_load_balancing(cell, underloaded_cell)
                for ue in ues_to_move:
                    perform_handover(gnodeb, ue, underloaded_cell, network_state)
                    cell_load = gnodeb.calculate_cell_load(cell)
                    if cell_load <= 0.8:
                        break
###########################################################################################################################################