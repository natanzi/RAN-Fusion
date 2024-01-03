import os
import time
from multiprocessing import Process, Queue
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
import logging
from logo import create_logo
from health_check.do_health_check import perform_health_check
from network.network_state import NetworkState
from network.handover_utils import handle_load_balancing, monitor_and_log_cell_load
from health_check.system_monitoring import SystemMonitor
from database.database_manager import DatabaseManager
from logs.logger_config import traffic_update
import threading
from traffic.traffic_generator import TrafficController
from multiprocessing import Lock

#update_received = False

#################################################################################################################################
# pickled by multiprocessing
def log_system_resources(system_monitor):
    while True:
        system_monitor.log_resource_usage()
        time.sleep(5)  # Log every 5 seconds

def network_state_manager(network_state, command_queue):
    while True:
        command = command_queue.get()  # Retrieve the command from the queue
        if command == 'save':
            network_state.save_state_to_influxdb()
        elif command == 'exit':  # Handle exit command to break the loop
            break
#####################################################################################################################################
def log_traffic(ues, command_queue, network_state):
    traffic_controller = TrafficController(command_queue)
    while True:
        for ue in ues:
            # Calculate throughput instead of generating traffic
            throughput_data = traffic_controller.calculate_and_write_ue_throughput(ue)

            # Extract the required values from the traffic_data dictionary
            # Assuming throughput calculation also provides delay, jitter, and packet_loss_rate
            delay = throughput_data['delay']
            jitter = throughput_data['jitter']
            packet_loss_rate = throughput_data['packet_loss_rate']
            formatted_throughput = f"{throughput_data['throughput']:.2f}"

            logging.info(
                f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Throughput: {formatted_throughput}Mbps, "
                f"Interval: {throughput['interval']}s, Delay: {delay}ms, Jitter: {jitter}ms, "
                f"Packet Loss Rate: {packet_loss_rate}%"
            )
        
        # Check for new commands and apply updates if necessary
        if not command_queue.empty():
            command = command_queue.get()
            if command['type'] == 'update':
                logging.info(f"Received update for {command['service_type']} traffic. Updating parameters. Update ID: {command['update_id']}")
                traffic_controller.update_parameters(command['data'])
                # Apply the update for matching UEs
                for ue in ues:
                    if ue.ServiceType.lower() == command['service_type'].lower():
                        # Assuming generate_updated_traffic now returns throughput and other parameters
                        updated_traffic = traffic_controller.generate_updated_traffic(ue)
                        logging.getLogger('traffic_update').info(
                            f"UE ID: {ue.ID} - Updated {ue.ServiceType} traffic with parameters: {command['data']} (Update ID: {command['update_id']})"
                        )
            elif command['type'] == 'save':
                network_state.save_state_to_influxdb()
            elif command['type'] == 'exit':
                break
        
        time.sleep(1)  # Sleep for a second before the next iteration
######################################################################################
def detect_and_handle_congestion(network_state, command_queue):
    while True:
        for cell_id, cell in network_state.cells.items():
            cell_load = network_state.get_cell_load(cell)
            if cell_load > 0.8:  # Assuming 0.8 is the congestion threshold
                # Call the load balancing function from handover_utils.py
                handle_load_balancing(cell.gNodeB_ID, network_state)
                command_queue.put('save')  # Save state after handling congestion
        time.sleep(5)  # Check for congestion at regular intervals
#####################################################################################
def main():
    logo_text = create_logo()
    print(logo_text)

    logging.basicConfig(level=logging.INFO)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)
    
    network_state_lock = Lock()
    network_state = NetworkState(network_state_lock)

    db_manager = DatabaseManager(network_state)

    if perform_health_check(network_state):
        print("Health check passed.")
    else:
        print("Health check failed.")
        return  # Exit if health check fails

    num_ues_to_launch = 10

    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config, db_manager)

    print(f"Number of UEs returned: {len(ues)}")
    time.sleep(2)

    #traffic_increase_config = {1: 2, 3: 1.5}

    command_queue = Queue()
    
    # Create an instance of TrafficController and pass the command_queue
    traffic_controller = TrafficController(command_queue)

    # Assuming traffic_controller is already created and available in this scope
    for gNodeB in gNodeBs.values():
        cell_load_thread = threading.Thread(target=monitor_and_log_cell_load, args=(gNodeB, traffic_controller))
        cell_load_thread.daemon = True  # This ensures the thread will exit when the main program does
        cell_load_thread.start()
    # Instantiate the SystemMonitor
    system_monitor = SystemMonitor(network_state)

    # Start the network state manager process
    logging_process = Process(target=log_traffic, args=(ues, command_queue, network_state))
    logging_process.start()

    # Start the cell monitor threads using monitor_and_log_cell_load
    for gNodeB in gNodeBs.values():
        cell_load_thread = threading.Thread(target=monitor_and_log_cell_load, args=(gNodeB, traffic_controller))
        cell_load_thread.daemon = True  # This ensures the thread will exit when the main program does
        cell_load_thread.start()

    # Start the congestion detection process
    congestion_process = Process(target=detect_and_handle_congestion, args=(network_state, command_queue))
    congestion_process.start()
    
    # Start the network state manager process
    ns_manager_process = Process(target=network_state_manager, args=(network_state, command_queue))
    ns_manager_process.start()

    # Start the system resource logging process with system_monitor passed as an argument
    system_resource_logging_process = Process(target=log_system_resources, args=(system_monitor,))
    system_resource_logging_process.start()

    # Wait for the processes to complete (if they ever complete)
    logging_process.join()
    congestion_process.join()
    system_resource_logging_process.join()

    # Signal the network state manager process to exit
    command_queue.put('exit')
    ns_manager_process.join()

if __name__ == "__main__":
    main()