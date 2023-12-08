## handover_utils.py and it is inside the network folder
from datetime import datetime
import logging
from .cell import Cell
from .network_state import NetworkState
from traffic.network_metrics import calculate_cell_throughput  # If needed
from log.logger_config import gnodeb_logger, cell_load_logger, cell_logger

###################################################Handover Decision Logic###################
def handle_load_balancing(gnodeb, calculate_cell_load, find_underloaded_cell, select_ues_for_load_balancing):
    for cell in gnodeb.Cells:
        if calculate_cell_load(cell) > 0.8:  # If cell load is over 80%
            underloaded_cell = find_underloaded_cell(gnodeb)
            if underloaded_cell:
                selected_ues = select_ues_for_load_balancing(cell)
                for ue in selected_ues:
                    perform_handover(gnodeb, ue, underloaded_cell)

def handle_qos_based_handover(gnodeb, all_ues, find_cell_by_id):
    for ue in all_ues(gnodeb):  # Assuming all_ues method returns all UEs in the gNodeB
        current_cell = find_cell_by_id(gnodeb, ue.ConnectedCellID)
        if current_cell and not current_cell.can_provide_gbr(ue):
            for cell in gnodeb.Cells:
                if cell != current_cell and cell.can_provide_gbr(ue):
                    perform_handover(gnodeb, ue, cell)
                    break
##################################################################################################
def handover_decision(gnodeb_instance, ue, cells):
    # Placeholder logic for deciding if a handover is needed
    from .gNodeB import gNodeB
    current_cell = next((cell for cell in gnodeb_instance.Cells if cell.ID == ue.ConnectedCellID), None)
    if current_cell and not current_cell.check_capacity():  # Assuming check_capacity is a method of Cell
        new_cell = gnodeb_instance.find_available_cell(ue)  # Correctly call the method on the gNodeB instance
        if new_cell:
            return new_cell
    return None
#####################################################################################################

#################################################Handover Execution###############################
def perform_handover(gnodeb, ue, target_cell=None):
    network_state = NetworkState()  # Assuming NetworkState is instantiated here or passed as an argument
    handover_successful = False  # Initialize the success flag
    current_cell_id = ue.ConnectedCellID  # Store the current cell ID for logging

    # If a target cell is not specified, decide on the new cell
    if target_cell is None:
        target_cell = handover_decision(gnodeb, ue, gnodeb.Cells)

    if target_cell:
        # Perform the handover to the target cell
        handover_successful = ue.perform_handover(target_cell)  # Assuming perform_handover is a method of UE

        if handover_successful:
            # Update the cell's connected UEs
            current_cell = next((cell for cell in gnodeb.Cells if cell.ID == current_cell_id), None)
            if current_cell:
                current_cell.ConnectedUEs.remove(ue.ID)  # Assuming ConnectedUEs holds UE IDs
            target_cell.ConnectedUEs.append(ue.ID)
            # Update the network state to reflect the handover
            network_state.update_state(gnodeb, target_cell, ue)  # Assuming update_state is a method of NetworkState

            # Log the successful handover
            gnodeb_logger.info(f"Handover successful for UE {ue.ID} from Cell {current_cell_id} to Cell {target_cell.ID}.")
        else:
            # Log the failed handover
            gnodeb_logger.error(f"Handover failed for UE {ue.ID} from Cell {current_cell_id}.")

    # Update handover success and failure counts
    if handover_successful:
        gnodeb.handover_success_count += 1
    else:
        gnodeb.handover_failure_count += 1
        # Log the failed handover if target cell was not found or handover was not successful
        gnodeb_logger.error(f"Handover failed for UE {ue.ID}. No suitable target cell found or handover was unsuccessful.")

    # Return the handover outcome
    return handover_successful
##################################################################################################################
def monitor_and_log_cell_load(gnodeb):
    for cell in gnodeb.Cells:
        # Use the gNodeB class method to calculate cell load
        cell_load_percentage = gnodeb.calculate_cell_load(cell) * 100  # Convert to percentage

        # Log the cell load percentage using cell_load_logger
        cell_load_logger.info(f'Cell load at time {datetime.now()}: {cell_load_percentage}% for Cell ID {cell.ID} in gNodeB ID {gnodeb.ID}')

        # Check if the cell load exceeds the congestion threshold
        if cell_load_percentage > 80:  # Assuming 80% is the congestion threshold
            # Construct and log the congestion message
            congestion_message = f"gNodeB ID {gnodeb.ID} - Cell ID {cell.ID} is congested with a load of {cell_load_percentage}%."
            print(congestion_message)
            cell_logger.warning(congestion_message)
            gnodeb_logger.warning(congestion_message)  # Assuming gnodeb_logger is set up in logger_config.py
            
            # Trigger load balancing
            handle_load_balancing(gnodeb, gnodeb.calculate_cell_load, gnodeb.find_underloaded_cell, gnodeb.select_ues_for_load_balancing)