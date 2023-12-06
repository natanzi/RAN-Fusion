# handover.py inside network folder to perform all handover processes.

def handover_decision(gnodeb, ue, find_available_cell, check_cell_capacity):
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