# handover_utils.py and it is inside the network folder
from datetime import datetime
import logging
from .cell import Cell
from .network_state import NetworkState
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger
from database.database_manager import DatabaseManager
import time

################################################Handover Execution#######################################################
def perform_handover(gnodeb, ue, target_cell, network_state):
    handover_successful = False
    current_cell_id = ue.ConnectedCellID
    original_cell = next((cell for cell in gnodeb.Cells if cell.ID == current_cell_id), None)

    # Ensure target_cell is provided
    if not target_cell:
        return False  # Optionally, handle this situation more gracefully

    if check_handover_feasibility(network_state, target_cell.ID, ue):
        handover_successful = ue.perform_handover(target_cell)

        if handover_successful:
            # Process after successful handover
            if original_cell:
                original_cell.ConnectedUEs.remove(ue.ID)
            target_cell.ConnectedUEs.append(ue.ID)
            network_state.update_state(gnodeb, target_cell, ue)

            # Logging the successful handover
            gnodeb_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
            cell_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
            ue_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")

            # Updating the database
            database_manager = DatabaseManager()
            database_manager.set_network_state(network_state)
            database_manager.save_state_to_influxdb()
        else:
            # Handling handover failure
            log_handover_failure("Handover execution failed", ue, original_cell, target_cell)
    else:
        # Handling feasibility check failure
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
        # Assuming handle_load_balancing is defined elsewhere and is relevant here
        handle_load_balancing(gnodeb, network_state)
    else:
        gnodeb.handover_failure_count += 1
###########################################################################################################################################
def monitor_and_log_cell_load(gnodeb):
    while True: 
        
        for cell in gnodeb.Cells:
            # Assume cell_load is a pre-calculated property or method in the Cell class
            cell_load_percentage = cell.load 

            # Log the cell load percentage using cell_load_logger
            cell_load_logger.info(f'Cell {cell.ID} @ gNodeB {gnodeb.ID} - Load: {cell_load_percentage}%')

            # Check if the cell load exceeds the congestion threshold
            if cell_load_percentage > 80:  # Use the correct congestion threshold of 80%
                # Construct and log the congestion message
                congestion_message = f"gNodeB ID {gnodeb.ID} - Cell ID {cell.ID} is congested with a load of {cell_load_percentage}%."
                print(congestion_message)
                cell_logger.warning(congestion_message)
                gnodeb_logger.warning(congestion_message)
                
                # Trigger load balancing
                handle_load_balancing(gnodeb, gnodeb.calculate_cell_load, gnodeb.find_underloaded_cell, gnodeb.select_ues_for_load_balancing)
        
        time.sleep(1)  # Sleep for one second before the next iteration
##########################################################################################################################################
def check_handover_feasibility(network_state, target_cell_id, ue):
    # Retrieve the target cell object using its ID
    target_cell = network_state.cells.get(target_cell_id)

    if target_cell is None:
        return False

    if len(target_cell.ConnectedUEs) >= target_cell.MaxConnectedUEs:
        return False

    if target_cell.is_in_restricted_region():
        return False

    if not ue.is_eligible_for_handover(network_state):
        return False

    # Retrieve the gNodeB object that the target cell belongs to
    target_gnodeb = network_state.gnodebs.get(target_cell.gNodeB_ID)
    if target_gnodeb is None:
        return False

    # Check the load of the gNodeB
    gnodeb_load = target_gnodeb.calculate_gnodeb_load()
    if gnodeb_load > 90:  # Define some_threshold as the maximum acceptable load
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