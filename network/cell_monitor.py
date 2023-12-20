#cell_monitor.py is located in network
import logging
from network.handover_utils import handle_load_balancing
import time
from logs.logger_config import cell_load_logger

# Define a threshold for when to consider a cell overloaded
CELL_LOAD_THRESHOLD = 0.8  # This is an example value; adjust as needed

def monitor_cell_load(network_state, gNodeBs, command_queue):
    while True:
        for gNodeB_id, gNodeB_instance in gNodeBs.items():
            for cell in gNodeB_instance.cells:
                cell_load = network_state.get_cell_load(cell)
                # Log the cell load here using the cell_load_logger
                cell_load_logger.info(f"gNodeB ID: {gNodeB_id}, Cell ID: {cell.ID}, Cell Load: {cell_load}")
                # Check if the cell load exceeds the threshold and handle it if necessary
                if cell_load > CELL_LOAD_THRESHOLD:
                    handle_load_balancing(gNodeB_instance, network_state)
                command_queue.put('save')
        time.sleep(5)  # Adjust the sleep time as needed for your simulation