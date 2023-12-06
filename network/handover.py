# handover.py inside network folder to perform all handover processes.
from network.cell import Cell
from network.network_state import NetworkState
from traffic.network_metrics import calculate_cell_throughput, calculate_cell_load
import logging

def handover_decision(gnodeb_instance, ue, target_cell):
    # Placeholder logic for deciding if a handover is needed
    current_cell = next((cell for cell in gnodeb.Cells if cell.ID == ue.ConnectedCellID), None)
    if current_cell and not check_cell_capacity(current_cell):
        new_cell = find_available_cell(gnodeb)
        if new_cell:
            return new_cell
    return None

def perform_handover(gnodeb, ue, network_state, target_cell=None):
    handover_successful = False  # Initialize the success flag

    # If a target cell is not specified, decide on the new cell
    if target_cell is None:
        target_cell = handover_decision(gnodeb, ue, gnodeb.find_available_cell, gnodeb.check_cell_capacity)

    if target_cell:
        # Perform the handover to the target cell
        handover_successful = ue.perform_handover(target_cell)

        if handover_successful:
            # Update the cell's connected UEs
            current_cell = next((cell for cell in gnodeb.Cells if cell.ID == ue.ConnectedCellID), None)
            if current_cell:
                current_cell.ConnectedUEs.remove(ue)
            target_cell.ConnectedUEs.append(ue)
            # Update the network state to reflect the handover
            network_state.update_state(gnodeb, target_cell, ue)

    # Update handover success and failure counts
    if handover_successful:
        gnodeb.handover_success_count += 1
    else:
        gnodeb.handover_failure_count += 1

    # Return the handover outcome
    return handover_successful

def monitor_and_log_cell_load(gnodeb, calculate_cell_load, logging):
    for cell in gnodeb.Cells:
        cell_load_percentage = calculate_cell_load(cell)

        # Log the cell load percentage
        logging.info(f'Cell {cell.ID} Load: {cell_load_percentage}%')

        # Check if the cell load exceeds the congestion threshold
        if cell_load_percentage > 80:  # Assuming 80% is the congestion threshold
            # Print and log the congestion message
            congestion_message = f"Cell {cell.ID} is congested with a load of {cell_load_percentage}%."
            print(congestion_message)
            logging.warning(congestion_message)
            # Trigger load balancing
            handle_load_balancing(gnodeb, calculate_cell_load, gnodeb.find_underloaded_cell, gnodeb.select_ues_for_load_balancing)