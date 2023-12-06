#handover.py inside network folder to perform all handover procerss.
def handover_decision(self, ue):
        # Placeholder logic for deciding if a handover is needed
        current_cell = next((cell for cell in self.Cells if cell.ID == ue.ConnectedCellID), None)
        if current_cell and not self.check_cell_capacity(current_cell):
            new_cell = self.find_available_cell()
            if new_cell:
                return new_cell
        return None

def perform_handover(self, ue, target_cell=None):
        handover_successful = False  # Initialize the success flag

        # If a target cell is not specified, decide on the new cell
        if target_cell is None:
            target_cell = self.handover_decision(ue)

        if target_cell:
            # Perform the handover to the target cell
            handover_successful = ue.perform_handover(target_cell.ID)

            if handover_successful:
                # Update the cell's connected UEs
                current_cell = next((cell for cell in self.Cells if cell.ID == ue.ConnectedCellID), None)
                if current_cell:
                    current_cell.ConnectedUEs.remove(ue.ID)
                target_cell.ConnectedUEs.append(ue.ID)
                # Update the network state to reflect the handover
                network_state.update_state(self, target_cell, ue)

        # Update handover success and failure counts
        if handover_successful:
            self.handover_success_count += 1
        else:
            self.handover_failure_count += 1

        # Return the handover outcome
        return handover_successful
def handle_load_balancing(self):
        for cell in self.Cells:
            if self.calculate_cell_load(cell) > 0.8:  # If cell load is over 80%
                underloaded_cell = self.find_underloaded_cell()
                if underloaded_cell:
                    selected_ues = self.select_ues_for_load_balancing(cell)
                    for ue in selected_ues:
                        self.perform_handover(ue, underloaded_cell)

def handle_qos_based_handover(self):
        for ue in self.all_ues():  # Assuming all_ues method returns all UEs in the gNodeB
            current_cell = self.find_cell_by_id(ue.ConnectedCellID)
            if current_cell and not current_cell.can_provide_gbr(ue):
                for cell in self.Cells:
                    if cell != current_cell and cell.can_provide_gbr(ue):
                        self.perform_handover(ue, cell)
                        break

def monitor_and_log_cell_load(self):
        while True:
            for cell in self.Cells:
                cell_load_percentage = calculate_cell_load(cell.ID, [self])
            
                # Log the cell load percentage
                logging.info(f'Cell {cell.ID} Load: {cell_load_percentage}%')

                # Check if the cell load exceeds the congestion threshold
                if cell_load_percentage > 80:  # Assuming 80% is the congestion threshold
                    # Print and log the congestion message
                    congestion_message = f"Cell {cell.ID} is congested with a load of {cell_load_percentage}%."
                    print(congestion_message)
                    logging.warning(congestion_message)
                    # Trigger load balancing
                    self.handle_load_balancing()

            time.sleep(20)  # Wait for 20 seconds before the next check