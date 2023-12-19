import os
import time
from multiprocessing import Process, Queue
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
import logging
from logo import create_logo
from health_check.do_health_check import perform_health_check
from network.network_state import NetworkState
from network.handover_utils import handle_load_balancing
from health_check.system_monitoring import SystemMonitor
from database.database_manager import DatabaseManager
from logs.logger_config import traffic_update

# pickled by multiprocessing
def log_system_resources(system_monitor):
    while True:
        system_monitor.log_resource_usage()
        time.sleep(60)  # Log every 60 seconds

def network_state_manager(network_state, command_queue):
    while True:
        command = command_queue.get()  # Retrieve the command from the queue
        if command == 'save':
            network_state.save_state_to_influxdb()
        elif command == 'exit':  # Handle exit command to break the loop
            break

def log_traffic(ues, command_queue, traffic_increase_config=None):
    while True:
        for ue in ues:
            # Call the generate_traffic method and get the traffic details
            traffic_details = ue.generate_traffic()
            
            # Log the traffic details in the desired format
            logging.info(f"u{ue.ID}, {ue.IMEI}, {ue.ServiceType}, {traffic_details['data_size']}MB, {traffic_details['interval']}s")
            
            # Save the state to the database
            command_queue.put('save')
        time.sleep(1)

def monitor_cell_load(gNodeBs, command_queue):
    while True:
        for gNodeB_id, gNodeB_instance in gNodeBs.items():
            # ... existing cell monitoring logic ...
            command_queue.put('save')
        time.sleep(5)  # Adjust the sleep time as needed for your simulation

def detect_and_handle_congestion(network_state, command_queue):
    while True:
        for cell_id, cell in network_state.cells.items():
            cell_load = network_state.get_cell_load(cell)
            if cell_load > 0.8:  # Assuming 0.8 is the congestion threshold
                # Call the load balancing function from handover_utils.py
                handle_load_balancing(cell.gNodeB_ID, network_state)
                command_queue.put('save')  # Save state after handling congestion
        time.sleep(5)  # Check for congestion at regular intervals

def main():
    logo_text = create_logo()
    print("Printing logo start")
    print(logo_text)
    print("Printing logo end")

    logging.basicConfig(level=logging.INFO)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    network_state = NetworkState()

    db_manager = DatabaseManager(network_state)

    if perform_health_check(network_state):
        print("Health check passed.")
    else:
        print("Health check failed.")
        return  # Exit if health check fails

    num_ues_to_launch = 40

    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config, db_manager)

    print(f"Number of UEs returned: {len(ues)}")
    time.sleep(2)

    traffic_increase_config = {1: 2, 3: 1.5}

    command_queue = Queue()

    # Instantiate the SystemMonitor
    system_monitor = SystemMonitor(network_state)

    # Start the network state manager process
    ns_manager_process = Process(target=network_state_manager, args=(network_state, command_queue))
    ns_manager_process.start()

    # Start the traffic logging process
    logging_process = Process(target=log_traffic, args=(ues, command_queue, traffic_increase_config))
    logging_process.start()

    # Start the cell monitor process
    cell_monitor_process = Process(target=monitor_cell_load, args=(gNodeBs, command_queue))
    cell_monitor_process.start()

    # Start the congestion detection process
    congestion_process = Process(target=detect_and_handle_congestion, args=(network_state, command_queue))
    congestion_process.start()

    # Start the system resource logging process with system_monitor passed as an argument
    system_resource_logging_process = Process(target=log_system_resources, args=(system_monitor,))
    system_resource_logging_process.start()

    # Wait for the processes to complete (if they ever complete)
    logging_process.join()
    cell_monitor_process.join()
    congestion_process.join()
    system_resource_logging_process.join()

    # Signal the network state manager process to exit
    command_queue.put('exit')
    ns_manager_process.join()

if __name__ == "__main__":
    main()