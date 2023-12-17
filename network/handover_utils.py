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
    # Removed the instantiation of NetworkState, use the passed instance instead
    handover_successful = False  # Initialize the success flag
    current_cell_id = ue.ConnectedCellID  # Store the current cell ID for logging
    original_cell = next((cell for cell in gnodeb.Cells if cell.ID == current_cell_id), None)

    # If a target cell is not specified, decide on the new cell
    if target_cell is None:
        target_cell = handover_decision(gnodeb, ue, gnodeb.Cells)

    # Check handover feasibility before performing handover
    if target_cell and check_handover_feasibility(network_state, target_cell.ID):
        # Perform the handover to the target cell
        handover_successful = ue.perform_handover(target_cell)  # Assuming perform_handover is a method of UE

        if handover_successful:
            # Confirm UE is no longer connected to the previous cell
            if ue.ID not in original_cell.ConnectedUEs:
                # Update the cell's connected UEs
                if original_cell:
                    original_cell.ConnectedUEs.remove(ue.ID)  # Assuming ConnectedUEs holds UE IDs
                target_cell.ConnectedUEs.append(ue.ID)
                # Update the network state to reflect the handover
                network_state.update_state(gnodeb, target_cell, ue)  # Assuming update_state is a method of NetworkState

                # Log the successful handover
                gnodeb_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
                cell_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
                ue_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")

                # Update the database with the new network state
                database_manager = DatabaseManager()
                database_manager.set_network_state(network_state)
                database_manager.save_state_to_influxdb()

            else:
                # Handover confirmation failed, UE is still connected to the original cell
                handover_successful = False
                # Rollback to the original cell
                rollback_successful = ue.perform_handover(original_cell)
                if rollback_successful:
                    gnodeb_logger.error(f"Handover confirmation failed for UE {ue.ID}. Rolled back to Cell {original_cell.ID}.")
                    cell_logger.error(f"Handover confirmation failed for UE {ue.ID}. Rolled back to Cell {original_cell.ID}.")
                    ue_logger.error(f"Handover confirmation failed for UE {ue.ID}. Rolled back to Cell {original_cell.ID}.")
                else:
                    gnodeb_logger.critical(f"Rollback failed for UE {ue.ID}.")
                    cell_logger.critical(f"Rollback failed for UE {ue.ID}.")
                    ue_logger.critical(f"Rollback failed for UE {ue.ID}.")
        else:
            # Log the failed handover
            gnodeb_logger.error(f"Handover failed for UE {ue.ID} from Cell {current_cell_id}.")
            cell_logger.error(f"Handover failed for UE {ue.ID} from Cell {current_cell_id}.")
            ue_logger.error(f"Handover failed for UE {ue.ID} from Cell {current_cell_id}.")
            # Rollback to the original cell
            ue.perform_handover(original_cell)

    # Update handover success and failure counts
    if handover_successful:
        gnodeb.handover_success_count += 1
        # After a successful handover, reassess the load distribution
        handle_load_balancing(gnodeb.ID, network_state)  # Pass gnodeb.ID and network_state

    else:
        gnodeb.handover_failure_count += 1
        # Log the failed handover if target cell was not found or handover was not successful
        gnodeb_logger.error(f"Handover failed for UE {ue.ID}. No suitable target cell found or handover was unsuccessful.")

    # Return the handover outcome
    return handover_successful
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
def check_handover_feasibility(network_state, target_cell_id):
    # Get the target cell object using its ID
    target_cell = network_state.cells.get(target_cell_id)

    if target_cell is None:
        raise ValueError(f"Target cell with ID {target_cell_id} does not exist.")

    # Check if the target cell can accept more UEs based on its load
    return len(target_cell.ConnectedUEs) < target_cell.MaxConnectedUEs